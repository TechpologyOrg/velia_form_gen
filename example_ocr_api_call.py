#!/usr/bin/env python3
"""
Example script showing how to call the OCR endpoint
Replace SERVER_URL with your actual server address
"""

import requests
import json
import sys

# Configuration
SERVER_URL = "http://localhost:8000"  # Change this to your server URL
OCR_ENDPOINT = f"{SERVER_URL}/ocr/extract"

def extract_ocr(file_path):
    """
    Extract OCR data from a file
    
    Args:
        file_path: Path to image or PDF file
    
    Returns:
        dict: Extracted data or error
    """
    try:
        # Open and send the file
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(OCR_ENDPOINT, files=files, timeout=60)
        
        # Check response
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'data': data
            }
        else:
            error_data = response.json()
            return {
                'success': False,
                'error': error_data.get('error', 'Unknown error'),
                'status_code': response.status_code
            }
    
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'error': 'Request timed out (>60s). Try a smaller file.'
        }
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'error': f'Could not connect to server at {SERVER_URL}'
        }
    except FileNotFoundError:
        return {
            'success': False,
            'error': f'File not found: {file_path}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def main():
    """Example usage"""
    if len(sys.argv) < 2:
        print("Usage: python3 example_ocr_api_call.py <path_to_image_or_pdf>")
        print(f"\nServer URL: {SERVER_URL}")
        print("Make sure the server is running!")
        return 1
    
    file_path = sys.argv[1]
    
    print(f"📤 Uploading file: {file_path}")
    print(f"🌐 Server: {OCR_ENDPOINT}")
    print("⏳ Processing (this may take 5-30 seconds)...\n")
    
    result = extract_ocr(file_path)
    
    if result['success']:
        print("✅ Success!\n")
        print("=" * 60)
        print("OCR TEXT:")
        print("=" * 60)
        print(result['data'].get('OCR', 'No OCR text found'))
        print("\n" + "=" * 60)
        print("EXTRACTED FIELDS:")
        print("=" * 60)
        
        # Print all fields except OCR
        fields = {k: v for k, v in result['data'].items() if k != 'OCR'}
        if fields:
            print(json.dumps(fields, indent=2))
        else:
            print("No additional fields extracted")
        
        print("\n" + "=" * 60)
        print("FULL JSON:")
        print("=" * 60)
        print(json.dumps(result['data'], indent=2))
        
        return 0
    else:
        print("❌ Error!")
        print(f"Status: {result.get('status_code', 'N/A')}")
        print(f"Error: {result['error']}")
        return 1

if __name__ == '__main__':
    sys.exit(main())


