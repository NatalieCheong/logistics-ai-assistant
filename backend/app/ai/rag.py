# backend/app/ai/rag.py
"""
RAG (Retrieval Augmented Generation) System
This allows the AI to search through logistics documentation and policies
"""

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from pathlib import Path
from typing import List, Dict, Any
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class LogisticsRAG:
    """
    RAG system for searching logistics documentation
    
    Features:
    - Load documents from PDFs and text files
    - Create embeddings and store in vector database
    - Semantic search over documents
    - Generate answers grounded in documentation
    """
    
    def __init__(self, docs_directory: str = "./docs"):
        """
        Initialize RAG system
        
        Args:
            docs_directory: Path to directory containing documentation
        """
        self.docs_directory = docs_directory
        self.embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0,
            api_key=settings.OPENAI_API_KEY
        )
        
        # Initialize or load vector store
        self.vector_store = self._initialize_vector_store()
        
        # Create retrieval QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 4}
            ),
            return_source_documents=True
        )
    
    def _initialize_vector_store(self) -> Chroma:
        """
        Initialize or load the vector store
        """
        try:
            # Try to load existing vector store
            vector_store = Chroma(
                persist_directory=settings.CHROMA_PERSIST_DIRECTORY,
                embedding_function=self.embeddings
            )
            
            # Check if it has documents
            if vector_store._collection.count() > 0:
                logger.info(f"Loaded existing vector store with {vector_store._collection.count()} documents")
                return vector_store
            
            # If empty, load documents
            logger.info("Vector store is empty. Loading documents...")
            return self._load_documents_to_vector_store()
            
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return self._load_documents_to_vector_store()
    
    def _load_documents_to_vector_store(self) -> Chroma:
        """
        Load documents from directory and create vector store
        """
        documents = []
        
        # Check if docs directory exists
        docs_path = Path(self.docs_directory)
        if not docs_path.exists():
            logger.warning(f"Documents directory {self.docs_directory} not found. Creating sample documents.")
            self._create_sample_documents()
        
        try:
            # Load PDF files
            pdf_loader = DirectoryLoader(
                self.docs_directory,
                glob="**/*.pdf",
                loader_cls=PyPDFLoader
            )
            documents.extend(pdf_loader.load())
            
            # Load text files
            txt_loader = DirectoryLoader(
                self.docs_directory,
                glob="**/*.txt",
                loader_cls=TextLoader
            )
            documents.extend(txt_loader.load())
            
            logger.info(f"Loaded {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Error loading documents: {e}")
            documents = self._get_sample_documents()
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        splits = text_splitter.split_documents(documents)
        logger.info(f"Split into {len(splits)} chunks")
        
        # Create vector store
        vector_store = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=settings.CHROMA_PERSIST_DIRECTORY
        )
        
        vector_store.persist()
        logger.info("Vector store created and persisted")
        
        return vector_store
    
    def _create_sample_documents(self):
        """Create sample documentation for demo purposes"""
        docs_path = Path(self.docs_directory)
        docs_path.mkdir(parents=True, exist_ok=True)
        
        sample_content = """
# Logistics Operations Manual

## Shipment Handling Procedures

### Standard Shipping
- Packages under 25kg can be shipped via standard ground service
- Estimated delivery time: 3-5 business days
- Cost: $10 base + $2.50 per kg

### Express Shipping
- Available for urgent deliveries
- Packages delivered within 1-2 business days
- Cost: $25 base + $5 per kg

### International Shipping
- Requires customs documentation
- Estimated delivery: 7-14 business days
- Additional fees apply based on destination

## Warehouse Operations

### Safety Procedures
1. Always wear safety equipment in warehouse areas
2. Follow proper lifting techniques for packages over 10kg
3. Report any damaged items immediately

### Storage Guidelines
- Fragile items must be marked clearly
- Hazardous materials require special storage
- Maximum stack height: 3 meters

## Customer Service

### Tracking Issues
If a customer cannot track their shipment:
1. Verify tracking number format
2. Check system for status updates
3. Contact warehouse if no updates for 48+ hours

### Damaged Packages
1. Document damage with photos
2. File insurance claim within 24 hours
3. Arrange replacement shipment

### Delivery Delays
Common causes:
- Weather conditions
- Traffic and road closures
- Customs clearance (international)
- Address verification issues

## Emergency Procedures

### Lost Shipments
1. Search warehouse and transit records
2. Contact last known location
3. File incident report
4. Initiate investigation within 48 hours

### Hazardous Spills
1. Evacuate immediate area
2. Contact emergency services
3. Follow Material Safety Data Sheet protocols
"""
        
        with open(docs_path / "operations_manual.txt", "w") as f:
            f.write(sample_content)
        
        logger.info("Created sample documentation")
    
    def _get_sample_documents(self) -> List:
        """Get sample documents if loading fails"""
        from langchain.schema import Document
        
        return [
            Document(
                page_content="""Shipping Policy: Standard shipments take 3-5 business days. 
                Express shipping available for 1-2 day delivery. International shipments require 
                7-14 business days and customs documentation.""",
                metadata={"source": "shipping_policy"}
            ),
            Document(
                page_content="""Warehouse Safety: Always wear protective equipment. 
                Use proper lifting techniques for heavy packages. Report damaged items immediately.""",
                metadata={"source": "safety_manual"}
            )
        ]
    
    async def search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Search documentation and generate answer
        
        Args:
            query: User's search query
            top_k: Number of relevant documents to retrieve
            
        Returns:
            Dictionary with answer and source documents
        """
        try:
            # Perform similarity search
            docs = self.vector_store.similarity_search(query, k=top_k)
            
            # Generate answer using QA chain
            result = await self.qa_chain.ainvoke({"query": query})
            
            # Format response
            return {
                "query": query,
                "answer": result["result"],
                "results": [
                    {
                        "content": doc.page_content,
                        "source": doc.metadata.get("source", "unknown"),
                        "page": doc.metadata.get("page", None)
                    }
                    for doc in result["source_documents"]
                ]
            }
            
        except Exception as e:
            logger.error(f"Error in search: {e}", exc_info=True)
            return {
                "query": query,
                "answer": "I apologize, but I encountered an error searching the documentation.",
                "results": [],
                "error": str(e)
            }
    
    async def simple_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Simple semantic search without answer generation
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of relevant document chunks
        """
        try:
            docs = self.vector_store.similarity_search(query, k=top_k)
            
            return [
                {
                    "content": doc.page_content,
                    "source": doc.metadata.get("source", "unknown"),
                    "relevance_score": None  # Chroma doesn't return scores by default
                }
                for doc in docs
            ]
            
        except Exception as e:
            logger.error(f"Error in simple search: {e}")
            return []
    
    def add_documents(self, texts: List[str], metadatas: List[Dict] = None):
        """
        Add new documents to the vector store
        
        Args:
            texts: List of text content to add
            metadatas: Optional metadata for each document
        """
        try:
            from langchain.schema import Document
            
            documents = [
                Document(page_content=text, metadata=meta or {})
                for text, meta in zip(texts, metadatas or [{}] * len(texts))
            ]
            
            self.vector_store.add_documents(documents)
            self.vector_store.persist()
            
            logger.info(f"Added {len(documents)} documents to vector store")
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")


# Global RAG instance
_rag_instance = None


def get_rag_system() -> LogisticsRAG:
    """
    Get or create RAG system instance (singleton pattern)
    """
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = LogisticsRAG()
    return _rag_instance
