from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .webhooks import PrivacyWebhookView
from .routes import cards
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from .views import (
    ProductViewSet, CategoryViewSet, OrderViewSet,
    ReviewViewSet, WishlistViewSet, UserActivityViewSet,
    UserViewSet, PaymentViewSet, ReportViewSet
)

schema_view = get_schema_view(
    openapi.Info(
        title="E-commerce API",
        default_version='v1',
        description="API documentation for the E-commerce platform",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Create the main router
router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'wishlists', WishlistViewSet, basename='wishlist')
router.register(r'activities', UserActivityViewSet, basename='activity')
router.register(r'users', UserViewSet, basename='user')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'reports', ReportViewSet, basename='report')

# Create a nested router for product reviews
products_router = routers.NestedDefaultRouter(router, r'products', lookup='product')
products_router.register(r'reviews', views.ReviewViewSet, basename='product-reviews')

urlpatterns = [
    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Include all routers
    path('', include(router.urls)),
    path('', include(products_router.urls)),
    
    # Authentication endpoints
    path('auth/login/', views.login, name='login'),
    path('auth/register/', views.signup, name='register'),
    path('auth/me/', views.get_user_profile, name='user_profile'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Card management endpoints
    path('cards/', cards.list_cards, name='list_cards'),
    path('cards/create/', cards.create_card, name='create_card'),
    path('cards/<str:card_id>/', cards.get_card, name='get_card'),
    path('cards/<str:card_id>/cancel/', cards.cancel_card, name='cancel_card'),
    path('cards/<str:card_id>/transactions/', cards.get_card_transactions, name='get_card_transactions'),
    path('cards/<str:card_id>/stats/', cards.get_card_stats, name='get_card_stats'),
    
    # Webhook endpoint
    path('webhooks/privacy/', PrivacyWebhookView.as_view(), name='privacy_webhook'),
] 