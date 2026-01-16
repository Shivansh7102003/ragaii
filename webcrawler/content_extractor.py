"""
Content Extractor Module
Extracts clean, meaningful content from HTML while removing boilerplate
"""

from bs4 import BeautifulSoup
import trafilatura
from typing import Dict, Optional
import hashlib


class ContentExtractor:
    """
    Extracts and cleans content from HTML pages
    """
    
    def __init__(self):
        """Initialize the content extractor"""
        self.seen_hashes = set()  # Track content hashes to avoid duplicates
    
    def extract_with_trafilatura(self, html: str, url: str) -> Optional[str]:
        """
        Extract main content using trafilatura (removes boilerplate automatically)
        
        Args:
            html: Raw HTML string
            url: Source URL
            
        Returns:
            Cleaned text content or None
        """
        try:
            # Trafilatura automatically removes headers, footers, nav, ads, etc.
            content = trafilatura.extract(
                html,
                url=url,
                include_comments=False,
                include_tables=True,
                no_fallback=False,
                favor_precision=True
            )
            return content
        except Exception as e:
            print(f"Trafilatura extraction failed: {e}")
            return None
    
    def extract_with_beautifulsoup(self, soup: BeautifulSoup) -> str:
        """
        Fallback extraction using BeautifulSoup
        Removes common boilerplate elements manually
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Cleaned text content
        """
        # Remove unwanted tags
        for tag in soup(['header', 'footer', 'nav', 'aside', 'script', 
                        'style', 'iframe', 'noscript', 'form']):
            tag.decompose()
        
        # Remove common ad/navigation classes
        ad_classes = ['advertisement', 'ad-', 'banner', 'sidebar', 
                     'navigation', 'menu', 'footer', 'header']
        for class_name in ad_classes:
            for element in soup.find_all(class_=lambda x: x and class_name in x.lower()):
                element.decompose()
        
        # Extract text from main content areas
        main_content = soup.find('main') or soup.find('article') or soup.find('body')
        
        if main_content:
            text = main_content.get_text(separator='\n', strip=True)
        else:
            text = soup.get_text(separator='\n', strip=True)
        
        # Clean up whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)
    
    def get_content_hash(self, text: str) -> str:
        """
        Generate hash of content for duplicate detection
        
        Args:
            text: Text content
            
        Returns:
            MD5 hash of the text
        """
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def is_duplicate(self, text: str) -> bool:
        """
        Check if content is duplicate
        
        Args:
            text: Text content
            
        Returns:
            True if duplicate, False otherwise
        """
        content_hash = self.get_content_hash(text)
        
        if content_hash in self.seen_hashes:
            return True
        
        self.seen_hashes.add(content_hash)
        return False
    
    def extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, str]:
        """
        Extract metadata from HTML
        
        Args:
            soup: BeautifulSoup object
            url: Source URL
            
        Returns:
            Dictionary with metadata (title, description, etc.)
        """
        metadata = {
            'url': url,
            'title': '',
            'description': ''
        }
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text(strip=True)
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            metadata['description'] = meta_desc['content']
        
        return metadata
    
    def extract(self, html: str, soup: BeautifulSoup, url: str) -> Dict[str, any]:
        """
        Main extraction function - tries trafilatura first, falls back to BeautifulSoup
        
        Args:
            html: Raw HTML string
            soup: BeautifulSoup object
            url: Source URL
            
        Returns:
            Dictionary containing:
                - 'content': Cleaned text content
                - 'metadata': Page metadata
                - 'is_duplicate': Whether content is duplicate
        """
        # Try trafilatura first (best for removing boilerplate)
        content = self.extract_with_trafilatura(html, url)
        
        # Fallback to BeautifulSoup if trafilatura fails
        if not content or len(content.strip()) < 100:
            content = self.extract_with_beautifulsoup(soup)
        
        # Extract metadata
        metadata = self.extract_metadata(soup, url)
        
        # Check for duplicates
        is_duplicate = self.is_duplicate(content)
        
        return {
            'content': content,
            'metadata': metadata,
            'is_duplicate': is_duplicate
        }
