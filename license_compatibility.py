import pandas as pd
from neo4j import GraphDatabase
import time
import ssl
import os
import certifi

class LicenseCompatibilityBuilder:
    def __init__(self):
        # Neo4j connection details
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD")
        
        if not self.uri or not self.password:
            raise ValueError("NEO4J_URI and NEO4J_PASSWORD must be set in environment variables")
        
        # SSL configuration
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        
        # Initialize Neo4j driver
        self.driver = GraphDatabase.driver(
            self.uri,
            auth=(self.user, self.password),
            max_connection_lifetime=30,
            max_connection_pool_size=50,
            connection_timeout=30,
            ssl_context=self.ssl_context
        )

    def close(self):
        """Close the Neo4j driver connection"""
        if self.driver:
            self.driver.close()

    def create_compatibility_constraint(self):
        """Create a constraint for the compatibility relationship"""
        try:
            with self.driver.session() as session:
                session.run("""
                    CREATE CONSTRAINT compatibility_unique IF NOT EXISTS 
                    FOR ()-[r:IS_COMPATIBLE_WITH]-() 
                    REQUIRE r.id IS UNIQUE
                """)
                print("Compatibility constraint created successfully")
        except Exception as e:
            print(f"Error creating compatibility constraint: {e}")
            raise

    def create_compatibility_relationship(self, source_license, target_license, is_compatible):
        """Create a compatibility relationship between two licenses"""
        query = """
        MATCH (l1:License {spdx_id: $source_license})
        MATCH (l2:License {spdx_id: $target_license})
        MERGE (l1)-[r:IS_COMPATIBLE_WITH {id: $relationship_id}]->(l2)
        SET r.is_compatible = $is_compatible
        """
        
        try:
            with self.driver.session() as session:
                session.run(query, {
                    "source_license": source_license,
                    "target_license": target_license,
                    "relationship_id": f"{source_license}_{target_license}",
                    "is_compatible": is_compatible
                })
        except Exception as e:
            print(f"Error creating compatibility relationship between {source_license} and {target_license}: {e}")
            raise

    def process_compatibility_matrix(self, matrix_file):
        """Process the compatibility matrix and create relationships"""
        try:
            # Read the matrix CSV file
            df = pd.read_csv(matrix_file)
            
            # Get the license IDs (first column)
            license_ids = df.iloc[:, 0].tolist()
            
            # Create compatibility constraint
            self.create_compatibility_constraint()
            
            # Process each row in the matrix
            total_relationships = len(license_ids) * len(license_ids)
            processed = 0
            
            print(f"Processing {total_relationships} potential compatibility relationships...")
            
            for i, source_license in enumerate(license_ids):
                for j, target_license in enumerate(license_ids):
                    # Skip self-compatibility
                    if i == j:
                        continue
                    
                    # Get compatibility value
                    compatibility_value = df.iloc[i, j+1]
                    
                    # Convert compatibility value to boolean
                    is_compatible = False
                    if compatibility_value == "Yes":
                        is_compatible = True
                    elif compatibility_value == "Unknown":
                        is_compatible = False  # Set unknown to False as requested
                    
                    # Create the relationship
                    self.create_compatibility_relationship(source_license, target_license, is_compatible)
                    
                    processed += 1
                    if processed % 100 == 0:
                        print(f"Processed {processed}/{total_relationships} relationships")
                    
                    # Small delay to avoid overwhelming the database
                    time.sleep(0.01)
            
            print("\nCompatibility relationships creation complete!")
            
        except Exception as e:
            print(f"Error processing compatibility matrix: {e}")
        finally:
            self.close()

def main():
    builder = LicenseCompatibilityBuilder()
    matrix_file = r"C:\Users\Ilyesbk\Work\PFE_Licenseer\PFE_Licenseer\data\licenses\matrix.csv"
    builder.process_compatibility_matrix(matrix_file)

if __name__ == "__main__":
    main() 