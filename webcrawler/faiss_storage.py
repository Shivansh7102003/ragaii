"""
FAISS Storage Module
Handles saving and loading FAISS indexes with metadata
"""

import os
import json
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from typing import Optional, Dict
import pickle


class FAISSStorage:
    """
    Manages FAISS index persistence to disk
    """
    
    def __init__(self, storage_dir: str = "faiss_indexes"):
        """
        Initialize FAISS storage
        
        Args:
            storage_dir: Directory to store FAISS indexes
        """
        self.storage_dir = storage_dir
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)
    
    def _get_index_path(self, index_name: str) -> str:
        """Get path for FAISS index"""
        return os.path.join(self.storage_dir, index_name)
    
    def _get_metadata_path(self, index_name: str) -> str:
        """Get path for metadata file"""
        return os.path.join(self.storage_dir, f"{index_name}_metadata.json")
    
    def save_index(self, faiss_index: FAISS, index_name: str, metadata: Dict = None):
        """
        Save FAISS index to disk
        
        Args:
            faiss_index: FAISS vector store
            index_name: Name for the index
            metadata: Optional metadata to save alongside index
        """
        try:
            # Save FAISS index
            index_path = self._get_index_path(index_name)
            faiss_index.save_local(index_path)
            
            # Save metadata if provided
            if metadata:
                metadata_path = self._get_metadata_path(index_name)
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2)
            
            print(f"✓ FAISS index saved to: {index_path}")
            
        except Exception as e:
            print(f"✗ Error saving FAISS index: {e}")
            raise
    
    def load_index(self, index_name: str, embedding_model: HuggingFaceEmbeddings) -> Optional[FAISS]:
        """
        Load FAISS index from disk
        
        Args:
            index_name: Name of the index to load
            embedding_model: Embedding model to use with the index
            
        Returns:
            FAISS vector store or None if not found
        """
        try:
            index_path = self._get_index_path(index_name)
            
            # Check if index exists
            if not os.path.exists(index_path):
                print(f"Index '{index_name}' not found at {index_path}")
                return None
            
            # Load FAISS index
            faiss_index = FAISS.load_local(
                index_path, 
                embedding_model,
                allow_dangerous_deserialization=True
            )
            
            print(f"✓ FAISS index loaded from: {index_path}")
            return faiss_index
            
        except Exception as e:
            print(f"✗ Error loading FAISS index: {e}")
            return None
    
    def load_metadata(self, index_name: str) -> Optional[Dict]:
        """
        Load metadata for an index
        
        Args:
            index_name: Name of the index
            
        Returns:
            Metadata dictionary or None if not found
        """
        try:
            metadata_path = self._get_metadata_path(index_name)
            
            if not os.path.exists(metadata_path):
                return None
            
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            return metadata
            
        except Exception as e:
            print(f"✗ Error loading metadata: {e}")
            return None
    
    def index_exists(self, index_name: str) -> bool:
        """
        Check if an index exists
        
        Args:
            index_name: Name of the index
            
        Returns:
            True if exists, False otherwise
        """
        index_path = self._get_index_path(index_name)
        return os.path.exists(index_path)
    
    def list_indexes(self) -> list:
        """
        List all available indexes
        
        Returns:
            List of index names
        """
        if not os.path.exists(self.storage_dir):
            return []
        
        # Get all directories in storage_dir
        indexes = [
            d for d in os.listdir(self.storage_dir)
            if os.path.isdir(os.path.join(self.storage_dir, d))
        ]
        
        return indexes
    
    def delete_index(self, index_name: str):
        """
        Delete an index and its metadata
        
        Args:
            index_name: Name of the index to delete
        """
        import shutil
        
        try:
            # Delete index directory
            index_path = self._get_index_path(index_name)
            if os.path.exists(index_path):
                shutil.rmtree(index_path)
            
            # Delete metadata file
            metadata_path = self._get_metadata_path(index_name)
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
            
            print(f"✓ Index '{index_name}' deleted")
            
        except Exception as e:
            print(f"✗ Error deleting index: {e}")
            raise
