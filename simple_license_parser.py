#!/usr/bin/env python3
"""
Simple License Parser using OpenAI LLM
Extracts license terms and attributes from text and returns JSON
"""

import json
import openai
import os
from typing import Dict, Any

def parse_license_with_openai(license_text: str, api_key: str) -> Dict[str, Any]:
    """
    Parse license text using OpenAI LLM with few-shot examples
    
    Args:
        license_text: The license text to parse
        api_key: OpenAI API key
        
    Returns:
        Dictionary containing parsed license information
    """
    
    # Few-shot examples in the prompt
    prompt = f"""
You are a legal AI expert. Parse the license text below and return a JSON object with these fields:

Example 1 - MIT License:
Input: "MIT License... Permission is hereby granted..."
Output: {{
    "license_name": "MIT License",
    "license_type": "permissive",
    "rights": ["use", "modify", "distribute", "sublicense", "sell"],
    "obligations": ["include_copyright_notice", "include_license_text"],
    "restrictions": [],
    "commercial_use": true,
    "modification_allowed": true,
    "patent_grant": false,
    "confidence_score": 0.95
}}

Example 2 - GPL-3.0:
Input: "GNU GENERAL PUBLIC LICENSE Version 3..."
Output: {{
    "license_name": "GNU General Public License",
    "license_type": "copyleft", 
    "rights": ["use", "modify", "distribute"],
    "obligations": ["include_copyright_notice", "include_license_text", "disclose_source_code"],
    "restrictions": ["no_sublicensing", "no_proprietary_derivatives"],
    "commercial_use": true,
    "modification_allowed": true,
    "patent_grant": true,
    "confidence_score": 0.92
}}

Now parse this license text:
{license_text}

Return only valid JSON, no other text:
"""

    try:
        client = openai.OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a legal expert. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        return {{"error": str(e)}}

def main():
    """Example usage"""
    
    # Your OpenAI API key - set via environment variable
    API_KEY = os.getenv("OPENAI_API_KEY")
    if not API_KEY:
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY=sk-your-actual-api-key-here")
        return
    
    # Example license text
    license_text = """
MIT License

Copyright (c) 2023 Example Corp

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    
    # Parse the license
    result = parse_license_with_openai(license_text, API_KEY)
    
    # Print result
    print("Parsed License:")
    print(json.dumps(result, indent=2))
    
    # Save to file
    with open("parsed_license.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print("\nResult saved to 'parsed_license.json'")

if __name__ == "__main__":
    main()
