import os
from license_rag import LicenseRAG

def test_simple_query():
    # Initialize the RAG system
    rag = LicenseRAG()
    
    # Load or build the vector database
    vector_db_path = "data/vector_db"
    if os.path.exists(vector_db_path):
        rag.load_vector_database(vector_db_path)
    else:
        rag.build_vector_database()
        rag.save_vector_database(vector_db_path)
    
    # Simple test query about a specific license
    query = "What are the main requirements of the UCL-1.0 license?"
    
    # Get raw retrieved documents
    print("\nRetrieving documents for query:", query)
    results = rag.query_rag(query)
    
    # Print first result
    if results["results"]:
        first_result = results["results"][0]
        print(f"\nLicense: {first_result['metadata']['name']} ({first_result['metadata']['spdx_id']})")
        print(f"Content snippet: {first_result['content'][:300]}...")
    else:
        print("No results found.")
    
    # Get LLM-enhanced response
    print("\nGenerating LLM response...")
    llm_response = rag.query_with_llm(query)
    
    # Print response
    print("\nLLM Response:")
    print(llm_response["result"])
    
    # Test license compatibility specific query
    compatibility_query = "Are the 0BSD and EPL-2.0 licenses compatible? What are key considerations for their compatibility?"
    print("\n\nTesting license compatibility query:", compatibility_query)
    
    # Get LLM-enhanced response for compatibility query
    compatibility_response = rag.query_with_llm(compatibility_query)
    
    # Print response
    print("\nCompatibility Response:")
    print(compatibility_response["result"])
    
    # Test with license names from live query
    print("\n\nTesting with actual licenses from the system:")
    live_query = "Are the Zero-Clause BSD (0BSD) and Eclipse Public License version 2.0 (EPL-2.0) licenses compatible?"
    live_response = rag.query_with_llm(live_query)
    print("\nDetailed Compatibility Response:")
    print(live_response["result"])

if __name__ == "__main__":
    test_simple_query() 