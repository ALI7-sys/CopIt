import requests
from bs4 import BeautifulSoup
import time
import random
from typing import List, Dict, Optional
from fake_useragent import UserAgent
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ProductScraper:
    def __init__(self, base_url: str, delay_range: tuple = (2, 5)):
        self.base_url = base_url
        self.delay_range = delay_range
        self.ua = UserAgent()
        self.session = requests.Session()
        
    def _get_headers(self) -> Dict[str, str]:
        """Generate random headers for each request"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def _random_delay(self):
        """Add random delay between requests"""
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)
    
    def scrape_product_list(self, category: str, max_pages: int = 3) -> List[Dict]:
        """Scrape product listings from a category page"""
        products = []
        
        for page in range(1, max_pages + 1):
            try:
                url = f"{self.base_url}/{category}?page={page}"
                logger.info(f"Scraping page {page} of {category}")
                
                response = self.session.get(url, headers=self._get_headers())
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                product_cards = soup.find_all('div', class_='product-card')  # Adjust selector based on target site
                
                for card in product_cards:
                    try:
                        product = {
                            'name': card.find('h2', class_='product-title').text.strip(),
                            'price': float(card.find('span', class_='price').text.strip().replace('$', '')),
                            'description': card.find('p', class_='description').text.strip(),
                            'stock': random.randint(5, 50),  # Random stock for testing
                            'image_url': card.find('img')['src'],
                            'source_url': card.find('a')['href'],
                            'created_at': datetime.now().isoformat(),
                            'updated_at': datetime.now().isoformat()
                        }
                        products.append(product)
                    except Exception as e:
                        logger.error(f"Error parsing product card: {e}")
                        continue
                
                self._random_delay()
                
            except Exception as e:
                logger.error(f"Error scraping page {page}: {e}")
                break
        
        return products

class AmazonScraper(ProductScraper):
    def __init__(self):
        super().__init__('https://www.amazon.com')
        self.delay_range = (3, 7)  # Longer delays for Amazon
    
    def scrape_product_list(self, category: str, max_pages: int = 2) -> List[Dict]:
        """Scrape product listings from Amazon"""
        products = []
        
        for page in range(1, max_pages + 1):
            try:
                url = f"{self.base_url}/s?k={category}&page={page}"
                logger.info(f"Scraping Amazon page {page} for {category}")
                
                response = self.session.get(url, headers=self._get_headers())
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                product_cards = soup.find_all('div', {'data-component-type': 's-search-result'})
                
                for card in product_cards:
                    try:
                        title_elem = card.find('h2')
                        price_elem = card.find('span', class_='a-price-whole')
                        image_elem = card.find('img', class_='s-image')
                        
                        if not all([title_elem, price_elem, image_elem]):
                            continue
                            
                        product = {
                            'name': title_elem.text.strip(),
                            'price': float(price_elem.text.strip().replace(',', '')),
                            'description': title_elem.text.strip(),  # Using title as description
                            'stock': random.randint(5, 50),
                            'image_url': image_elem['src'],
                            'source_url': f"{self.base_url}{title_elem.find('a')['href']}",
                            'created_at': datetime.now().isoformat(),
                            'updated_at': datetime.now().isoformat()
                        }
                        products.append(product)
                    except Exception as e:
                        logger.error(f"Error parsing Amazon product card: {e}")
                        continue
                
                self._random_delay()
                
            except Exception as e:
                logger.error(f"Error scraping Amazon page {page}: {e}")
                break
        
        return products

def get_scraper(site: str) -> ProductScraper:
    """Factory function to get appropriate scraper"""
    scrapers = {
        'amazon': AmazonScraper,
        # Add more scrapers here
    }
    return scrapers.get(site.lower(), ProductScraper)() 