from django.contrib.auth.models import AbstractUser
from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator

class FXTransaction(models.Model):
    """Model for storing foreign exchange transaction logs"""
    
    transaction_id = models.CharField(max_length=100, unique=True)
    source_currency = models.CharField(max_length=3)
    target_currency = models.CharField(max_length=3)
    source_amount = models.DecimalField(max_digits=20, decimal_places=2)
    target_amount = models.DecimalField(max_digits=20, decimal_places=2)
    exchange_rate = models.DecimalField(max_digits=20, decimal_places=6)
    fee = models.DecimalField(max_digits=20, decimal_places=2)
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'fx_transactions'
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['source_currency', 'target_currency']),
        ]
    
    def __str__(self):
        return f"FX Transaction {self.transaction_id} - {self.source_amount} {self.source_currency} → {self.target_amount} {self.target_currency}"
    
    @property
    def total_cost(self) -> Decimal:
        """Calculate total cost including fee"""
        return self.target_amount + self.fee 

class User(AbstractUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, default='')
    address = models.TextField(blank=True, default='')
    preferences = models.JSONField(default=dict, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']
    
    def __str__(self):
        return self.email 

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    image_url = models.URLField()
    source_url = models.URLField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return 0
        return sum(review.rating for review in reviews) / len(reviews)

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    
    @property
    def subtotal(self):
        return self.product.price * self.quantity

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order {self.id} - {self.user.email}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order
    
    @property
    def subtotal(self):
        return self.price * self.quantity 

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('product', 'user')
    
    def __str__(self):
        return f"Review by {self.user.email} for {self.product.name}"

class Wishlist(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, related_name='wishlists')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Wishlist for {self.user.email}"

class UserActivity(models.Model):
    ACTIVITY_TYPES = [
        ('view', 'Product View'),
        ('search', 'Search'),
        ('cart_add', 'Add to Cart'),
        ('cart_remove', 'Remove from Cart'),
        ('purchase', 'Purchase'),
        ('review', 'Review'),
    ]
    
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    details = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "User Activities"
    
    def __str__(self):
        return f"{self.user.email} - {self.activity_type}" 