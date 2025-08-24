import os
from openai import OpenAI
from license_compatibility_checker import LicenseCompatibilityChecker
from license_rag import LicenseRAG
import json
from typing import Dict, Tuple
from dotenv import load_dotenv

class LicenseCompatibilityLLM:
    def __init__(self):
        # Load environment variables
        load_dotenv(override=True)
        
        # Get OpenAI API key
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        # Initialize license compatibility checker
        self.checker = LicenseCompatibilityChecker()
        
        # Initialize RAG system
        self.rag = LicenseRAG()
        self.initialize_rag()
    
    def initialize_rag(self):
        """Initialize the RAG system by building or loading the vector database"""
        # paths relative to this file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        vector_db_path = os.path.join(base_dir, "data", "vector_db")
        if os.path.exists(vector_db_path):
            try:
                self.rag.load_vector_database(vector_db_path)
            except Exception:
                # Fallback to rebuild if loading fails (e.g., version mismatch/corruption)
                self.rag.build_vector_database()
                self.rag.save_vector_database(vector_db_path)
        else:
            self.rag.build_vector_database()
            self.rag.save_vector_database(vector_db_path)

    def extract_packages(self, query: str) -> Tuple[str, str]:
        """Use GPT-4 to extract package names from the query"""
        prompt = f"""
        You are a helpful assistant that extracts package names from queries.
        Extract the names of two Python packages from the following query. 
        Return only a JSON object with two fields: 'package1' and 'package2'.
        If you can't identify two packages, return null for both fields.
        
        Query: {query}
        
        Example response format:
        {{
            "package1": "requests",
            "package2": "urllib3"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            result_text = response.choices[0].message.content
            # Extract the JSON response
            result = json.loads(result_text)
            return result.get("package1"), result.get("package2")
            
        except Exception as e:
            print(f"Error extracting packages: {e}")
            return None, None

    def generate_response(self, query: str, compatibility_result: Dict) -> str:
        """Use RAG system to generate a natural language response about compatibility"""
        # Format the compatibility result for the RAG query
        result_str = json.dumps(compatibility_result, indent=2)
        
        # Extract license information correctly from the structure
        license1_info = None
        license2_info = None
        
        if compatibility_result.get('package1') and compatibility_result['package1'].get('licenses') and len(compatibility_result['package1']['licenses']) > 0:
            license1_info = compatibility_result['package1']['licenses'][0]
        
        if compatibility_result.get('package2') and compatibility_result['package2'].get('licenses') and len(compatibility_result['package2']['licenses']) > 0:
            license2_info = compatibility_result['package2']['licenses'][0]
        
        # Get license names and spdx_ids
        license1_name = license1_info.get('name', 'Unknown') if license1_info else 'Unknown'
        license1_spdx = license1_info.get('spdx_id', 'Unknown') if license1_info else 'Unknown'
        license2_name = license2_info.get('name', 'Unknown') if license2_info else 'Unknown'
        license2_spdx = license2_info.get('spdx_id', 'Unknown') if license2_info else 'Unknown'
        
        # Create a query for the RAG system
        rag_query = f"""
        I need information about license compatibility between the following licenses:
        
        License 1: {license1_name} ({license1_spdx})
        License 2: {license2_name} ({license2_spdx})
        
        Are these licenses compatible? What are the key considerations for their compatibility?
        """
        
        try:
            # Use the RAG system to get a response
            print("--------------WWWWWWWWWWWWWWWWWWW ", rag_query)
            rag_response = self.rag.query_rag(rag_query)
            print("--------------WWWWWWWWWWWWWWWWWWW ", rag_response)
            # Create a final prompt that includes the RAG information
            p1 = compatibility_result.get('package1') or {}
            p2 = compatibility_result.get('package2') or {}
            final_prompt = f"""
            Based on the following compatibility check results and the retrieved license information, provide a clear and concise response to the original query.
            
            Original Query: {query}
            
            Package 1: {p1.get('name', 'Unknown')} with license {license1_name} ({license1_spdx})
            Package 2: {p2.get('name', 'Unknown')} with license {license2_name} ({license2_spdx})
            
            Compatibility Results: {json.dumps(compatibility_result.get('compatibility_results', []), indent=2)}
            Overall Compatible: {compatibility_result.get('overall_compatible', False)}
            
            License Information from RAG system: {rag_response}
            
            Provide a response that:
            1. Directly answers the compatibility question
            2. Explains which licenses are involved
            3. Provides context about why they are/aren't compatible
            4. Suggests alternatives if they're not compatible
            """
            
            # Get final response from LLM
            response = self.client.chat.completions.create(
                model="gpt-4.1",
                messages=[{"role": "user", "content": final_prompt}],
                temperature=0.1
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Sorry, I encountered an error while generating the response."

    def process_query(self, query: str) -> str:
        """Process a natural language query about package compatibility"""
        # Extract package names
        package1, package2 = self.extract_packages(query)
        
        if not package1 or not package2:
            return "I couldn't identify two packages in your query. Please specify two packages to check their compatibility."
        
        # Check compatibility
        compatibility_result = self.checker.check_packages_compatibility(package1, package2)
        print("compatibility_result", compatibility_result)
        
        # Generate response
        response = self.generate_response(query, compatibility_result)
        
        return response

def main():
    llm = LicenseCompatibilityLLM()
    
    # Example usage
    query = "Are roman-numerals-py and asyncssh compatible?"
    
    print(f"\nProcessing query: {query}")
    response = llm.process_query(query)
    
    print("\nResponse:")
    print(response)
    
    # Close the Neo4j connection
    llm.checker.close()

if __name__ == "__main__":
    main() 