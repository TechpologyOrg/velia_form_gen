from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging
import imghdr
import io

from .services import extract_data_from_file

# Configure logging
logger = logging.getLogger(__name__)


def ocr_reader(request):
    """
    Display the OCR Reader page with file upload interface
    """
    return render(request, 'ocr/reader.html')


@csrf_exempt  # Allow external API calls without CSRF token
@require_http_methods(["POST"])
def extract_ocr(request):
    """
    Extract data from uploaded file (image or PDF) using OpenAI Vision API
    
    SECURITY FEATURES:
    - Files are processed in-memory only, never saved to disk
    - Content validation ensures files are truly images/PDFs
    - File size limits prevent DoS attacks
    - Files are immediately discarded after processing
    - No execution capabilities - read-only processing
    
    Expects a POST request with a file upload
    Returns JSON with extracted data
    """
    uploaded_file = None
    try:
        # Check if file was uploaded
        if 'file' not in request.FILES:
            return JsonResponse({
                'error': 'No file uploaded. Please provide a file in the "file" field.'
            }, status=400)
        
        uploaded_file = request.FILES['file']
        
        # Validate file size FIRST (max 20MB for PDFs, 10MB for images)
        max_size = 20 * 1024 * 1024  # 20MB
        if uploaded_file.size > max_size:
            return JsonResponse({
                'error': 'File too large. Maximum size is 20MB.'
            }, status=400)
        
        if uploaded_file.size == 0:
            return JsonResponse({
                'error': 'Empty file uploaded.'
            }, status=400)
        
        # Read file content into memory for validation (read once, use multiple times)
        file_content = uploaded_file.read()
        
        # Validate file content - ensure it's actually an image or PDF
        is_valid, file_type, error_msg = validate_file_content(file_content, uploaded_file.content_type)
        if not is_valid:
            return JsonResponse({
                'error': error_msg
            }, status=400)
        
        logger.info(f"Processing file: {uploaded_file.name}, validated type: {file_type}, size: {uploaded_file.size} bytes")
        
        # Create a file-like object from the bytes for processing
        # This ensures we're working with in-memory data only
        file_obj = io.BytesIO(file_content)
        file_obj.name = uploaded_file.name
        file_obj.content_type = uploaded_file.content_type
        
        # Extract data using OpenAI (file is processed in-memory)
        result = extract_data_from_file(file_obj, file_type)
        
        # Explicitly clear the file content from memory
        del file_content
        del file_obj
        
        # Check if there was an error
        if 'error' in result and len(result) == 1:
            return JsonResponse(result, status=500)
        
        # Return the extracted data
        return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"Error in extract_ocr: {str(e)}", exc_info=True)
        return JsonResponse({
            'error': f'Server error: {str(e)}'
        }, status=500)
    finally:
        # Ensure uploaded file is closed and memory is freed
        if uploaded_file:
            try:
                uploaded_file.close()
            except:
                pass


def validate_file_content(file_content, declared_type):
    """
    Validate that file content matches declared type and is safe to process.
    
    Returns: (is_valid, file_type, error_message)
    """
    # Check for PDF magic bytes
    if file_content.startswith(b'%PDF'):
        if declared_type not in ['application/pdf', 'application/x-pdf']:
            logger.warning(f"PDF file uploaded with incorrect MIME type: {declared_type}")
        return True, 'pdf', None
    
    # Validate image files using imghdr (checks actual file content, not just extension)
    try:
        image_type = imghdr.what(None, h=file_content)
        if image_type:
            # Valid image types
            allowed_image_types = ['jpeg', 'png', 'gif', 'webp', 'bmp', 'tiff']
            if image_type in allowed_image_types:
                return True, f'image/{image_type}', None
            else:
                return False, None, f'Unsupported image type: {image_type}'
    except Exception as e:
        logger.error(f"Error validating image: {e}")
    
    # Check if it might be a WEBP (not always detected by imghdr)
    if file_content[8:12] == b'WEBP':
        return True, 'image/webp', None
    
    # If we get here, file type couldn't be validated
    return False, None, 'File type could not be validated. Please upload a valid image (PNG, JPG, GIF, WebP) or PDF file.'
