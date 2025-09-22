# License Parser with OpenAI LLM

This script uses OpenAI's GPT-4o model to parse license text and extract structured information in JSON format.

## Features

- **Few-shot Learning**: Includes examples of MIT and GPL-3.0 licenses in the prompt
- **Structured Output**: Returns consistent JSON format with license attributes
- **Error Handling**: Graceful handling of API errors and JSON parsing issues
- **Confidence Scoring**: Provides confidence scores for parsed results

## Installation

```bash
pip install -r requirements_license_parser.txt
```

## Usage

### Simple Usage

```python
from simple_license_parser import parse_license_with_openai

# Your OpenAI API key
api_key = "your-openai-api-key-here"

# License text to parse
license_text = """
MIT License
Copyright (c) 2023 Example Corp
...
"""

# Parse the license
result = parse_license_with_openai(license_text, api_key)
print(json.dumps(result, indent=2))
```

### Advanced Usage

```python
from license_parser_openai import LicenseParser

# Initialize parser
parser = LicenseParser(api_key="your-openai-api-key-here")

# Parse single license
result = parser.parse_license(license_text)

# Parse multiple licenses
results = parser.parse_multiple_licenses([license1, license2, license3])

# Save results
parser.save_results(results, "output.json")
```

## Output Format

The parser returns a JSON object with the following structure:

```json
{
    "license_name": "MIT License",
    "license_type": "permissive",
    "rights": ["use", "modify", "distribute", "sublicense", "sell"],
    "obligations": ["include_copyright_notice", "include_license_text"],
    "restrictions": [],
    "commercial_use": true,
    "modification_allowed": true,
    "patent_grant": false,
    "confidence_score": 0.95
}
```

## Fields Explained

- **license_name**: Name of the license
- **license_type**: "permissive", "copyleft", or "proprietary"
- **rights**: List of granted rights (use, modify, distribute, etc.)
- **obligations**: List of required obligations (attribution, notice, etc.)
- **restrictions**: List of restrictions (no_sublicensing, etc.)
- **commercial_use**: Boolean indicating if commercial use is allowed
- **modification_allowed**: Boolean indicating if modifications are allowed
- **patent_grant**: Boolean indicating if patent rights are granted
- **confidence_score**: Confidence score (0.0-1.0) based on license clarity

## Examples

### MIT License
```json
{
    "license_name": "MIT License",
    "license_type": "permissive",
    "rights": ["use", "modify", "distribute", "sublicense", "sell"],
    "obligations": ["include_copyright_notice", "include_license_text"],
    "restrictions": [],
    "commercial_use": true,
    "modification_allowed": true,
    "patent_grant": false,
    "confidence_score": 0.98
}
```

### GPL-3.0 License
```json
{
    "license_name": "GNU General Public License",
    "license_type": "copyleft",
    "rights": ["use", "modify", "distribute"],
    "obligations": ["include_copyright_notice", "include_license_text", "disclose_source_code"],
    "restrictions": ["no_sublicensing", "no_proprietary_derivatives"],
    "commercial_use": true,
    "modification_allowed": true,
    "patent_grant": true,
    "confidence_score": 0.95
}
```

## Configuration

- **Model**: Uses GPT-4o by default (can be changed in the code)
- **Temperature**: Set to 0.1 for consistent, factual output
- **Max Tokens**: 1000-2000 depending on complexity
- **Response Format**: JSON object format enforced

## Error Handling

The script handles common errors:
- Invalid API key
- Network connectivity issues
- JSON parsing errors
- Rate limiting

## Notes

- Requires a valid OpenAI API key
- Uses few-shot learning with MIT and GPL-3.0 examples
- Designed for software license analysis
- Confidence scores help assess parsing quality
