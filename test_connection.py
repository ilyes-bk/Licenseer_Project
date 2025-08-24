import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_connection():
    """Test the Neo4j connection directly"""
    # Load environment variables
    load_dotenv()
    
    # Get credentials directly
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    
    # Remove quotes if present
    if uri and uri.startswith('"') and uri.endswith('"'):
        uri = uri[1:-1]
    if user and user.startswith('"') and user.endswith('"'):
        user = user[1:-1]
    if password and password.startswith('"') and password.endswith('"'):
        password = password[1:-1]
    
    print(f"Testing connection to: {uri}")
    
    try:
        # Create a simple driver
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # Test the connection
        with driver.session() as session:
            result = session.run("RETURN 'Connection successful!' as message")
            message = result.single()["message"]
            print(message)
        
        # Close the driver
        driver.close()
        return True
    
    except Exception as e:
        print(f"Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection() 