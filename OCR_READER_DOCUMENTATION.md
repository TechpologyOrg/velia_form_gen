# OCR Reader Documentation

## Overview
The OCR Reader is a new feature that allows users to upload images or documents and extract text and structured data using OpenAI's Vision API (GPT-4 with vision capabilities).

## Features

### 1. Navigation
- Added a new "📷 OCR Reader" tab in the main navigation bar
- Accessible at `/ocr/` URL

### 2. File Upload Interface
- Drag-and-drop support for easy file uploading
- Click to browse and select files
- Preview of uploaded images before processing
- Supports: PNG, JPG, GIF, WebP image formats
- Maximum file size: 10MB

### 3. Data Extraction
- Extracts all visible text from images (OCR)
- Identifies and extracts structured fields (names, dates, amounts, etc.)
- Returns data in JSON format
- Specifically ensures OCR text is in the format: `{"OCR": "...", ...}`

### 4. Results Display
- Full OCR text in a formatted, readable view
- Individual extracted fields displayed as separate cards
- Copy buttons for:
  - OCR text only
  - Full JSON output
- Clean, modern UI using Tailwind CSS

## Technical Implementation

### New Files Created

1. **`formgen/ocr/`** - New Django app
   - `services.py` - OpenAI Vision API integration
   - `views.py` - Request handling for OCR page and extract endpoint
   - `urls.py` - URL routing for OCR features

2. **`formgen/templates/ocr/reader.html`** - OCR Reader page template

3. **Updated Files:**
   - `formgen/formgen/settings.py` - Added 'ocr' to INSTALLED_APPS
   - `formgen/formgen/urls.py` - Added OCR URL routing
   - `formgen/templates/base.html` - Added OCR Reader navigation tab

## API Endpoints

### POST `/ocr/extract`
Extracts data from uploaded image using OpenAI Vision API.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: File upload with key 'file'

**Response:**
```json
{
  "OCR": "Complete text transcription from the image...",
  "Name": "John Doe",
  "Date": "2025-01-15",
  "Amount": "$150.00",
  ...
}
```

**Error Response:**
```json
{
  "error": "Error message here"
}
```

## Usage

1. Navigate to the OCR Reader page by clicking the "📷 OCR Reader" tab in the navigation bar
2. Upload an image by:
   - Dragging and dropping it onto the upload zone
   - Clicking the upload zone to browse for files
3. Wait for the image to be processed (usually 3-10 seconds)
4. View extracted data in the results panel
5. Use copy buttons to copy OCR text or full JSON data

## OpenAI Configuration

The OCR feature uses the GPT-4o model with vision capabilities. Ensure your `OPENAI_API_KEY` environment variable is set:

```bash
export OPENAI_API_KEY='your-api-key-here'
```

The API key is already configured in `settings.py` to read from the environment variable.

## Error Handling

The system handles various error cases:
- Invalid file types (non-image files)
- Files exceeding size limit (>10MB)
- OpenAI API errors
- Network errors

All errors are displayed to the user in a friendly format with suggestions for resolution.

## Security Features

- CSRF protection enabled for all POST requests
- File type validation (images only)
- File size validation (max 10MB)
- Secure file handling (files not saved to disk)

## Future Enhancements

Potential improvements:
- Support for PDF documents
- Batch processing of multiple images
- History of processed images
- Export options (CSV, Excel)
- Custom extraction templates
- Multi-language OCR support

