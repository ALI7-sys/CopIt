from django.core.management.base import BaseCommand
from api.models import Product, Category

SAMPLE_CATEGORIES = [
    {
        'name': 'Smartphones',
        'description': 'Latest mobile phones and accessories'
    },
    {
        'name': 'Laptops',
        'description': 'High-performance laptops and notebooks'
    },
    {
        'name': 'Tablets',
        'description': 'Tablets and e-readers'
    },
    {
        'name': 'Accessories',
        'description': 'Tech accessories and peripherals'
    },
    {
        'name': 'Gaming',
        'description': 'Gaming consoles and accessories'
    }
]

SAMPLE_PRODUCTS = [
    # Smartphones
    {
        'name': 'Apple iPhone 13',
        'description': '128GB, Blue, Unlocked. The latest iPhone with A15 Bionic chip.',
        'price': 799.99,
        'stock': 10,
        'image_url': 'https://dummyimage.com/300x300/000/fff&text=iPhone+13',
        'source_url': 'https://www.apple.com/iphone-13/',
        'category_name': 'Smartphones'
    },
    {
        'name': 'Samsung Galaxy S22',
        'description': '256GB, Phantom Black, Unlocked. Pro-grade camera and 8K video.',
        'price': 699.99,
        'stock': 15,
        'image_url': 'https://dummyimage.com/300x300/000/fff&text=Galaxy+S22',
        'source_url': 'https://www.samsung.com/galaxy-s22/',
        'category_name': 'Smartphones'
    },
    {
        'name': 'Google Pixel 7',
        'description': '128GB, Snow, Unlocked. Google Tensor G2 and amazing camera.',
        'price': 599.99,
        'stock': 12,
        'image_url': 'https://dummyimage.com/300x300/000/fff&text=Pixel+7',
        'source_url': 'https://store.google.com/pixel_7/',
        'category_name': 'Smartphones'
    },
    
    # Laptops
    {
        'name': 'MacBook Pro 14"',
        'description': 'Apple M1 Pro chip, 16GB RAM, 512GB SSD.',
        'price': 1999.99,
        'stock': 5,
        'image_url': 'https://dummyimage.com/300x300/000/fff&text=MacBook+Pro+14',
        'source_url': 'https://www.apple.com/macbook-pro-14/',
        'category_name': 'Laptops'
    },
    {
        'name': 'Dell XPS 13',
        'description': '13.4" FHD, Intel i7, 16GB RAM, 512GB SSD.',
        'price': 1299.99,
        'stock': 8,
        'image_url': 'https://dummyimage.com/300x300/000/fff&text=Dell+XPS+13',
        'source_url': 'https://www.dell.com/xps-13/',
        'category_name': 'Laptops'
    },
    
    # Tablets
    {
        'name': 'iPad Pro 12.9"',
        'description': 'M2 chip, 256GB, Wi-Fi + Cellular, Space Gray.',
        'price': 1099.99,
        'stock': 7,
        'image_url': 'https://dummyimage.com/300x300/000/fff&text=iPad+Pro',
        'source_url': 'https://www.apple.com/ipad-pro/',
        'category_name': 'Tablets'
    },
    {
        'name': 'Samsung Galaxy Tab S9',
        'description': '11" AMOLED, 256GB, Wi-Fi, Snapdragon 8 Gen 2.',
        'price': 799.99,
        'stock': 9,
        'image_url': 'https://dummyimage.com/300x300/000/fff&text=Galaxy+Tab+S9',
        'source_url': 'https://www.samsung.com/galaxy-tab-s9/',
        'category_name': 'Tablets'
    },
    
    # Accessories
    {
        'name': 'AirPods Pro 2',
        'description': 'Active Noise Cancellation, Spatial Audio, USB-C charging.',
        'price': 249.99,
        'stock': 20,
        'image_url': 'https://dummyimage.com/300x300/000/fff&text=AirPods+Pro',
        'source_url': 'https://www.apple.com/airpods-pro/',
        'category_name': 'Accessories'
    },
    {
        'name': 'Samsung Galaxy Watch 6',
        'description': '44mm, LTE, Android Wear OS, Health monitoring.',
        'price': 399.99,
        'stock': 15,
        'image_url': 'https://dummyimage.com/300x300/000/fff&text=Galaxy+Watch+6',
        'source_url': 'https://www.samsung.com/galaxy-watch-6/',
        'category_name': 'Accessories'
    },
    
    # Gaming
    {
        'name': 'PlayStation 5',
        'description': 'Digital Edition, White, 825GB SSD.',
        'price': 399.99,
        'stock': 3,
        'image_url': 'https://dummyimage.com/300x300/000/fff&text=PS5',
        'source_url': 'https://www.playstation.com/ps5/',
        'category_name': 'Gaming'
    },
    {
        'name': 'Xbox Series X',
        'description': '1TB SSD, 4K Gaming, HDR.',
        'price': 499.99,
        'stock': 4,
        'image_url': 'https://dummyimage.com/300x300/000/fff&text=Xbox+Series+X',
        'source_url': 'https://www.xbox.com/series-x',
        'category_name': 'Gaming'
    }
]

class Command(BaseCommand):
    help = 'Load sample product data into the database.'

    def handle(self, *args, **options):
        # Clear existing data
        Product.objects.all().delete()
        Category.objects.all().delete()
        
        # Create categories
        categories = {}
        for cat_data in SAMPLE_CATEGORIES:
            category = Category.objects.create(**cat_data)
            categories[cat_data['name']] = category
        
        # Create products
        for prod in SAMPLE_PRODUCTS:
            category_name = prod.pop('category_name')
            category = categories[category_name]
            Product.objects.create(category=category, **prod)
            
        self.stdout.write(self.style.SUCCESS(f'Loaded {len(SAMPLE_CATEGORIES)} categories and {len(SAMPLE_PRODUCTS)} sample products.')) 