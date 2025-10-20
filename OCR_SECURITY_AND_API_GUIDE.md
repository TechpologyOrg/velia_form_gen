# OCR API Security & Usage Guide

## 🔒 Security Features

The OCR endpoint (`/ocr/extract`) has been designed with comprehensive security measures to ensure safe, public access:

### 1. **No File Storage on Server**
- **Files are NEVER saved to disk** - all processing happens entirely in-memory
- File content is read once into RAM, processed, and immediately discarded
- Explicit memory cleanup with `del` statements after processing
- Python's garbage collector ensures complete memory release

### 2. **Content Validation (Not Just Extension/MIME Type)**
- **Magic byte verification**: Files are validated by their actual binary content, not just their declared type
- PDF files: Checks for `%PDF` magic bytes at the start of the file
- Image files: Uses Python's `imghdr` library to verify actual image format
- WebP special handling: Additional check for WebP RIFF headers
- **Prevents executable files**: Only validated images and PDFs can be processed

### 3. **No Execution Capabilities**
- Files are treated as **read-only data**
- No file execution, interpretation, or script running
- Files are only:
  1. Read into memory
  2. Encoded as base64
  3. Sent to OpenAI API
  4. Discarded

### 4. **Size Limits (DoS Prevention)**
- Maximum file size: **20MB**
- Prevents memory exhaustion attacks
- Empty file detection and rejection

### 5. **Public API Access**
- `@csrf_exempt` decorator allows external API calls
- Anyone can call the endpoint without authentication
- Rate limiting should be added at the reverse proxy level (nginx/apache)

### 6. **Error Handling**
- Comprehensive try-except-finally blocks
- Memory cleanup in `finally` blocks ensures resources are freed even on errors
- Detailed error logging for debugging
- User-friendly error messages (no sensitive info leaked)

### 7. **File Type Restrictions**
Allowed file types:
- **Images**: PNG, JPEG, GIF, WebP, BMP, TIFF
- **Documents**: PDF

Blocked by default:
- Executables (.exe, .dll, .so)
- Scripts (.sh, .py, .js, .php)
- Archives (.zip, .tar, .rar)
- Office documents (.doc, .xlsx, .ppt)

---

## 📡 API Usage

### Endpoint
```
POST /ocr/extract
```

### Authentication
**None required** - This is a public endpoint

### Request Format

**Content-Type**: `multipart/form-data`

**Parameters**:
- `file` (required): The image or PDF file to process

### Example: cURL

```bash
# Basic usage
curl -X POST \
  -F "file=@/path/to/your/image.png" \
  https://your-domain.com/ocr/extract

# With verbose output
curl -v -X POST \
  -F "file=@/path/to/document.pdf" \
  https://your-domain.com/ocr/extract
```

### Example: Python (requests library)

```python
import requests

# Upload an image
with open('receipt.jpg', 'rb') as f:
    response = requests.post(
        'https://your-domain.com/ocr/extract',
        files={'file': f}
    )

# Check response
if response.status_code == 200:
    data = response.json()
    print("OCR Text:", data.get('OCR'))
    print("Extracted Fields:", {k: v for k, v in data.items() if k != 'OCR'})
else:
    print("Error:", response.json().get('error'))
```

### Example: JavaScript (Fetch API)

```javascript
// With File input from HTML
const fileInput = document.getElementById('fileInput');
const file = fileInput.files[0];

const formData = new FormData();
formData.append('file', file);

fetch('https://your-domain.com/ocr/extract', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    if (data.error) {
        console.error('Error:', data.error);
    } else {
        console.log('OCR Text:', data.OCR);
        console.log('Extracted Data:', data);
    }
})
.catch(error => console.error('Request failed:', error));
```

### Example: Node.js

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

async function extractOCR(filePath) {
    const form = new FormData();
    form.append('file', fs.createReadStream(filePath));
    
    try {
        const response = await axios.post(
            'https://your-domain.com/ocr/extract',
            form,
            {
                headers: form.getHeaders()
            }
        );
        
        console.log('OCR Text:', response.data.OCR);
        console.log('All Data:', response.data);
        return response.data;
    } catch (error) {
        console.error('Error:', error.response?.data || error.message);
    }
}

