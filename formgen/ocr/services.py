from openai import OpenAI
from django.conf import settings
import json
import logging
import base64

# Configure logging
logger = logging.getLogger(__name__)

# Initialize OpenAI client with error handling
try:
    if settings.OPENAI_API_KEY:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        OPENAI_AVAILABLE = True
    else:
        client = None
        OPENAI_AVAILABLE = False
        logger.warning("OPENAI_API_KEY not set. AI features will be disabled.")
except Exception as e:
    client = None
    OPENAI_AVAILABLE = False
    logger.error(f"Failed to initialize OpenAI client: {e}")


def extract_data_from_file(file_obj, file_type):
    """
    Extract data from a file (image or PDF) using OpenAI Vision API with OCR focus
    
    SECURITY: File is processed in-memory only, never saved to disk.
    File content is read, encoded, sent to OpenAI, and immediately discarded.
    
    Args:
        file_obj: File-like object (BytesIO) containing the file data
        file_type: String indicating file type (e.g., 'image/png', 'pdf')
    
    Returns:
        dict: Extracted data as JSON with OCR and other fields
    """
    # Check if OpenAI is available
    if not OPENAI_AVAILABLE or not client:
        return {
            "error": "AI assistant is currently unavailable. Please check your OpenAI API key configuration."
        }
    
    try:
        # Read the file data from the BytesIO object
        file_obj.seek(0)  # Ensure we're at the start
        file_data = file_obj.read()
        
        # Encode as base64 for OpenAI API
        base64_file = base64.b64encode(file_data).decode('utf-8')
        
        # Clear the file data from memory as soon as we have the base64
        del file_data
        
        # Determine MIME type for data URL
        if file_type == 'pdf':
            mime_type = 'application/pdf'
        elif file_type.startswith('image/'):
            mime_type = file_type
        else:
            mime_type = f'image/{file_type}'
        
        # Create the data URL
        data_url = f"data:{mime_type};base64,{base64_file}"
        
        # Prepare the prompt for OCR extraction
        prompt = """Analyze this document/image and extract all visible text and data from it.
        
Please provide the output as a JSON object with the following structure:
- "OCR": A complete transcription of ALL text visible in the image, preserving formatting and structure as much as possible
- For any other identifiable fields (like names, dates, amounts, addresses, etc.), create additional key-value pairs where the key is a descriptive field name and the value is the extracted data

Be thorough and accurate with the OCR. Include every piece of text you can see.

Example format:
{
    "OCR": "Complete text transcription here...",
    "Name": "John Doe",
    "Date": "2025-01-15",
    "Amount": "$150.00"
}

Return ONLY the JSON object, no additional text."""

        # Call OpenAI Vision API
        response = client.chat.completions.create(
            model="gpt-4o",  # Using GPT-4 with vision capabilities
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": data_url
                            }
                        }
                    ]
                }
            ],
            max_tokens=4096,
            temperature=0.2  # Lower temperature for more consistent/accurate extraction
        )
        
        # Extract the response content
        content = response.choices[0].message.content.strip()
        
        # Clear the base64 data from memory immediately after API call
        del base64_file
        del data_url
        
        # Try to parse as JSON
        try:
            # Remove markdown code blocks if present
            if content.startswith('```'):
                # Find the actual JSON content
                lines = content.split('\n')
                json_lines = []
                in_code_block = False
                for line in lines:
                    if line.startswith('```'):
                        in_code_block = not in_code_block
                        continue
                    if in_code_block or (not line.startswith('```')):
                        json_lines.append(line)
                content = '\n'.join(json_lines)
            
            extracted_data = json.loads(content)
            return extracted_data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from OpenAI response: {e}")
            logger.error(f"Response content: {content}")
            # Return the raw content if JSON parsing fails
            return {
                "OCR": content,
                "error": "Response was not in valid JSON format, showing raw content"
            }
            
    except Exception as e:
        logger.error(f"Error in extract_data_from_file: {str(e)}")
        return {
            "error": f"Failed to process file: {str(e)}"
        }
    finally:
        # Ensure all file data is cleared from memory
        try:
            if 'base64_file' in locals():
                del base64_file
            if 'data_url' in locals():
                del data_url
        except:
            pass

