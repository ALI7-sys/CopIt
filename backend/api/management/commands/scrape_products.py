from django.core.management.base import BaseCommand
from api.models import Product
from scrapers import NeweggScraper, BackMarketScraper
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Scrape products from Newegg and Back Market'

    def add_arguments(self, parser):
        parser.add_argument('query', type=str, help='Search query for products')
        parser.add_argument('--site', type=str, choices=['newegg', 'backmarket', 'all'], default='all',
                          help='Site to scrape (default: all)')
        parser.add_argument('--limit', type=int, default=10,
                          help='Maximum number of products to scrape per site (default: 10)')

    def handle(self, *args, **options):
        query = options['query']
        site = options['site']
        limit = options['limit']

        self.stdout.write(f"Starting to scrape products for query: {query}")

        scrapers = []
        if site == 'all' or site == 'newegg':
            scrapers.append(('Newegg', NeweggScraper()))
        if site == 'all' or site == 'backmarket':
            scrapers.append(('Back Market', BackMarketScraper()))

        total_products = 0
        for site_name, scraper in scrapers:
            try:
                self.stdout.write(f"\nScraping {site_name}...")
                products = scraper.search_products(query)
                
                # Limit the number of products
                products = products[:limit]
                
                for product_data in products:
                    try:
                        # Get detailed product information
                        details = scraper.get_product_details(product_data['source_url'])
                        if not details:
                            continue

                        # Create or update product in database
                        product, created = Product.objects.update_or_create(
                            source_url=details['source_url'],
                            defaults={
                                'name': details['name'],
                                'description': details.get('description', ''),
                                'price': details['price'],
                                'image_url': details['image_url'],
                                'stock': 1  # Default stock value
                            }
                        )

                        if created:
                            self.stdout.write(self.style.SUCCESS(f"Created product: {product.name}"))
                        else:
                            self.stdout.write(f"Updated product: {product.name}")
                        
                        total_products += 1

                    except Exception as e:
                        logger.error(f"Error processing product {product_data.get('name', 'Unknown')}: {str(e)}")
                        continue

            except Exception as e:
                logger.error(f"Error scraping {site_name}: {str(e)}")
                self.stdout.write(self.style.ERROR(f"Error scraping {site_name}: {str(e)}"))
                continue

        self.stdout.write(self.style.SUCCESS(f"\nSuccessfully processed {total_products} products")) 