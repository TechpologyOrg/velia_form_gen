from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging

from .services import extract_data_from_image

# Configure logging
logger = logging.getLogger(__name__)


def ocr_reader(request):
    """
    Display the OCR Reader page with file upload interface
    """
    return render(request, 'ocr/reader.html')


@require_http_methods(["POST"])
def extract_ocr(request):
    """
    Extract data from uploaded image using OpenAI Vision API
    
    Expects a POST request with a file upload
    Returns JSON with extracted data
    """
    try:
        # Check if file was uploaded
        if 'file' not in request.FILES:
            return JsonResponse({
                'error': 'No file uploaded'
            }, status=400)
        
        uploaded_file = request.FILES['file']
        
        # Validate file type (images only)
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp', 'application/pdf']
        if uploaded_file.content_type not in allowed_types:
            return JsonResponse({
                'error': f'Invalid file type. Allowed types: {", ".join(allowed_types)}'
            }, status=400)
        
        # Validate file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if uploaded_file.size > max_size:
            return JsonResponse({
                'error': 'File too large. Maximum size is 10MB'
            }, status=400)
        
        logger.info(f"Processing file: {uploaded_file.name}, type: {uploaded_file.content_type}, size: {uploaded_file.size}")
        
        # Extract data using OpenAI
        result = extract_data_from_image(uploaded_file)
        
        # Check if there was an error
        if 'error' in result and len(result) == 1:
            return JsonResponse(result, status=500)
        
        # Return the extracted data
        return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"Error in extract_ocr: {str(e)}")
        return JsonResponse({
            'error': f'Server error: {str(e)}'
        }, status=500)
