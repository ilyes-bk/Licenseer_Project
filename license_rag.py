import os
import json
import glob
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.schema.document import Document
from langchain_community.vectorstores import FAISS
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import EmbeddingsFilter
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA

class LicenseRAG:
    def __init__(self):
        # Load environment variables
        load_dotenv(override=True)
        
        # Set OpenAI API key
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings()
        
        # Set robust data paths relative to this file's directory
        self.base_dir = Path(__file__).resolve().parent
        self.licenses_path = str(self.base_dir / "data" / "licenses")
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=50,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Initialize vector database
        self.vector_db = None
    
    def load_license_files(self) -> List[Dict[str, Any]]:
        """Load all license JSON files from the licenses directory"""
        licenses = []
        license_files = glob.glob(os.path.join(self.licenses_path, "*.json"))
        
        for file_path in license_files:
            if os.path.basename(file_path) == "summary.json":
                continue  # Skip the summary file
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    license_data = json.load(f)
                    licenses.append(license_data)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        print(f"Loaded {len(licenses)} license files")
        return licenses
    
    def create_documents(self, licenses: List[Dict[str, Any]]) -> List[Document]:
        """Convert license data to Langchain Document objects"""
        documents = []
        
        for license_data in licenses:
            # Get license content
            content = license_data.get("content", "")
            
            # Create metadata
            metadata = {
                "name": license_data.get("basic_info", {}).get("name", "Unknown"),
                "spdx_id": license_data.get("basic_info", {}).get("spdx_id", "Unknown"),
                "category": license_data.get("basic_info", {}).get("category", "Unknown"),
                "url": license_data.get("basic_info", {}).get("url", ""),
                "version": license_data.get("metadata", {}).get("version", ""),
                "submitted": license_data.get("metadata", {}).get("submitted", ""),
                "approved": license_data.get("metadata", {}).get("approved", "")
            }
            
            # Split content into chunks
            text_chunks = self.text_splitter.split_text(content)
            
            # Create Document objects for each chunk
            for i, chunk in enumerate(text_chunks):
                doc_metadata = metadata.copy()
                doc_metadata["chunk_id"] = i
                doc_metadata["total_chunks"] = len(text_chunks)
                
                documents.append(Document(page_content=chunk, metadata=doc_metadata))
        
        print(f"Created {len(documents)} document chunks")
        return documents
    
    def build_vector_database(self) -> None:
        """Build the vector database from license documents"""
        # Load license data
        licenses = self.load_license_files()

        if not licenses:
            raise ValueError(f"No license JSON files found under {self.licenses_path}. Ensure the dataset is present.")
        
        # Create documents
        documents = self.create_documents(licenses)
        
        # Create vector store
        self.vector_db = FAISS.from_documents(documents, self.embeddings)
        print("Vector database created successfully")
    
    def save_vector_database(self, path: str = None) -> None:
        """Save the vector database to disk"""
        if path is None:
            path = str(self.base_dir / "data" / "vector_db")
        if self.vector_db:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            self.vector_db.save_local(path)
            print(f"Vector database saved to {path}")
        else:
            print("No vector database to save")
    
    def load_vector_database(self, path: str = None) -> None:
        """Load the vector database from disk"""
        if path is None:
            path = str(self.base_dir / "data" / "vector_db")
        if os.path.exists(path):
            self.vector_db = FAISS.load_local(path, self.embeddings, allow_dangerous_deserialization=True)
            print(f"Vector database loaded from {path}")
        else:
            print(f"No vector database found at {path}")
    
    def get_retriever(self, k: int = 10):
        """Get a retriever from the vector database with filtering"""
        if not self.vector_db:
            raise ValueError("Vector database not initialized")
        
        # Create base retriever
        retriever = self.vector_db.as_retriever(search_kwargs={"k": k})
        
        # Add embedding filter for better results
        embeddings_filter = EmbeddingsFilter(embeddings=self.embeddings, similarity_threshold=0.7)
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=embeddings_filter,
            base_retriever=retriever
        )
        
        return compression_retriever
    
    def query_rag(self, query: str, k: int = 4) -> Dict[str, Any]:
        """Query the RAG system and return relevant documents and their metadata"""
        if not self.vector_db:
            raise ValueError("Vector database not initialized. Call build_vector_database() first.")
        
        try:
            # Get retriever
            retriever = self.get_retriever(k=k)
            
            # Retrieve relevant documents
            docs = retriever.get_relevant_documents(query)
            
            # Extract results
            results = []
            for doc in docs:
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })
            
            return {
                "query": query,
                "results": results,
                "has_results": len(results) > 0,
                "result_count": len(results)
            }
            
        except Exception as e:
            print(f"Error querying RAG system: {e}")
            return {
                "query": query,
                "results": [],
                "has_results": False,
                "result_count": 0,
                "error": str(e)
            }
    
    def query_with_llm(self, query: str) -> str:
        """Use LLM to generate a response based on retrieved documents"""
        if not self.vector_db:
            raise ValueError("Vector database not initialized. Call build_vector_database() first.")
        
        # Initialize the LLM
        llm = ChatOpenAI(temperature=0, model="gpt-4.1")
        
        # Create a retrieval QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.get_retriever(),
            return_source_documents=True
        )
        
        # Run the chain
        response = qa_chain({"query": query})
        
        return response


def main():
    # Initialize the RAG system
    rag = LicenseRAG()
    
    # Build or load the vector database
    vector_db_path = "data/vector_db"
    if os.path.exists(vector_db_path):
        rag.load_vector_database(vector_db_path)
    else:
        rag.build_vector_database()
        rag.save_vector_database(vector_db_path)
    
    # Example query
    query = "What are the key requirements of the UCL-1.0 license?"
    
    # Get results
    results = rag.query_rag(query)
    
    # Print results
    print(f"\nQuery: {results['query']}")
    print("\nRelevant License Information:")
    for i, result in enumerate(results['results']):
        print(f"\n--- Result {i+1} ---")
        print(f"License: {result['metadata']['name']} ({result['metadata']['spdx_id']})")
        print(f"Content: {result['content'][:300]}...")
    
    # Get LLM response
    llm_response = rag.query_with_llm(query)
    print("\nLLM Response:")
    print(llm_response['result'])
    print("\nSources:")
    for i, doc in enumerate(llm_response['source_documents']):
        print(f"\nSource {i+1}: {doc.metadata['name']} ({doc.metadata['spdx_id']})")


if __name__ == "__main__":
    main() 