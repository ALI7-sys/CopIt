from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from datetime import timedelta
from .models import Order, OrderItem, Product, Category

class SalesReport:
    @staticmethod
    def get_daily_sales(days=30):
        """Get daily sales for the last N days"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        return Order.objects.filter(
            created_at__range=(start_date, end_date),
            status='COMPLETED'
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            total_sales=Sum('total_amount'),
            order_count=Count('id')
        ).order_by('date')
    
    @staticmethod
    def get_monthly_sales(months=12):
        """Get monthly sales for the last N months"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30 * months)
        
        return Order.objects.filter(
            created_at__range=(start_date, end_date),
            status='COMPLETED'
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            total_sales=Sum('total_amount'),
            order_count=Count('id')
        ).order_by('month')
    
    @staticmethod
    def get_product_sales():
        """Get sales by product"""
        return OrderItem.objects.values(
            'product__name'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('price'),
            order_count=Count('order')
        ).order_by('-total_revenue')
    
    @staticmethod
    def get_category_sales():
        """Get sales by category"""
        return OrderItem.objects.values(
            'product__category__name'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('price'),
            order_count=Count('order')
        ).order_by('-total_revenue')
    
    @staticmethod
    def get_customer_metrics():
        """Get customer-related metrics"""
        return {
            'total_customers': Order.objects.values('user').distinct().count(),
            'average_order_value': Order.objects.filter(
                status='COMPLETED'
            ).aggregate(
                avg=Avg('total_amount')
            )['avg'] or 0,
            'repeat_customers': Order.objects.values('user').annotate(
                order_count=Count('id')
            ).filter(order_count__gt=1).count()
        }
    
    @staticmethod
    def get_inventory_metrics():
        """Get inventory-related metrics"""
        return {
            'total_products': Product.objects.count(),
            'low_stock_products': Product.objects.filter(stock__lt=10).count(),
            'out_of_stock_products': Product.objects.filter(stock=0).count(),
            'total_inventory_value': Product.objects.aggregate(
                total=Sum('price' * 'stock')
            )['total'] or 0
        }
    
    @staticmethod
    def get_comprehensive_report():
        """Get a comprehensive sales report"""
        return {
            'daily_sales': list(SalesReport.get_daily_sales()),
            'monthly_sales': list(SalesReport.get_monthly_sales()),
            'product_sales': list(SalesReport.get_product_sales()),
            'category_sales': list(SalesReport.get_category_sales()),
            'customer_metrics': SalesReport.get_customer_metrics(),
            'inventory_metrics': SalesReport.get_inventory_metrics()
        } 