"""
Embedding Manager Module
Generates embeddings and creates FAISS index
"""

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from typing import List, Dict


class EmbeddingManager:
    """
    Manages embedding generation and FAISS index creation
    """
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize embedding manager
        
        Args:
            model_name: HuggingFace model name for embeddings
        """
        self.model_name = model_name
        self.embedding_model = HuggingFaceEmbeddings(model_name=model_name)
    
    def create_documents(self, chunks: List[Dict[str, any]]) -> List[Document]:
        """
        Convert chunks to LangChain Document objects
        
        Args:
            chunks: List of chunk dictionaries with 'text' and 'metadata'
            
        Returns:
            List of Document objects
        """
        documents = []
        for chunk in chunks:
            doc = Document(
                page_content=chunk['text'],
                metadata=chunk['metadata']
            )
            documents.append(doc)
        
        return documents
    
    def create_faiss_index(self, chunks: List[Dict[str, any]]) -> FAISS:
        """
        Create FAISS vector store from chunks
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            FAISS vector store
        """
        if not chunks:
            raise ValueError("No chunks provided for embedding")
        
        # Convert to Document objects
        documents = self.create_documents(chunks)
        
        # Create FAISS index
        faiss_index = FAISS.from_documents(documents, self.embedding_model)
        
        return faiss_index
    
    def add_to_index(self, faiss_index: FAISS, chunks: List[Dict[str, any]]) -> FAISS:
        """
        Add new chunks to existing FAISS index
        
        Args:
            faiss_index: Existing FAISS index
            chunks: New chunks to add
            
        Returns:
            Updated FAISS index
        """
        if not chunks:
            return faiss_index
        
        documents = self.create_documents(chunks)
        faiss_index.add_documents(documents)
        
        return faiss_index
