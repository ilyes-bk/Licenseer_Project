#!/usr/bin/env python3
"""
License Parser using OpenAI LLM
Parses license text to extract terms, attributes, and compatibility information
Returns structured JSON output with few-shot learning examples
"""

import json
import openai
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LicenseParser:
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        """
        Initialize the License Parser with OpenAI API
        
        Args:
            api_key: OpenAI API key
            model: OpenAI model to use (default: gpt-4o)
        """
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        
    def create_parsing_prompt(self, license_text: str) -> str:
        """
        Create a comprehensive prompt with few-shot examples for license parsing
        
        Args:
            license_text: The license text to parse
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""
You are an expert legal AI assistant specializing in software license analysis. Your task is to parse license text and extract key terms, attributes, and compatibility information in a structured JSON format.

## Few-Shot Examples:

### Example 1: MIT License
**Input License Text:**
```
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
```

**Expected JSON Output:**
```json
{{
    "license_name": "MIT License",
    "license_type": "permissive",
    "spdx_identifier": "MIT",
    "rights": [
        "use",
        "modify",
        "distribute",
        "sublicense",
        "sell",
        "private_use"
    ],
    "obligations": [
        "include_copyright_notice",
        "include_license_text"
    ],
    "restrictions": [],
    "conditions": [
        "copyright_notice_required",
        "license_text_required"
    ],
    "compatibility": {{
        "copyleft_compatible": true,
        "gpl_compatible": true,
        "commercial_use": true,
        "modification_allowed": true,
        "distribution_allowed": true,
        "patent_grant": false
    }},
    "attribution_requirements": {{
        "copyright_notice": true,
        "license_text": true,
        "source_code": false,
        "modification_notice": false
    }},
    "commercial_use": true,
    "modification_allowed": true,
    "distribution_allowed": true,
    "patent_grant": false,
    "liability_disclaimer": true,
    "warranty_disclaimer": true,
    "confidence_score": 0.98
}}
```

### Example 2: GPL-3.0 License
**Input License Text:**
```
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
```

**Expected JSON Output:**
```json
{{
    "license_name": "GNU General Public License",
    "license_type": "copyleft",
    "spdx_identifier": "GPL-3.0",
    "rights": [
        "use",
        "modify",
        "distribute"
    ],
    "obligations": [
        "include_copyright_notice",
        "include_license_text",
        "disclose_source_code",
        "preserve_license_terms"
    ],
    "restrictions": [
        "no_sublicensing",
        "no_proprietary_derivatives"
    ],
    "conditions": [
        "copyright_notice_required",
        "license_text_required",
        "source_code_disclosure",
        "license_preservation"
    ],
    "compatibility": {{
        "copyleft_compatible": true,
        "gpl_compatible": true,
        "commercial_use": true,
        "modification_allowed": true,
        "distribution_allowed": true,
        "patent_grant": true
    }},
    "attribution_requirements": {{
        "copyright_notice": true,
        "license_text": true,
        "source_code": true,
        "modification_notice": true
    }},
    "commercial_use": true,
    "modification_allowed": true,
    "distribution_allowed": true,
    "patent_grant": true,
    "liability_disclaimer": true,
    "warranty_disclaimer": true,
    "confidence_score": 0.95
}}
```

## Instructions:
1. Analyze the provided license text carefully
2. Extract all relevant terms, rights, obligations, restrictions, and conditions
3. Determine compatibility with other license types
4. Provide a confidence score (0.0-1.0) based on clarity and completeness of the license text
5. Return ONLY valid JSON format - no additional text or explanations
6. If a field is not applicable or unclear, use null or empty array as appropriate
7. Be precise and factual - do not interpret or add information not present in the license text

## License Text to Parse:
```
{license_text}
```

## JSON Output:
"""
        return prompt

    def parse_license(self, license_text: str) -> Dict[str, Any]:
        """
        Parse license text and return structured JSON
        
        Args:
            license_text: The license text to parse
            
        Returns:
            Dictionary containing parsed license information
        """
        try:
            prompt = self.create_parsing_prompt(license_text)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert legal AI assistant specializing in software license analysis. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistent, factual output
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # Parse the JSON response
            result = json.loads(response.choices[0].message.content)
            
            logger.info(f"Successfully parsed license: {result.get('license_name', 'Unknown')}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return {"error": "Failed to parse JSON response", "raw_response": response.choices[0].message.content}
            
        except Exception as e:
            logger.error(f"Error parsing license: {e}")
            return {"error": str(e)}

    def parse_multiple_licenses(self, license_texts: List[str]) -> List[Dict[str, Any]]:
        """
        Parse multiple license texts
        
        Args:
            license_texts: List of license texts to parse
            
        Returns:
            List of parsed license dictionaries
        """
        results = []
        for i, license_text in enumerate(license_texts):
            logger.info(f"Parsing license {i+1}/{len(license_texts)}")
            result = self.parse_license(license_text)
            result["license_index"] = i
            results.append(result)
        
        return results

    def save_results(self, results: Dict[str, Any], filename: str) -> None:
        """
        Save parsing results to JSON file
        
        Args:
            results: Parsed license data
            filename: Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")


def main():
    """
    Example usage of the License Parser
    """
    # Initialize the parser (replace with your OpenAI API key)
    parser = LicenseParser(api_key="your-openai-api-key-here")
    
    # Example license texts
    mit_license = """
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

    apache_license = """
Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

"License" shall mean the terms and conditions for use, reproduction, and distribution as defined by Sections 1 through 9 of this document.

"Licensor" shall mean the copyright owner or entity granting the License.

"Legal Entity" shall mean the union of the acting entity and all other entities that control, are controlled by, or are under common control with that entity.

"You" (or "Your") shall mean an individual or Legal Entity exercising permissions granted by this License.

"Source" form shall mean the preferred form for making modifications, including but not limited to software source code, documentation source, and configuration files.

"Object" form shall mean any form resulting from mechanical transformation or translation of a Source form, including but not limited to compiled object code, generated documentation, and conversions to other media types.

"Work" shall mean the work of authorship, whether in Source or Object form, made available under the License, as indicated by a copyright notice that is included in or attached to the work.

"Derivative Works" shall mean any work, whether in Source or Object form, that is based upon (or derived from) the Work and for which the editorial revisions, annotations, elaborations, or other modifications represent, as a whole, an original work of authorship.

2. Grant of Copyright License. Subject to the terms and conditions of this License, each Contributor hereby grants to You a perpetual, worldwide, non-exclusive, no-charge, royalty-free, irrevocable copyright license to use, reproduce, modify, distribute, and prepare Derivative Works of, and to display and perform the Work and such Derivative Works in any medium, whether now known or hereafter devised.

3. Grant of Patent License. Subject to the terms and conditions of this License, each Contributor hereby grants to You a perpetual, worldwide, non-exclusive, no-charge, royalty-free, irrevocable (except as stated in this section) patent license to make, have made, use, offer to sell, sell, import, and otherwise transfer the Work, where such license applies only to those patent claims licensable by such Contributor that are necessarily infringed by their Contribution(s) alone or by combination of their Contribution(s) with the Work to which such Contribution(s) was submitted.

4. Redistribution. You may reproduce and distribute copies of the Work or Derivative Works thereof in any medium, with or without modifications, and in Source or Object form, provided that You meet the following conditions:

a) You must give any other recipients of the Work or Derivative Works a copy of this License; and

b) You must cause any modified files to carry prominent notices stating that You changed the files; and

c) You must retain, in the Source form of any Derivative Works that You distribute, all copyright, patent, trademark, and attribution notices from the Source form of the Work, excluding those notices that do not pertain to any part of the Derivative Works; and

d) If the Work includes a "NOTICE" text file as part of its distribution, then any Derivative Works that You distribute must include a readable copy of the attribution notices contained within such NOTICE file, excluding those notices that do not pertain to any part of the Derivative Works, in at least one of the following places: within a NOTICE text file distributed as part of the Derivative Works; within the Source form or documentation, if provided along with the Derivative Works; or, within a display generated by the Derivative Works, if and wherever such third-party notices normally appear. The contents of the NOTICE file are for informational purposes only and do not modify the License.

5. Submission of Contributions. Unless You explicitly state otherwise, any Contribution intentionally submitted for inclusion in the Work by You to the Licensor shall be under the terms and conditions of this License, without any additional terms or conditions.

6. Trademarks. This License does not grant permission to use the trade names, trademarks, service marks, or product names of the Licensor, except as required for reasonable and customary use in describing the origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or agreed to in writing, Licensor provides the Work (and each Contributor provides its Contributions) on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied, including, without limitation, any warranties or conditions of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A PARTICULAR PURPOSE.

8. Limitation of Liability. In no event and under no legal theory, whether in tort (including negligence), contract, or otherwise, unless required by applicable law (such as deliberate and grossly negligent acts) or agreed to in writing, shall any Contributor be liable to You for damages, including any direct, indirect, special, incidental, or consequential damages of any character arising as a result of this License or out of the use or inability to use the Work (including but not limited to damages for loss of goodwill, work stoppage, computer failure or malfunction, or any and all other commercial damages or losses), even if such Contributor has been advised of the possibility of such damages.

9. Accepting Warranty or Support. You may choose to offer, and charge a fee for, warranty, support, indemnity or other liability obligations and/or rights consistent with this License. However, in accepting such obligations, You may act only on Your own behalf and on Your sole responsibility, not on behalf of any other Contributor, and only if You agree to indemnify, defend, and hold each Contributor harmless for any liability incurred by, or claims asserted against, such Contributor by reason of your accepting any such warranty or support.
"""

    # Parse single license
    print("Parsing MIT License...")
    mit_result = parser.parse_license(mit_license)
    print(json.dumps(mit_result, indent=2))
    
    # Parse multiple licenses
    print("\nParsing multiple licenses...")
    all_results = parser.parse_multiple_licenses([mit_license, apache_license])
    
    # Save results
    parser.save_results(all_results, "parsed_licenses.json")
    
    print(f"\nParsed {len(all_results)} licenses successfully!")


if __name__ == "__main__":
    main()
