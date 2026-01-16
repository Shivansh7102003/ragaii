"""
Web Crawler Module - Main Interface
Orchestrates the entire web crawling and embedding pipeline
"""

from .crawler import WebCrawler
from .content_extractor import ContentExtractor
from .text_processor import TextProcessor
from .embedding_manager import EmbeddingManager
from .faiss_storage import FAISSStorage

from typing import Dict, Optional, Tuple
from urllib.parse import urlparse
import hashlib


def url_to_index_name(url: str) -> str:
    """
    Convert URL to a valid index name
    
    Args:
        url: Website URL
        
    Returns:
        Safe index name
    """
    # Use domain + hash for uniqueness
    parsed = urlparse(url)
    domain = parsed.netloc.replace('www.', '')
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    
    # Create safe filename
    safe_name = f"{domain}_{url_hash}".replace('.', '_').replace('/', '_')
    return safe_name


def process_website(
    url: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 100,
    force_reindex: bool = False,
    storage_dir: str = "faiss_indexes"
) -> Dict[str, any]:
    """
    Main function to process a website and create/load FAISS index
    
    Args:
        url: Website URL to process
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
        force_reindex: If True, re-crawl even if index exists
        storage_dir: Directory to store FAISS indexes
        
    Returns:
        Dictionary containing:
            - 'success': Boolean indicating success
            - 'retriever': FAISS retriever (if successful)
            - 'db': FAISS database (if successful)
            - 'metadata': Website metadata
            - 'error': Error message (if failed)
            - 'index_name': Name of the index
            - 'was_cached': Whether index was loaded from cache
    """
    
    # Initialize components
    crawler = WebCrawler()
    extractor = ContentExtractor()
    processor = TextProcessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    embedding_manager = EmbeddingManager()
    storage = FAISSStorage(storage_dir=storage_dir)
    
    # Generate index name from URL
    index_name = url_to_index_name(url)
    
    # Check if index already exists (unless force_reindex)
    if not force_reindex and storage.index_exists(index_name):
        print(f"📦 Loading existing index for: {url}")
        
        # Load existing index
        faiss_index = storage.load_index(index_name, embedding_manager.embedding_model)
        metadata = storage.load_metadata(index_name)
        
        if faiss_index:
            retriever = faiss_index.as_retriever(search_kwargs={"k": 5})
            return {
                'success': True,
                'retriever': retriever,
                'db': faiss_index,
                'metadata': metadata,
                'error': None,
                'index_name': index_name,
                'was_cached': True
            }
    
    print(f"🌐 Crawling website: {url}")
    
    # Step 1: Crawl the website
    crawl_result = crawler.crawl(url)
    
    if crawl_result['error']:
        return {
            'success': False,
            'retriever': None,
            'db': None,
            'metadata': None,
            'error': crawl_result['error'],
            'index_name': index_name,
            'was_cached': False
        }
    
    print(f"✓ Website crawled successfully")
    
    # Step 2: Extract content
    extraction_result = extractor.extract(
        crawl_result['html'],
        crawl_result['soup'],
        crawl_result['url']
    )
    
    if extraction_result['is_duplicate']:
        print("⚠ Duplicate content detected")
    
    content = extraction_result['content']
    metadata = extraction_result['metadata']
    
    if not content or len(content.strip()) < 50:
        return {
            'success': False,
            'retriever': None,
            'db': None,
            'metadata': metadata,
            'error': 'Insufficient content extracted from website',
            'index_name': index_name,
            'was_cached': False
        }
    
    print(f"✓ Content extracted ({len(content)} characters)")
    
    # Step 3: Process and chunk text
    chunks = processor.process(content, metadata)
    
    if not chunks:
        return {
            'success': False,
            'retriever': None,
            'db': None,
            'metadata': metadata,
            'error': 'Failed to create text chunks',
            'index_name': index_name,
            'was_cached': False
        }
    
    print(f"✓ Text chunked into {len(chunks)} pieces")
    
    # Step 4: Create embeddings and FAISS index
    try:
        faiss_index = embedding_manager.create_faiss_index(chunks)
        print(f"✓ FAISS index created with {len(chunks)} embeddings")
    except Exception as e:
        return {
            'success': False,
            'retriever': None,
            'db': None,
            'metadata': metadata,
            'error': f'Failed to create embeddings: {str(e)}',
            'index_name': index_name,
            'was_cached': False
        }
    
    # Step 5: Save to disk
    try:
        storage.save_index(faiss_index, index_name, metadata)
    except Exception as e:
        print(f"⚠ Warning: Failed to save index to disk: {e}")
        # Continue anyway - index is still usable in memory
    
    # Step 6: Create retriever
    retriever = faiss_index.as_retriever(search_kwargs={"k": 5})
    
    return {
        'success': True,
        'retriever': retriever,
        'db': faiss_index,
        'metadata': metadata,
        'error': None,
        'index_name': index_name,
        'was_cached': False
    }


# Export main function
__all__ = ['process_website', 'url_to_index_name']
