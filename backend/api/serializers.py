from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import (
    Product, Cart, CartItem, Order, OrderItem,
    Category, Review, Wishlist, UserActivity
)

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    name = serializers.CharField(required=True)
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    username = serializers.CharField(read_only=True)
    preferences = serializers.JSONField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'name', 'phone', 'address', 'username', 'preferences')
        extra_kwargs = {
            'email': {'required': True},
            'name': {'required': True},
            'phone': {'required': False},
            'address': {'required': False},
        }
        read_only_fields = ('id', 'username', 'preferences')

    def create(self, validated_data):
        # Generate a unique username from email
        email = validated_data['email']
        username = email.split('@')[0]  # Use part before @ as username
        validated_data['username'] = username
        
        user = User.objects.create_user(**validated_data)
        return user

class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('preferences',)

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_id', 'quantity', 'subtotal')

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total', 'created_at', 'updated_at')

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'quantity', 'price', 'subtotal')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'status', 'total_amount', 'shipping_address', 
                 'items', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'total_amount', 'created_at', 'updated_at')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = ('id', 'user', 'product', 'rating', 'comment', 'created_at', 'updated_at')
        read_only_fields = ('user', 'created_at', 'updated_at')

class ProductDetailSerializer(ProductSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    
    class Meta(ProductSerializer.Meta):
        fields = list(ProductSerializer.Meta.fields) + ['category', 'reviews', 'average_rating', 'views_count']

class WishlistSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    
    class Meta:
        model = Wishlist
        fields = ('id', 'products', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

class UserActivitySerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = UserActivity
        fields = ('id', 'activity_type', 'product', 'details', 'created_at')
        read_only_fields = ('created_at',) 