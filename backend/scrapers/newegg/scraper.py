from ..base_scraper import BaseScraper
import urllib.parse
import json
import time
import random

class NeweggScraper(BaseScraper):
    BASE_URL = "https://www.newegg.com"
    SEARCH_URL = f"{BASE_URL}/p/pl?d="
    API_URL = "https://www.newegg.com/api/search/v2"
    
    def search_products(self, query):
        """Search for products on Newegg"""
        try:
            # First try the API endpoint
            products = self._search_api(query)
            if products:
                return products
            
            # Fallback to HTML scraping if API fails
            return self._search_html(query)
            
        except Exception as e:
            print(f"Error searching Newegg products: {str(e)}")
            return []
    
    def _search_api(self, query):
        """Search using Newegg's API"""
        try:
            params = {
                'query': query,
                'pageSize': 20,
                'pageNumber': 1,
                'sort': 'FEATURED'
            }
            
            headers = self.get_headers()
            headers.update({
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Referer': f"{self.SEARCH_URL}{urllib.parse.quote(query)}"
            })
            
            response = self.session.get(
                self.API_URL,
                params=params,
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            products = []
            
            for item in data.get('ProductList', []):
                try:
                    product = {
                        'name': item.get('Title', ''),
                        'price': self.clean_price(str(item.get('FinalPrice', 0))),
                        'image_url': item.get('ImageUrl', ''),
                        'source_url': f"{self.BASE_URL}{item.get('ProductUrl', '')}",
                        'description': item.get('Description', '')
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
        url = f"{self.SEARCH_URL}{encoded_query}"
        
        try:
            response = self.make_request(url)
            soup = self.parse_html(response.text)
            
            products = []
            # Find product items
            product_items = soup.select('.item-cell')
            
            for item in product_items:
                try:
                    product = {
                        'name': item.select_one('.item-title').text.strip(),
                        'price': self.clean_price(item.select_one('.price-current').text.strip()),
                        'image_url': item.select_one('.item-img img')['src'],
                        'source_url': self.BASE_URL + item.select_one('.item-title')['href'],
                        'description': item.select_one('.item-description').text.strip() if item.select_one('.item-description') else ''
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
                'name': soup.select_one('.product-title').text.strip(),
                'price': self.clean_price(soup.select_one('.price-current').text.strip()),
                'image_url': soup.select_one('.product-view-img-original')['src'],
                'source_url': product_url,
                'description': soup.select_one('.product-bullets').text.strip() if soup.select_one('.product-bullets') else '',
                'specifications': self._extract_specifications(soup)
            }
            
            return product
        except Exception as e:
            print(f"Error getting Newegg product details: {str(e)}")
            return None
    
    def _extract_specifications(self, soup):
        """Extract product specifications"""
        specs = {}
        try:
            spec_table = soup.select_one('.product-specs')
            if spec_table:
                rows = spec_table.select('tr')
                for row in rows:
                    label = row.select_one('th')
                    value = row.select_one('td')
                    if label and value:
                        specs[label.text.strip()] = value.text.strip()
        except Exception as e:
            print(f"Error extracting specifications: {str(e)}")
        return specs 