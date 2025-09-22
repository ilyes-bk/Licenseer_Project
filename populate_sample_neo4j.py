#!/usr/bin/env python3
"""
Script to populate Neo4j with sample license compatibility data
Creates a simple knowledge graph with dependencies, licenses, and terms
"""

import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
import json

# Load environment variables
load_dotenv()

class Neo4jSamplePopulator:
    def __init__(self):
        self.uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = os.getenv('NEO4J_USER', 'neo4j')
        self.password = os.getenv('NEO4J_PASSWORD', 'password')
        self.database = os.getenv('NEO4J_DATABASE', 'neo4j')
        
        # Initialize driver
        if self.uri.startswith(('bolt://', 'neo4j://')):
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        else:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
    
    def close(self):
        self.driver.close()
    
    def clear_database(self):
        """Clear existing data"""
        with self.driver.session(database=self.database) as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("✅ Cleared existing data")
    
    def create_constraints(self):
        """Create constraints for better performance"""
        with self.driver.session(database=self.database) as session:
            constraints = [
                "CREATE CONSTRAINT license_name IF NOT EXISTS FOR (l:License) REQUIRE l.name IS UNIQUE",
                "CREATE CONSTRAINT dependency_name IF NOT EXISTS FOR (d:Dependency) REQUIRE d.name IS UNIQUE",
                "CREATE CONSTRAINT term_name IF NOT EXISTS FOR (t:Term) REQUIRE t.name IS UNIQUE"
            ]
            
            for constraint in constraints:
                try:
                    session.run(constraint)
                except Exception as e:
                    print(f"Constraint might already exist: {e}")
            
            print("✅ Created constraints")
    
    def create_licenses(self):
        """Create license nodes with terms"""
        with self.driver.session(database=self.database) as session:
            licenses_data = [
                {
                    'name': 'MIT',
                    'type': 'Permissive',
                    'description': 'MIT License - Very permissive',
                    'terms': [
                        {'name': 'Permissive', 'description': 'Allows commercial use'},
                        {'name': 'No Copyleft', 'description': 'No derivative work restrictions'},
                        {'name': 'Commercial Use OK', 'description': 'Can be used in commercial projects'}
                    ]
                },
                {
                    'name': 'GPL-3.0',
                    'type': 'Copyleft',
                    'description': 'GNU General Public License v3.0 - Copyleft',
                    'terms': [
                        {'name': 'Copyleft', 'description': 'Requires derivative works to be open source'},
                        {'name': 'Derivative Works', 'description': 'Must share derivative works under same license'},
                        {'name': 'Commercial Restricted', 'description': 'Commercial use requires open source release'}
                    ]
                }
            ]
            
            for license_data in licenses_data:
                # Create license node
                session.run("""
                    MERGE (l:License {name: $name})
                    SET l.type = $type, l.description = $description
                """, name=license_data['name'], type=license_data['type'], 
                description=license_data['description'])
                
                # Create term nodes and relationships
                for term in license_data['terms']:
                    session.run("""
                        MERGE (t:Term {name: $term_name})
                        SET t.description = $term_description
                        MERGE (l:License {name: $license_name})
                        MERGE (l)-[:HAS_TERM]->(t)
                    """, term_name=term['name'], term_description=term['description'],
                    license_name=license_data['name'])
            
            print("✅ Created licenses and terms")
    
    def create_dependencies(self):
        """Create dependency nodes"""
        with self.driver.session(database=self.database) as session:
            dependencies_data = [
                {'name': 'requests', 'version': '2.31.0', 'license': 'MIT'},
                {'name': 'numpy', 'version': '1.24.3', 'license': 'MIT'},
                {'name': 'pandas', 'version': '1.5.3', 'license': 'MIT'},
                {'name': 'tensorflow', 'version': '2.13.0', 'license': 'GPL-3.0'},
                {'name': 'pytorch', 'version': '2.0.1', 'license': 'GPL-3.0'},
                {'name': 'scikit-learn', 'version': '1.3.0', 'license': 'GPL-3.0'}
            ]
            
            for dep_data in dependencies_data:
                session.run("""
                    MERGE (d:Dependency {name: $name})
                    SET d.version = $version
                    MERGE (l:License {name: $license})
                    MERGE (d)-[:USES_LICENSE]->(l)
                """, name=dep_data['name'], version=dep_data['version'], 
                license=dep_data['license'])
            
            print("✅ Created dependencies")
    
    def create_compatibility_relationships(self):
        """Create compatibility relationships"""
        with self.driver.session(database=self.database) as session:
            # MIT and GPL-3.0 are incompatible
            session.run("""
                MATCH (l1:License {name: 'MIT'})
                MATCH (l2:License {name: 'GPL-3.0'})
                MERGE (l1)-[:INCOMPATIBLE_WITH]->(l2)
                MERGE (l2)-[:INCOMPATIBLE_WITH]->(l1)
            """)
            
            # MIT is compatible with itself
            session.run("""
                MATCH (l:License {name: 'MIT'})
                MERGE (l)-[:COMPATIBLE_WITH]->(l)
            """)
            
            # GPL-3.0 is compatible with itself
            session.run("""
                MATCH (l:License {name: 'GPL-3.0'})
                MERGE (l)-[:COMPATIBLE_WITH]->(l)
            """)
            
            print("✅ Created compatibility relationships")
    
    def create_sample_queries(self):
        """Create some sample queries to test"""
        with self.driver.session(database=self.database) as session:
            # Query 1: Get all licenses with their terms
            result = session.run("""
                MATCH (l:License)-[:HAS_TERM]->(t:Term)
                RETURN l.name as license, l.type as type, 
                       collect(t.name) as terms
                ORDER BY l.name
            """)
            
            print("\n📋 Licenses with their terms:")
            for record in result:
                print(f"  {record['license']} ({record['type']}): {', '.join(record['terms'])}")
            
            # Query 2: Get dependencies and their licenses
            result = session.run("""
                MATCH (d:Dependency)-[:USES_LICENSE]->(l:License)
                RETURN d.name as dependency, d.version as version, 
                       l.name as license, l.type as license_type
                ORDER BY d.name
            """)
            
            print("\n📦 Dependencies and their licenses:")
            for record in result:
                print(f"  {record['dependency']} v{record['version']} -> {record['license']} ({record['license_type']})")
            
            # Query 3: Check compatibility
            result = session.run("""
                MATCH (l1:License)-[r:INCOMPATIBLE_WITH]->(l2:License)
                RETURN l1.name as license1, l2.name as license2
            """)
            
            print("\n❌ Incompatible license pairs:")
            for record in result:
                print(f"  {record['license1']} ❌ {record['license2']}")
    
    def populate_sample_data(self):
        """Main method to populate sample data"""
        print("🚀 Starting Neo4j sample data population...")
        
        try:
            self.clear_database()
            self.create_constraints()
            self.create_licenses()
            self.create_dependencies()
            self.create_compatibility_relationships()
            self.create_sample_queries()
            
            print("\n✅ Sample data population completed!")
            print(f"🌐 Connect to Neo4j Browser at: {self.uri}")
            print("📊 Run these queries in Neo4j Browser:")
            print("   MATCH (n) RETURN n LIMIT 25")
            print("   MATCH (l:License)-[:HAS_TERM]->(t:Term) RETURN l, t")
            print("   MATCH (d:Dependency)-[:USES_LICENSE]->(l:License) RETURN d, l")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.close()

if __name__ == "__main__":
    populator = Neo4jSamplePopulator()
    populator.populate_sample_data()


