from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Avg
from .models import (
    Product, Cart, CartItem, Order, OrderItem,
    Category, Review, Wishlist, UserActivity
)
from .serializers import (
    UserSerializer, ProductSerializer, ProductDetailSerializer,
    CartSerializer, CartItemSerializer, OrderSerializer,
    UserPreferencesSerializer, CategorySerializer, ReviewSerializer,
    WishlistSerializer, UserActivitySerializer
)
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ValidationError
from rest_framework.exceptions import NotFound
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from .payments import FlutterwavePayment
from .reports import SalesReport
import jwt
import datetime

User = get_user_model()

def format_response(data=None, message=None, status_code=status.HTTP_200_OK):
    response_data = {}
    if data is not None:
        response_data['data'] = data
    if message is not None:
        response_data['message'] = message
    return Response(response_data, status=status_code)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'name']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Track product view
        if request.user.is_authenticated:
            UserActivity.objects.create(
                user=request.user,
                activity_type='view',
                product=instance
            )
            instance.views_count += 1
            instance.save()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def get_queryset(self):
        queryset = Product.objects.all()
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
            
        # Filter by stock availability
        in_stock = self.request.query_params.get('in_stock')
        if in_stock == 'true':
            queryset = queryset.filter(stock__gt=0)
            
        # Filter by category
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        # Filter by rating
        min_rating = self.request.query_params.get('min_rating')
        if min_rating:
            queryset = queryset.annotate(avg_rating=Avg('reviews__rating')).filter(avg_rating__gte=min_rating)
            
        return queryset

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    
    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart
    
    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        cart = self.get_object()
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
            
        if product.stock < quantity:
            return Response({'error': 'Not enough stock'}, status=status.HTTP_400_BAD_REQUEST)
            
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
            
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def remove_item(self, request, pk=None):
        cart = self.get_object()
        item_id = request.data.get('item_id')
        
        try:
            item = CartItem.objects.get(id=item_id, cart=cart)
            item.delete()
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        cart = self.get_object()
        shipping_address = request.data.get('shipping_address')
        
        if not shipping_address:
            return Response({'error': 'Shipping address is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
            
        # Create order
        order = Order.objects.create(
            user=request.user,
            total_amount=cart.total,
            shipping_address=shipping_address
        )
        
        # Create order items
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            
            # Update product stock
            item.product.stock -= item.quantity
            item.product.save()
            
        # Clear cart
        cart.items.all().delete()
        
        serializer = OrderSerializer(order)
        return Response(serializer.data)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        
        if order.status != 'pending':
            return Response({'error': 'Only pending orders can be cancelled'}, 
                          status=status.HTTP_400_BAD_REQUEST)
            
        order.status = 'cancelled'
        order.save()
        
        # Restore product stock
        for item in order.items.all():
            item.product.stock += item.quantity
            item.product.save()
            
        serializer = OrderSerializer(order)
        return Response(serializer.data)

class UserPreferencesViewSet(viewsets.ModelViewSet):
    serializer_class = UserPreferencesSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        preferences = request.data.get('preferences', {})
        
        # Merge new preferences with existing ones
        user.preferences.update(preferences)
        user.save()
        
        serializer = self.get_serializer(user)
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    try:
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return format_response(
                data={
                    'user': UserSerializer(user).data,
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                },
                message='User created successfully',
                status_code=status.HTTP_201_CREATED
            )
        return format_response(
            data={'errors': serializer.errors},
            message='Validation failed',
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except ValidationError as e:
        return format_response(
            data={'errors': str(e)},
            message='Validation error',
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return format_response(
            data={'error': str(e)},
            message='An unexpected error occurred',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    try:
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
            return format_response(
                message='Please provide both email and password',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        user = User.objects.get(email=email)
        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return format_response(
                data={
                    'user': UserSerializer(user).data,
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                },
                message='Login successful'
            )
        
        return format_response(
            message='Invalid credentials',
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    except User.DoesNotExist:
        return format_response(
            message='Invalid credentials',
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as e:
        return format_response(
            message='An unexpected error occurred',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    try:
        serializer = UserSerializer(request.user)
        return format_response(data=serializer.data)
    except Exception as e:
        return format_response(
            message='An unexpected error occurred',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def product_list(request):
    try:
        if request.method == 'GET':
            products = Product.objects.all()
            serializer = ProductSerializer(products, many=True)
            return format_response(data=serializer.data)
        
        elif request.method == 'POST':
            serializer = ProductSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return format_response(
                    data=serializer.data,
                    message='Product created successfully',
                    status_code=status.HTTP_201_CREATED
                )
            return format_response(
                data={'errors': serializer.errors},
                message='Validation failed',
                status_code=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        return format_response(
            message='An unexpected error occurred',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def product_detail(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        raise NotFound('Product not found')

    try:
        if request.method == 'GET':
            serializer = ProductSerializer(product)
            return format_response(data=serializer.data)

        elif request.method == 'PUT':
            serializer = ProductSerializer(product, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return format_response(
                    data=serializer.data,
                    message='Product updated successfully'
                )
            return format_response(
                data={'errors': serializer.errors},
                message='Validation failed',
                status_code=status.HTTP_400_BAD_REQUEST
            )

        elif request.method == 'DELETE':
            product.delete()
            return format_response(
                message='Product deleted successfully',
                status_code=status.HTTP_204_NO_CONTENT
            )
    except Exception as e:
        return format_response(
            message='An unexpected error occurred',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Category.objects.all()
        parent_id = self.request.query_params.get('parent')
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        return queryset

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])
    
    def perform_create(self, serializer):
        product = Product.objects.get(id=self.kwargs['product_pk'])
        serializer.save(user=self.request.user, product=product)
        
        # Track activity
        UserActivity.objects.create(
            user=self.request.user,
            activity_type='review',
            product=product,
            details={'rating': serializer.validated_data['rating']}
        )

class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        wishlist, created = Wishlist.objects.get_or_create(user=self.request.user)
        return wishlist
    
    @action(detail=True, methods=['post'])
    def add_product(self, request, pk=None):
        wishlist = self.get_object()
        product_id = request.data.get('product_id')
        
        try:
            product = Product.objects.get(id=product_id)
            wishlist.products.add(product)
            
            # Track activity
            UserActivity.objects.create(
                user=self.request.user,
                activity_type='wishlist_add',
                product=product
            )
            
            serializer = self.get_serializer(wishlist)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def remove_product(self, request, pk=None):
        wishlist = self.get_object()
        product_id = request.data.get('product_id')
        
        try:
            product = Product.objects.get(id=product_id)
            wishlist.products.remove(product)
            
            # Track activity
            UserActivity.objects.create(
                user=self.request.user,
                activity_type='wishlist_remove',
                product=product
            )
            
            serializer = self.get_serializer(wishlist)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserActivitySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserActivity.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        # Get user's activity statistics
        activities = UserActivity.objects.filter(user=request.user)
        
        stats = {
            'total_views': activities.filter(activity_type='view').count(),
            'total_searches': activities.filter(activity_type='search').count(),
            'total_purchases': activities.filter(activity_type='purchase').count(),
            'total_reviews': activities.filter(activity_type='review').count(),
            'recent_activities': self.get_serializer(activities.order_by('-created_at')[:10], many=True).data
        }
        
        return Response(stats)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def verify_email(self, request):
        """Send email verification link"""
        user = request.user
        if user.is_verified:
            return Response({'message': 'Email already verified'})
        
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, settings.SECRET_KEY, algorithm='HS256')
        
        verification_url = f"{settings.FRONTEND_URL}/verify-email/{token}"
        html_message = render_to_string('email/verification.html', {
            'verification_url': verification_url
        })
        
        send_mail(
            'Verify your email',
            'Please verify your email',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message
        )
        
        return Response({'message': 'Verification email sent'})

    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        """Send password reset link"""
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=404)
        
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, settings.SECRET_KEY, algorithm='HS256')
        
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{token}"
        html_message = render_to_string('email/password_reset.html', {
            'reset_url': reset_url
        })
        
        send_mail(
            'Reset your password',
            'Please reset your password',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message
        )
        
        return Response({'message': 'Password reset email sent'})

class PaymentViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.payment = FlutterwavePayment()
    
    @action(detail=False, methods=['post'])
    def initialize(self, request):
        """Initialize a payment transaction"""
        try:
            payment = self.payment.initialize_payment(
                user=request.user,
                amount=request.data.get('amount'),
                currency=request.data.get('currency', 'USD'),
                payment_type=request.data.get('payment_type', 'card')
            )
            return Response(payment)
        except Exception as e:
            return Response({'error': str(e)}, status=400)
    
    @action(detail=True, methods=['get'])
    def verify(self, request, pk=None):
        """Verify a payment transaction"""
        try:
            verification = self.payment.verify_payment(pk)
            return Response(verification)
        except Exception as e:
            return Response({'error': str(e)}, status=400)
    
    @action(detail=True, methods=['get'])
    def get_transaction(self, request, pk=None):
        """Get transaction details"""
        try:
            transaction = self.payment.get_transaction(pk)
            return Response(transaction)
        except Exception as e:
            return Response({'error': str(e)}, status=400)
    
    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """Refund a transaction"""
        try:
            refund = self.payment.refund_transaction(
                pk,
                amount=request.data.get('amount')
            )
            return Response(refund)
        except Exception as e:
            return Response({'error': str(e)}, status=400)
    
    @action(detail=False, methods=['get'])
    def list_transactions(self, request):
        """List transactions with optional filters"""
        try:
            transactions = self.payment.get_transactions(**request.query_params.dict())
            return Response(transactions)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

class ReportViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=False, methods=['get'])
    def daily_sales(self, request):
        """Get daily sales report"""
        days = int(request.query_params.get('days', 30))
        return Response(SalesReport.get_daily_sales(days))
    
    @action(detail=False, methods=['get'])
    def monthly_sales(self, request):
        """Get monthly sales report"""
        months = int(request.query_params.get('months', 12))
        return Response(SalesReport.get_monthly_sales(months))
    
    @action(detail=False, methods=['get'])
    def product_sales(self, request):
        """Get product sales report"""
        return Response(SalesReport.get_product_sales())
    
    @action(detail=False, methods=['get'])
    def category_sales(self, request):
        """Get category sales report"""
        return Response(SalesReport.get_category_sales())
    
    @action(detail=False, methods=['get'])
    def customer_metrics(self, request):
        """Get customer metrics"""
        return Response(SalesReport.get_customer_metrics())
    
    @action(detail=False, methods=['get'])
    def inventory_metrics(self, request):
        """Get inventory metrics"""
        return Response(SalesReport.get_inventory_metrics())
    
    @action(detail=False, methods=['get'])
    def comprehensive(self, request):
        """Get comprehensive report"""
        return Response(SalesReport.get_comprehensive_report()) 