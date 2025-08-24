import requests
from bs4 import BeautifulSoup
import os
from pathlib import Path
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class LicenseDownloader:
    def __init__(self):
        self.base_url = "https://opensource.org/licenses"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        # Create licenses directory if it doesn't exist
        self.licenses_dir = Path("data/licenses")
        self.licenses_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Selenium WebDriver
        chrome_options = Options()
        #chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=chrome_options)

    def get_all_licenses(self):
        """Fetch all available licenses from OSI website using Selenium"""
        try:
            self.driver.get(self.base_url)
            # Wait for the table to be present
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="content-scroll"]/tbody'))
            )
            
            # Get all rows from the table
            rows = self.driver.find_elements(By.XPATH, '//*[@id="content-scroll"]/tbody/tr')
            
            licenses = []
            for row in rows:
                try:
                    # Get license name and URL
                    name_element = row.find_element(By.CLASS_NAME, 'license-table--title').find_element(By.TAG_NAME, 'a')
                    name = name_element.text.strip()
                    url = name_element.get_attribute('href')
                    
                    # Get SPDX ID
                    spdx = row.find_element(By.CLASS_NAME, 'license-table--spdx').text.strip()
                    
                    # Get category
                    category_element = row.find_element(By.CLASS_NAME, 'license-table--category')
                    category = category_element.find_element(By.CLASS_NAME, 'term-item').text.strip()
                    
                    licenses.append({
                        'name': name,
                        'url': url,
                        'spdx': spdx,
                        'category': category
                    })
                    print(name, url, spdx, category)
                except Exception as e:
                    print(f"Error processing row: {e}")
                    continue
                    
            return licenses
        except Exception as e:
            print(f"Error fetching licenses: {e}")
            return []
        finally:
            print("Closing driver")

    def scrape_license_content(self, url):
        """Scrape the license content and metadata from the OSI website"""
        try:
            self.driver.get(url)
            # Wait for the content to be present
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'entry-content'))
            )
            
            # Extract metadata
            metadata = {}
            
            # Get category
            try:
                category_element = self.driver.find_element(By.CLASS_NAME, 'pill-taxonomy')
                metadata['category'] = category_element.find_element(By.CLASS_NAME, 'term-item').text.strip()
            except:
                metadata['category'] = "N/A"
            
            # Get license meta information
            try:
                meta_element = self.driver.find_element(By.CLASS_NAME, 'license-meta')
                try:
                    metadata['version'] = meta_element.find_element(By.CLASS_NAME, 'license-version').text.strip()
                except:
                    metadata['version'] = 'N/A'
                try:
                    metadata['submitted'] = meta_element.find_element(By.CLASS_NAME, 'license-release').text.strip()
                except:
                    metadata['submitted'] = 'N/A'
                try:
                    metadata['submitter'] = meta_element.find_element(By.CLASS_NAME, 'license-submitter').text.strip()
                except:
                    metadata['submitter'] = 'N/A'
                try:
                    metadata['approved'] = meta_element.find_element(By.CLASS_NAME, 'license-approved').text.strip()
                except:
                    metadata['approved'] = 'N/A'
                try:
                    metadata['spdx'] = meta_element.find_element(By.CLASS_NAME, 'license-spdx').text.strip()
                except:
                    metadata['spdx'] = 'N/A'
            except:
                metadata.update({
                    'version': 'N/A',
                    'submitted': 'N/A',
                    'submitter': 'N/A',
                    'approved': 'N/A',
                    'spdx': 'N/A'
                })
            
            # Get steward information
            try:
                steward_element = self.driver.find_element(By.CLASS_NAME, 'license-steward-meta')
                metadata['steward'] = steward_element.find_element(By.CLASS_NAME, 'license-steward').find_element(By.CLASS_NAME, 'term-item').text.strip()
                metadata['steward_url'] = steward_element.find_element(By.CLASS_NAME, 'license-steward-url').find_element(By.TAG_NAME, 'a').get_attribute('href')
            except:
                metadata.update({
                    'steward': 'N/A',
                    'steward_url': 'N/A'
                })
            
            # Get the license content
            try:
                content_element = self.driver.find_element(By.CLASS_NAME, 'entry-content')
                content = content_element.text.strip()
            except:
                content = "N/A"
            
            return {
                'metadata': metadata,
                'content': content
            }
        except Exception as e:
            print(f"Error scraping license content from {url}: {e}")
            return None

    def save_license_to_file(self, license_data, content_data):
        """Save license information to a JSON file"""
        if not license_data or not content_data:
            return

        # Use SPDX ID as filename
        filename = self.licenses_dir / f"{license_data['spdx']}.json"
        
        # Combine all data into a single dictionary
        license_info = {
            "basic_info": {
                "name": license_data['name'],
                "spdx_id": license_data['spdx'],
                "category": license_data['category'],
                "url": license_data['url']
            },
            "metadata": content_data['metadata'],
            "content": content_data['content']
        }
        
        # Save as JSON
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(license_info, f, indent=4, ensure_ascii=False)

    def download_all_licenses(self):
        """Download all available licenses"""
        print("Fetching list of available licenses...")
        licenses = self.get_all_licenses()
        
        # Create a summary file with all licenses
        summary = {
            "total_licenses": len(licenses),
            "licenses": []
        }
        
        print(f"Found {len(licenses)} licenses. Starting download...")
        for license_info in licenses:
            try:
                print(f"\nProcessing {license_info['name']} ({license_info['spdx']})...")
                
                # Scrape the license content
                print(f"Scraping content from {license_info['url']}")
                content_data = self.scrape_license_content(license_info['url'])
                time.sleep(2)
                if content_data:
                    # Save to file
                    self.save_license_to_file(license_info, content_data)
                    print(f"Saved {license_info['spdx']}.json")
                    
                    # Add to summary
                    summary["licenses"].append({
                        "name": license_info['name'],
                        "spdx_id": license_info['spdx'],
                        "category": license_info['category'],
                        "url": license_info['url']
                    })
                else:
                    print(f"Failed to scrape content for {license_info['spdx']}")
                
                # Add a small delay to avoid rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"Error processing {license_info['spdx']}: {e}")
                continue
        
        # Save summary file
        with open(self.licenses_dir / "summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=4, ensure_ascii=False)
        print("\nSaved summary.json with all license information")

def main():
    downloader = LicenseDownloader()
    downloader.download_all_licenses()
    print("\nLicense download complete!")

if __name__ == "__main__":
    main()