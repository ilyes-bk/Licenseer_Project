import time
from neo4j import GraphDatabase

# Wait for 60 seconds (as instructed)
print("Waiting for 60 seconds before connecting to Neo4j...")


# Connection details
NEO4J_URI = "neo4j+s://03761ccd.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "GV5_25MFoAuxzDcyDQUdSPDzeVsArIvHkN-tLDLfMzk"

# Connect to Neo4j
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

# Run a test query
def test_connection():
    with driver.session() as session:
        result = session.run("RETURN 'Connection successful!' AS message")
        for record in result:
            print(record["message"])

if __name__ == "__main__":
    try:
        test_connection()
    finally:
        driver.close()
