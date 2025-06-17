from abc import ABC, abstractmethod
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import time
import random
from ratelimit import limits, sleep_and_retry
from tenacity import retry, stop_after_attempt, wait_exponential

class BaseScraper(ABC):
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
    
    def get_headers(self):
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Pragma': 'no-cache'
        }
    
    @sleep_and_retry
    @limits(calls=5, period=60)  # Reduced to 5 calls per minute
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def make_request(self, url):
        """Make a request with rate limiting and retry logic"""
        # Add random delay between requests
        time.sleep(random.uniform(2, 5))
        
        response = self.session.get(url, headers=self.get_headers())
        response.raise_for_status()
        return response
    
    def parse_html(self, html_content):
        """Parse HTML content using BeautifulSoup"""
        return BeautifulSoup(html_content, 'html.parser')
    
    @abstractmethod
    def search_products(self, query):
        """Search for products based on query"""
        pass
    
    @abstractmethod
    def get_product_details(self, product_url):
        """Get detailed information about a specific product"""
        pass
    
    def clean_price(self, price_str):
        """Clean and convert price string to float"""
        if not price_str:
            return None
        # Remove currency symbols and other non-numeric characters except decimal point
        cleaned = ''.join(c for c in price_str if c.isdigit() or c == '.')
        try:
            return float(cleaned)
        except ValueError:
            return None 