"""
Web Crawler Module
Handles URL validation, content fetching, and HTML parsing
"""

import requests
from bs4 import BeautifulSoup
import validators
from typing import Optional, Dict, List
from urllib.parse import urljoin, urlparse
import time


class WebCrawler:
    """
    Crawls websites and extracts HTML content
    """
    
    def __init__(self, timeout: int = 10, max_retries: int = 3):
        """
        Initialize the web crawler
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def validate_url(self, url: str) -> bool:
        """
        Validate if URL is properly formatted
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        return validators.url(url) is True
    
    def fetch_page(self, url: str) -> Optional[Dict[str, any]]:
        """
        Fetch HTML content from a URL
        
        Args:
            url: URL to fetch
            
        Returns:
            Dictionary containing:
                - 'url': The final URL (after redirects)
                - 'html': Raw HTML content
                - 'status_code': HTTP status code
                - 'error': Error message if any
        """
        # Validate URL
        if not self.validate_url(url):
            return {
                'url': url,
                'html': None,
                'status_code': None,
                'error': 'Invalid URL format'
            }
        
        # Try fetching with retries
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
                
                # Check if successful
                if response.status_code == 200:
                    return {
                        'url': response.url,
                        'html': response.text,
                        'status_code': response.status_code,
                        'error': None
                    }
                else:
                    return {
                        'url': url,
                        'html': None,
                        'status_code': response.status_code,
                        'error': f'HTTP {response.status_code}'
                    }
                    
            except requests.exceptions.Timeout:
                if attempt == self.max_retries - 1:
                    return {
                        'url': url,
                        'html': None,
                        'status_code': None,
                        'error': 'Request timeout'
                    }
                time.sleep(1)  # Wait before retry
                
            except requests.exceptions.ConnectionError:
                return {
                    'url': url,
                    'html': None,
                    'status_code': None,
                    'error': 'Connection error - URL unreachable'
                }
                
            except requests.exceptions.RequestException as e:
                return {
                    'url': url,
                    'html': None,
                    'status_code': None,
                    'error': f'Request failed: {str(e)}'
                }
        
        return {
            'url': url,
            'html': None,
            'status_code': None,
            'error': 'Max retries exceeded'
        }
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """
        Parse HTML content using BeautifulSoup
        
        Args:
            html: Raw HTML string
            
        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(html, 'lxml')
    
    def crawl(self, url: str) -> Optional[Dict[str, any]]:
        """
        Main crawl function - fetches and parses a URL
        
        Args:
            url: URL to crawl
            
        Returns:
            Dictionary containing:
                - 'url': Final URL
                - 'soup': BeautifulSoup object
                - 'html': Raw HTML
                - 'error': Error message if any
        """
        result = self.fetch_page(url)
        
        if result['error']:
            return {
                'url': url,
                'soup': None,
                'html': None,
                'error': result['error']
            }
        
        soup = self.parse_html(result['html'])
        
        return {
            'url': result['url'],
            'soup': soup,
            'html': result['html'],
            'error': None
        }
