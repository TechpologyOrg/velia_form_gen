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


def extract_data_from_image(image_file):
    """
    Extract data from an image using OpenAI Vision API with OCR focus
    
    Args:
        image_file: Django UploadedFile object containing the image
    
    Returns:
        dict: Extracted data as JSON with OCR and other fields
    """
    # Check if OpenAI is available
    if not OPENAI_AVAILABLE or not client:
        return {
            "error": "AI assistant is currently unavailable. Please check your OpenAI API key configuration."
        }
    
    try:
        # Read the image file and encode it as base64
        image_data = image_file.read()
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # Determine the image format
        image_format = image_file.content_type.split('/')[-1]
        if image_format == 'jpeg':
            image_format = 'jpg'
        
        # Create the data URL
        data_url = f"data:{image_file.content_type};base64,{base64_image}"
        
        # Prepare the prompt for OCR extraction
        prompt = """Analyze this image and extract all visible text and data from it.
        
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
        logger.error(f"Error in extract_data_from_image: {str(e)}")
        return {
            "error": f"Failed to process image: {str(e)}"
        }

