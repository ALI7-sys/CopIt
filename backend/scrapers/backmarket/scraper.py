from ..base_scraper import BaseScraper
import urllib.parse
import json
import time
import random

class BackMarketScraper(BaseScraper):
    BASE_URL = "https://www.backmarket.com"
    SEARCH_URL = f"{BASE_URL}/search"
    API_URL = f"{BASE_URL}/api/v1/products"
    
    def search_products(self, query):
        """Search for products on Back Market"""
        try:
            # First try the API endpoint
            products = self._search_api(query)
            if products:
                return products
            
            # Fallback to HTML scraping if API fails
            return self._search_html(query)
            
        except Exception as e:
            print(f"Error searching Back Market products: {str(e)}")
            return []
    
    def _search_api(self, query):
        """Search using Back Market's API"""
        try:
            params = {
                'q': query,
                'limit': 20,
                'offset': 0,
                'sort': 'relevance'
            }
            
            headers = self.get_headers()
            headers.update({
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Referer': f"{self.SEARCH_URL}?q={urllib.parse.quote(query)}"
            })
            
            response = self.session.get(
                self.API_URL,
                params=params,
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            products = []
            
            for item in data.get('products', []):
                try:
                    product = {
                        'name': item.get('name', ''),
                        'price': self.clean_price(str(item.get('price', {}).get('amount', 0))),
                        'image_url': item.get('images', [{}])[0].get('url', ''),
                        'source_url': f"{self.BASE_URL}{item.get('url', '')}",
                        'description': item.get('description', ''),
                        'condition': item.get('condition', '')
                    }
                    products.append(product)
                except (AttributeError, KeyError) as e:
                    continue
            
            return products
            
        except Exception as e:
            print(f"Error in API search: {str(e)}")
            return []
    
    def _search_html(self, query):
        """Fallback to HTML scraping"""
        encoded_query = urllib.parse.quote(query)
        url = f"{self.SEARCH_URL}?q={encoded_query}"
        
        try:
            response = self.make_request(url)
            soup = self.parse_html(response.text)
            
            products = []
            # Find product items
            product_items = soup.select('[data-test="product-card"]')
            
            for item in product_items:
                try:
                    product = {
                        'name': item.select_one('[data-test="product-card-title"]').text.strip(),
                        'price': self.clean_price(item.select_one('[data-test="product-card-price"]').text.strip()),
                        'image_url': item.select_one('img')['src'],
                        'source_url': self.BASE_URL + item.select_one('a')['href'],
                        'description': item.select_one('[data-test="product-card-description"]').text.strip() if item.select_one('[data-test="product-card-description"]') else '',
                        'condition': item.select_one('[data-test="product-card-condition"]').text.strip() if item.select_one('[data-test="product-card-condition"]') else ''
                    }
                    products.append(product)
                except (AttributeError, KeyError) as e:
                    continue
            
            return products
        except Exception as e:
            print(f"Error in HTML search: {str(e)}")
            return []
    
    def get_product_details(self, product_url):
        """Get detailed information about a specific product"""
        try:
            response = self.make_request(product_url)
            soup = self.parse_html(response.text)
            
            # Extract product details
            product = {
                'name': soup.select_one('[data-test="product-title"]').text.strip(),
                'price': self.clean_price(soup.select_one('[data-test="product-price"]').text.strip()),
                'image_url': soup.select_one('[data-test="product-image"]')['src'],
                'source_url': product_url,
                'description': soup.select_one('[data-test="product-description"]').text.strip() if soup.select_one('[data-test="product-description"]') else '',
                'condition': soup.select_one('[data-test="product-condition"]').text.strip() if soup.select_one('[data-test="product-condition"]') else '',
                'specifications': self._extract_specifications(soup)
            }
            
            return product
        except Exception as e:
            print(f"Error getting Back Market product details: {str(e)}")
            return None
    
    def _extract_specifications(self, soup):
        """Extract product specifications"""
        specs = {}
        try:
            spec_sections = soup.select('[data-test="product-specifications"]')
            for section in spec_sections:
                title = section.select_one('[data-test="specification-title"]')
                if title:
                    specs[title.text.strip()] = {}
                    items = section.select('[data-test="specification-item"]')
                    for item in items:
                        label = item.select_one('[data-test="specification-label"]')
                        value = item.select_one('[data-test="specification-value"]')
                        if label and value:
                            specs[title.text.strip()][label.text.strip()] = value.text.strip()
        except Exception as e:
            print(f"Error extracting specifications: {str(e)}")
        return specs 