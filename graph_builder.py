import os
from pathlib import Path
import json
from neo4j import GraphDatabase
import pandas as pd
import time
from neo4j.exceptions import ServiceUnavailable
import ssl
import certifi
from dotenv import load_dotenv

class GraphBuilder:
    def __init__(self):
        # Load environment variables
        load_dotenv(override=True)
        
        # Neo4j connection details (prefer environment variables)
        self.uri = os.getenv("NEO4J_URI", "neo4j://bd3b0481.databases.neo4j.io")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "U1F41LwSpgTLohHhgUXsBH9yEyD_bGFL3-TmRBXdCJE")
        self.database = os.getenv("NEO4J_DATABASE", "neo4j")
        
        # SSL configuration
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        
        # Initialize Neo4j driver with connection timeout
        self.driver = GraphDatabase.driver(
            self.uri,
            auth=(self.user, self.password),
            max_connection_lifetime=30,
            max_connection_pool_size=50,
            connection_timeout=30,
            ssl_context=self.ssl_context
        )
        
        # Data directories
        self.dependencies_dir = Path("data/dependencies")
        self.licenses_dir = Path("data/licenses")

    def test_connection(self, max_retries=3):
        """Test the Neo4j connection with retry logic"""
        for attempt in range(max_retries):
            try:
                with self.driver.session(database=self.database) as session:
                    result = session.run("RETURN 1 as test")
                    if result.single()["test"] == 1:
                        return True
            except Exception as e:
                print(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    print("Retrying in 5 seconds...")
                    time.sleep(5)
                else:
                    print("All connection attempts failed")
                    return False
        return False

    def close(self):
        """Close the Neo4j driver connection"""
        if self.driver:
            self.driver.close()

    def create_constraints(self):
        """Create unique constraints for nodes"""
        try:
            with self.driver.session(database=self.database) as session:
                # Create constraints for Package nodes
                session.run("CREATE CONSTRAINT package_name IF NOT EXISTS FOR (p:Package) REQUIRE p.name IS UNIQUE")
                # Create constraints for License nodes
                session.run("CREATE CONSTRAINT license_spdx IF NOT EXISTS FOR (l:License) REQUIRE l.spdx_id IS UNIQUE")
                print("Constraints created successfully")
                print(f"Connected to Neo4j: {self.uri}")
                print(f"Database: {self.database}")
        except Exception as e:
            print(f"Error creating constraints: {e}")
            raise

    def create_package_node(self, package_data):
        """Create a Package node with its properties"""
        query = """
        MERGE (p:Package {name: $name})
        SET p.description = $description,
            p.homepage = $homepage,
            p.language = $language,
            p.latest_release = $latest_release,
            p.latest_release_date = $latest_release_date,
            p.dependent_repos = $dependent_repos,
            p.dependents_count = $dependents_count,
            p.keywords = $keywords,
            p.repository_url = $repository_url,
            p.package_manager_url = $package_manager_url
        """
        
        try:
            with self.driver.session(database=self.database) as session:
                session.run(query, {
                    "name": package_data["name"],
                    "description": package_data.get("description"),
                    "homepage": package_data.get("homepage"),
                    "language": package_data.get("language"),
                    "latest_release": package_data.get("latest_release_number"),
                    "latest_release_date": package_data.get("latest_release_published_at"),
                    "dependent_repos": package_data.get("dependent_repos_count"),
                    "dependents_count": package_data.get("dependents_count"),
                    "keywords": package_data.get("keywords", []),
                    "repository_url": package_data.get("repository_url"),
                    "package_manager_url": package_data.get("package_manager_url")
                })
        except Exception as e:
            print(f"Error creating package node for {package_data['name']}: {e}")
            raise

    def create_license_node(self, license_data):
        """Create a License node with its properties"""
        query = """
        MERGE (l:License {spdx_id: $spdx_id})
        SET l.name = $name,
            l.category = $category,
            l.version = $version,
            l.submitter = $submitter,
            l.steward = $steward,
            l.steward_url = $steward_url,
            l.content = $content
        """
        
        try:
            with self.driver.session(database=self.database) as session:
                session.run(query, {
                    "spdx_id": license_data["basic_info"]["spdx_id"],
                    "name": license_data["basic_info"]["name"],
                    "category": license_data["basic_info"]["category"],
                    "version": license_data["metadata"].get("version"),
                    "submitter": license_data["metadata"].get("submitter"),
                    "steward": license_data["metadata"].get("steward"),
                    "steward_url": license_data["metadata"].get("steward_url"),
                    "content": license_data["content"]
                })
        except Exception as e:
            print(f"Error creating license node for {license_data['basic_info']['spdx_id']}: {e}")
            raise

    def create_license_relationship(self, package_name, license_spdx):
        """Create a relationship between a Package and its License"""
        query = """
        MATCH (p:Package {name: $package_name})
        MATCH (l:License {spdx_id: $license_spdx})
        MERGE (p)-[:USES_LICENSE]->(l)
        """
        
        try:
            with self.driver.session(database=self.database) as session:
                session.run(query, {
                    "package_name": package_name,
                    "license_spdx": license_spdx
                })
        except Exception as e:
            print(f"Error creating relationship between {package_name} and {license_spdx}: {e}")
            raise

    def build_graph(self):
        """Build the complete graph from the collected data"""
        try:
            # Test connection first
            print("Testing Neo4j connection...")
            if not self.test_connection():
                print("Failed to connect to Neo4j. Please check your connection details.")
                return
            
            print("Connection successful!")
            
            # Create constraints
            self.create_constraints()
            
            # Process license files
            print("\nProcessing license files...")
            for license_file in self.licenses_dir.glob("*.json"):
                if license_file.name == "summary.json":
                    continue
                    
                with open(license_file, "r", encoding="utf-8") as f:
                    license_data = json.load(f)
                    self.create_license_node(license_data)
                    print(f"Processed license: {license_data['basic_info']['spdx_id']}")
                    time.sleep(0.1)  # Small delay to avoid overwhelming the database
            
            # Process dependency files
            print("\nProcessing dependency files...")
            for dep_file in self.dependencies_dir.glob("*.json"):
                if dep_file.name == "summary.json":
                    continue
                    
                with open(dep_file, "r", encoding="utf-8") as f:
                    package_data = json.load(f)
                    
                    # Create package node
                    self.create_package_node(package_data)
                    
                    # Create license relationships
                    if package_data.get("normalized_licenses"):
                        for license_spdx in package_data["normalized_licenses"]:
                            self.create_license_relationship(package_data["name"], license_spdx)
                    
                    print(f"Processed package: {package_data['name']}")
                    time.sleep(0.1)  # Small delay to avoid overwhelming the database
            
            print("\nGraph construction complete!")
            
        except Exception as e:
            print(f"Error building graph: {e}")
        finally:
            self.close()

def main():
    builder = GraphBuilder()
    builder.build_graph()

if __name__ == "__main__":
    main() 