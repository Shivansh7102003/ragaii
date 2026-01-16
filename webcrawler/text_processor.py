"""
Text Processor Module
Handles text normalization and chunking with metadata
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict
import re


class TextProcessor:
    """
    Processes and chunks text content for embedding
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):
        """
        Initialize text processor
        
        Args:
            chunk_size: Size of each text chunk
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def normalize_text(self, text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: Raw text
            
        Returns:
            Normalized text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters (keep basic punctuation)
        text = re.sub(r'[^\w\s.,!?;:()\-\'"]+', '', text)
        
        # Normalize line breaks
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove multiple consecutive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def chunk_text(self, text: str, metadata: Dict[str, str]) -> List[Dict[str, any]]:
        """
        Split text into semantic chunks with metadata
        
        Args:
            text: Text to chunk
            metadata: Metadata to attach to each chunk (url, title, etc.)
            
        Returns:
            List of dictionaries containing:
                - 'text': Chunk text
                - 'metadata': Metadata dict
                - 'chunk_index': Index of chunk
        """
        # Normalize text first
        normalized_text = self.normalize_text(text)
        
        # Split into chunks
        chunks = self.text_splitter.split_text(normalized_text)
        
        # Attach metadata to each chunk
        chunked_data = []
        for idx, chunk in enumerate(chunks):
            chunk_data = {
                'text': chunk,
                'metadata': {
                    **metadata,  # Include all original metadata
                    'chunk_index': idx,
                    'total_chunks': len(chunks)
                }
            }
            chunked_data.append(chunk_data)
        
        return chunked_data
    
    def process(self, content: str, metadata: Dict[str, str]) -> List[Dict[str, any]]:
        """
        Main processing function - normalizes and chunks text
        
        Args:
            content: Raw text content
            metadata: Metadata (url, title, etc.)
            
        Returns:
            List of chunks with metadata
        """
        if not content or len(content.strip()) == 0:
            return []
        
        return self.chunk_text(content, metadata)
