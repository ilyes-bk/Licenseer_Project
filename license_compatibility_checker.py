import pandas as pd
from neo4j import GraphDatabase
import time
import ssl
import certifi
import json
import os
from dotenv import load_dotenv
from typing import Dict, List, Tuple

class LicenseCompatibilityChecker:
    def __init__(self):
        # Load environment variables if available
        load_dotenv(override=True)

        # Neo4j connection details (prefer environment variables; fall back to existing defaults)
        self.uri = os.getenv("NEO4J_URI", "neo4j://03761ccd.databases.neo4j.io")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "GV5_25MFoAuxzDcyDQUdSPDzeVsArIvHkN-tLDLfMzk")
        self.database = os.getenv("NEO4J_DATABASE", "neo4j")
        
        # SSL configuration
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        
        # Initialize Neo4j driver
        driver_kwargs = {
            "auth": (self.user, self.password),
            "max_connection_lifetime": 30,
            "max_connection_pool_size": 50,
            "connection_timeout": 30,
        }
        # For plain 'bolt://' or 'neo4j://' URIs only, allow custom SSL context
        if self.uri.startswith("neo4j://") or self.uri.startswith("bolt://"):
            driver_kwargs["ssl_context"] = self.ssl_context

        self.driver = GraphDatabase.driver(self.uri, **driver_kwargs)

    def close(self):
        """Close the Neo4j driver connection"""
        if self.driver:
            self.driver.close()

    def get_package_info(self, package_name: str) -> Dict:
        """Get package information and its licenses"""
        query = """
        MATCH (p:Package {name: $package_name})
        OPTIONAL MATCH (p)-[:USES_LICENSE]->(l:License)
        RETURN p, collect(l) as licenses
        """
        
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, {"package_name": package_name})
                record = result.single()
                if record:
                    package = record["p"]
                    licenses = record["licenses"]
                    return {
                        "name": package["name"],
                        "description": package.get("description"),
                        "homepage": package.get("homepage"),
                        "language": package.get("language"),
                        "latest_release": package.get("latest_release"),
                        "latest_release_date": package.get("latest_release_date"),
                        "dependent_repos": package.get("dependent_repos"),
                        "dependents_count": package.get("dependents_count"),
                        "keywords": package.get("keywords", []),
                        "repository_url": package.get("repository_url"),
                        "package_manager_url": package.get("package_manager_url"),
                        "licenses": [{
                            "spdx_id": l["spdx_id"],
                            "name": l["name"],
                            "category": l["category"],
                            "version": l.get("version"),
                            "submitter": l.get("submitter"),
                            "steward": l.get("steward"),
                            "steward_url": l.get("steward_url")
                        } for l in licenses]
                    }
                return None
        except Exception as e:
            print(f"Error getting package info for {package_name}: {e}")
            return None

    def check_license_compatibility(self, license1: str, license2: str) -> bool:
        """Check if two licenses are compatible"""
        query = """
        MATCH (l1:License {spdx_id: $license1})-[r:IS_COMPATIBLE_WITH]->(l2:License {spdx_id: $license2})
        RETURN r.is_compatible as is_compatible
        """
        
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, {
                    "license1": license1,
                    "license2": license2
                })
                record = result.single()
                return record["is_compatible"] if record else False
        except Exception as e:
            print(f"Error checking compatibility between {license1} and {license2}: {e}")
            return False

    def check_packages_compatibility(self, package1: str, package2: str) -> Dict:
        """Check compatibility between two packages based on their licenses"""
        # Get package information
        p1_info = self.get_package_info(package1)
        p2_info = self.get_package_info(package2)
        
        if not p1_info or not p2_info:
            return {
                "error": "One or both packages not found",
                "package1": p1_info,
                "package2": p2_info
            }
        
        # Check compatibility between all license pairs
        compatibility_results = []
        for l1 in p1_info["licenses"]:
            for l2 in p2_info["licenses"]:
                is_compatible = self.check_license_compatibility(l1["spdx_id"], l2["spdx_id"])
                compatibility_results.append({
                    "license1": l1["spdx_id"],
                    "license2": l2["spdx_id"],
                    "is_compatible": is_compatible
                })
        
        # Determine overall compatibility
        overall_compatible = any(r["is_compatible"] for r in compatibility_results)
        
        return {
            "package1": p1_info,
            "package2": p2_info,
            "compatibility_results": compatibility_results,
            "overall_compatible": overall_compatible
        }

def main():
    checker = LicenseCompatibilityChecker()
    
    # Example usage
    package1 = "requests"
    package2 = "urllib3"
    
    print(f"\nChecking compatibility between {package1} and {package2}...")
    result = checker.check_packages_compatibility(package1, package2)
    
    # Print results in a readable format
    print("\nResults:")
    print(json.dumps(result, indent=2))
    
    checker.close()

if __name__ == "__main__":
    main() 