// Usage
extractOCR('./invoice.pdf');
```

---

## 📥 Response Format

### Success Response (200 OK)

```json
{
    "OCR": "Complete text transcription from the document...\nLine 2...\nLine 3...",
    "Name": "John Doe",
    "Date": "2025-10-20",
    "Amount": "$1,234.56",
    "Invoice_Number": "INV-2025-001",
    "Address": "123 Main St, City, State 12345"
}
```

**Fields:**
- `OCR` (string): Complete text transcription, always present
- Additional fields: Automatically extracted structured data (varies by document)

### Error Response (4xx/5xx)

```json
{
    "error": "Error message describing what went wrong"
}
```

**Common Error Cases:**

| Status Code | Error Message | Cause |
|-------------|---------------|-------|
| 400 | "No file uploaded. Please provide a file in the 'file' field." | Missing file parameter |
| 400 | "File too large. Maximum size is 20MB." | File exceeds size limit |
| 400 | "Empty file uploaded." | File has 0 bytes |
| 400 | "File type could not be validated..." | Invalid or unsupported file type |
| 500 | "AI assistant is currently unavailable..." | OpenAI API key not configured |
| 500 | "Server error: ..." | Internal server error |

---

## 🛡️ Security Best Practices

### For Server Administrators

1. **Rate Limiting** (Recommended)
   - Add rate limiting at the nginx/apache level
   - Example nginx config:
     ```nginx
     limit_req_zone $binary_remote_addr zone=ocr_limit:10m rate=10r/m;
     
     location /ocr/extract {
         limit_req zone=ocr_limit burst=5;
         proxy_pass http://localhost:8000;
     }
     ```

2. **File Size Limits at Proxy Level**
   - nginx: `client_max_body_size 20M;`
   - apache: `LimitRequestBody 20971520`

3. **Monitor OpenAI API Usage**
   - Track API costs
   - Set up billing alerts in OpenAI dashboard
   - Monitor for abuse patterns

4. **Logging and Monitoring**
   - Monitor file upload patterns
   - Track error rates
   - Set up alerts for unusual activity

5. **HTTPS Only**
   - Ensure endpoint is only accessible via HTTPS
   - Disable HTTP access for production

### For API Consumers

1. **Validate Files Client-Side**
   - Check file type before uploading
   - Validate file size < 20MB
   - Show user-friendly errors

2. **Handle Errors Gracefully**
   - Check response status codes
   - Parse error messages
   - Implement retry logic for network failures

3. **Respect Server Resources**
   - Don't abuse the endpoint with excessive requests
   - Implement client-side rate limiting
   - Cache results when appropriate

---

## 🚀 Performance Considerations

- **Average processing time**: 3-10 seconds per file
- **Depends on**:
  - File size
  - Document complexity
  - OpenAI API response time
  - Network latency

- **Best practices**:
  - Use async/await or promises for non-blocking operations
  - Show loading indicators to users
  - Implement timeout handling (recommend 30s timeout)

---

## 🔧 Troubleshooting

### "AI assistant is currently unavailable"
**Cause**: OpenAI API key not configured  
**Solution**: Set `OPENAI_API_KEY` environment variable on the server

### "File type could not be validated"
**Cause**: File is not a valid image or PDF  
**Solution**: 
- Ensure file is actually an image (PNG, JPG, etc.) or PDF
- Try re-saving the file in a standard format
- Check file isn't corrupted

### "File too large"
**Cause**: File exceeds 20MB limit  
**Solution**: 
- Compress the image
- Reduce image resolution
- Split multi-page PDFs

### Timeout errors
**Cause**: Processing takes too long  
**Solution**: 
- Increase client timeout to 30-60 seconds
- Reduce file size
- Try again during off-peak hours

---

## 📊 Cost Considerations

OpenAI Vision API pricing (as of 2025):
- GPT-4o: ~$0.01-0.03 per image depending on size
- Costs scale with usage
- Consider implementing usage quotas for high-traffic scenarios

---

## 🔄 Version History

### v1.1 (Current) - Enhanced Security
- Added content validation (magic bytes)
- Implemented in-memory-only processing
- Added explicit memory cleanup
- Made endpoint public with @csrf_exempt
- Enhanced error handling
- Added PDF support

### v1.0 - Initial Release
- Basic image OCR functionality
- OpenAI Vision API integration

