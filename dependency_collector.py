import requests
import pandas as pd
import json
from pathlib import Path
import time
import os

class DependencyCollector:
    def __init__(self):
        self.api_key = "59bd1ecaf14a8080edbaaeb935d2288e"
        self.base_url = "https://libraries.io/api/Pypi"
        self.dependencies_dir = Path("data/dependencies")
        self.dependencies_dir.mkdir(parents=True, exist_ok=True)
        
        # Fields to extract from the API response
        self.fields_to_extract = [
            'code_of_conduct_url',
            'contribution_guidelines_url',
            'dependent_repos_count',
            'dependents_count',
            'deprecation_reason',
            'description',
            'homepage',
            'keywords',
            'language',
            'latest_release_number',
            'latest_release_published_at',
            'latest_stable_release_number',
            'latest_stable_release_published_at',
            'license_normalized',
            'licenses',
            'name',
            'normalized_licenses',
            'package_manager_url',
            'repository_license',
            'platform',
            'repository_status',
            'repository_url',
            'security_policy_url'
        ]

    def get_dependency_info(self, package_name):
        """Get dependency information for a specific package"""
        url = f"{self.base_url}/{package_name}/latest/dependencies"
        
        try:
            response = requests.get(url, params={"api_key": self.api_key})
            response.raise_for_status()
            
            data = response.json()
            
            # Extract only the fields we want
            extracted_data = {field: data.get(field, None) for field in self.fields_to_extract}
            
            return extracted_data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {package_name}: {e}")
            return None

    def save_dependency_info(self, package_name, data):
        """Save dependency information to a JSON file"""
        if not data:
            return

        filename = self.dependencies_dir / f"{package_name}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def process_dataset(self, csv_path):
        """Process the dataset CSV file and collect dependency information"""
        try:
            # Read the CSV file
            df = pd.read_csv(csv_path)
            df = df[0:1500]
            # Create a summary file
            summary = {
                "total_packages": len(df),
                "processed_packages": 0,
                "failed_packages": 0,
                "packages": []
            }
            
            print(f"Found {len(df)} packages. Starting collection...")
            
            for index, row in df.iterrows():
                package_name = row['project']
                print(f"\nProcessing {package_name} ({index + 1}/{len(df)})...")
                
                # Get dependency information
                dependency_info = self.get_dependency_info(package_name)
                
                if dependency_info:
                    # Save to file
                    self.save_dependency_info(package_name, dependency_info)
                    print(f"Saved {package_name}.json")
                    
                    # Add to summary
                    summary["packages"].append({
                        "name": package_name,
                        "download_count": row['download_count'],
                        "status": "success"
                    })
                    summary["processed_packages"] += 1
                else:
                    print(f"Failed to get dependency information for {package_name}")
                    summary["packages"].append({
                        "name": package_name,
                        "download_count": row['download_count'],
                        "status": "failed"
                    })
                    summary["failed_packages"] += 1
                
                # Add a small delay to avoid rate limiting
                time.sleep(1.5)
            
            # Save summary file
            with open(self.dependencies_dir / "summary.json", "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=4, ensure_ascii=False)
            print("\nSaved summary.json with collection results")
            
        except Exception as e:
            print(f"Error processing dataset: {e}")

def main():
    collector = DependencyCollector()
    # Replace with your CSV file path
    csv_path = r"C:\Users\Ilyesbk\Work\PFE_Licenseer\src\top-pypi-packages.csv"
    collector.process_dataset(csv_path)
    print("\nDependency collection complete!")

if __name__ == "__main__":
    main() 