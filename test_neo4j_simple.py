import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_direct_connection():
    """Test a direct connection to Neo4j without any of our custom code"""
    # Load environment variables
    load_dotenv()
    
    # Get credentials directly
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    
    # Remove quotes if present
    if uri and uri.startswith('"') and uri.endswith('"'):
        uri = uri[1:-1]
    
    logger.info(f"Testing direct connection to Neo4j: {uri}")
    
    try:
        # Create a simple driver
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # Test the connection
        with driver.session() as session:
            result = session.run("RETURN 'Connection successful!' as message")
            message = result.single()["message"]
            logger.info(message)
        
        # Close the driver
        driver.close()
        return True
    
    except Exception as e:
        logger.error(f"Connection failed: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    test_direct_connection() 