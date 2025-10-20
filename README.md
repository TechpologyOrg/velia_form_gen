# Velia Form Generator

A powerful Django-based dynamic form generation system with advanced conditional logic and variable manipulation.

## Features

### Core Capabilities
- **Dynamic Form Builder**: Visual editor for creating complex forms
- **Conditional Visibility** (`visibleWhen`): Show/hide questions based on answers
- **Variable Manipulation** (`onCondition`): Automatically update variables based on form responses
- **OCR Reader**: AI-powered text extraction from images and PDFs
- **Multiple Question Types**: text, numeric, choice, boolean, date, toggleList, file upload, markdown, and more
- **Nested Sections**: Organize forms into hierarchical sections
- **Real-time JSON Preview**: See your form schema as you build
- **Import/Export**: Share and reuse form templates

### Question Types
- **text**: Single-line text input
- **numeric**: Number input with validation
- **choice**: Single selection from options
- **boolean**: Yes/No toggle
- **date**: Date picker
- **toggleList**: Multiple selection checkboxes
- **fileUpload**: File upload with type and size validation
- **paragraph**: Multi-line text area
- **markdown**: Rich text with markdown support
- **display**: Display variables from the vars object
- **title**: Section headers and labels

## OCR Reader - NEW! 🚀

Extract text and structured data from images and PDF documents using AI-powered OCR.

### Features
- **Drag-and-drop file upload** with instant preview
- **AI-powered OCR** using OpenAI GPT-4o Vision API
- **Structured data extraction** - automatically identifies fields like names, dates, amounts, etc.
- **Public API endpoint** - can be called from anywhere
- **Secure processing** - files never saved to disk, processed in-memory only
- **Multiple formats** - supports PNG, JPG, GIF, WebP, PDF

### Quick Start

1. Navigate to **📷 OCR Reader** in the navigation bar
2. Upload an image or PDF document
3. Wait 5-30 seconds for AI processing
4. View extracted text and structured data
5. Copy OCR text or full JSON output

### API Usage

The OCR endpoint is publicly accessible at `/ocr/extract`:

```bash
curl -X POST \
  -F "file=@/path/to/your/image.png" \
  https://your-server.com/ocr/extract
```

**Response:**
```json
{
  "OCR": "Complete text transcription...",
  "Name": "John Doe",
  "Date": "2025-10-20",
  "Amount": "$1,234.56"
}
```

### Documentation
- **Complete API Guide**: See `OCR_SECURITY_AND_API_GUIDE.md`
- **Feature Overview**: See `OCR_READER_DOCUMENTATION.md`
- **Example Script**: Run `python3 example_ocr_api_call.py <image_file>`

### Security
✅ Files processed in-memory only (never saved to disk)  
✅ Content validation (magic byte verification)  
✅ No executable files accepted  
✅ Size limits (20MB max)  
✅ Immediate memory cleanup after processing  

---

## New Feature: onCondition Variable Manipulation

The `onCondition` system allows questions to dynamically modify form variables when certain conditions are met.

### Quick Example

```json
{
  "id": 4,
  "title": "Employment Status",
  "type": "choice",
  "choices": ["employed", "student", "unemployed"],
  "onCondition": [
    {
      "condition": {
        "path": "4",
        "op": "equals",
        "value": "employed"
      },
      "action": {
        "type": "append",
        "varName": "user_tags",
        "value": "professional"
      }
    }
  ]
}
```

### Action Types
- **set**: Set/overwrite variable value
- **append**: Add value to array variable
- **increment**: Add to numeric variable
- **decrement**: Subtract from numeric variable

### Documentation
- **Quick Start**: See `ONCONDITION_QUICKSTART.md`
- **Complete Reference**: See `ONCONDITION_DOCUMENTATION.md`
- **Feature Summary**: See `ONCONDITION_FEATURE_SUMMARY.md`
- **Implementation Details**: See `IMPLEMENTATION_SUMMARY.md`

## Installation

### Prerequisites
- Python 3.8+
- Django 5.2+
- Node.js (for frontend assets)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd velia_form_gen
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database:
```bash
cd formgen
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

7. Access the application at `http://localhost:8000`

## Project Structure

```
velia_form_gen/
├── formgen/
│   ├── core/               # Form generation app
│   │   ├── models.py       # Form and organisation models
│   │   ├── views.py        # Form CRUD operations
│   │   └── urls.py         # URL routing
│   ├── cardgen/            # Card template generation app
│   ├── ocr/                # OCR Reader app (NEW)
│   │   ├── services.py     # OpenAI Vision API integration
│   │   ├── views.py        # OCR endpoint handlers
│   │   └── urls.py         # OCR routing
│   ├── templates/
│   │   ├── core/
│   │   │   ├── editor.html # Main form editor
│   │   │   └── index.html  # Organisation list
│   │   ├── ocr/
│   │   │   └── reader.html # OCR Reader interface
│   │   └── base.html       # Base template
│   ├── formgen/            # Django project settings
│   └── manage.py
├── sample_form.json        # Example form with onCondition
├── sample_answers_array.json
├── example_ocr_api_call.py # Example OCR API usage
├── requirements.txt
└── Documentation files...
```

## Usage

### Creating a Form

1. Navigate to the home page
2. Select or create an organisation
3. Click "New Form"
4. Use the visual editor to add sections and questions
5. Configure conditional logic (visibleWhen, onCondition)
6. Save and export your form

### Adding Conditional Visibility

1. Edit any question
2. Check "This question is conditionally visible"
3. Configure the condition:
   - Choose condition type (Simple, AND, OR)
   - Set path to reference question
   - Select operator
   - Enter comparison value
4. Save the question

### Adding Variable Manipulation

1. Edit any question
2. Scroll to "Variable Actions (onCondition)"
3. Click "+ Add Variable Action"
4. Configure WHEN (Condition):
   - Select condition type
   - Set the path, operator, and value
5. Configure THEN (Action):
   - Choose action type (set, append, increment, decrement)
   - Enter variable name
   - Enter value
6. Save the question

### Working with Variables

Initialize variables in the `vars` object:

```json
{
  "vars": {
    "user_tags": [],
    "score": 0,
    "status": "pending"
  }
}
```

Variables can be:
- Displayed using the "display" question type
- Modified using onCondition rules
- Used in backend processing

## API Endpoints

### Form Management
- `GET /` - Organisation list
- `GET /org/<org_id>/` - Forms list for organisation
- `GET /editor/<form_id>/` - Form editor
- `POST /api/save-form/<form_id>/` - Save form schema
- `POST /create-form/` - Create new form
- `POST /import-form/` - Import form from JSON
- `POST /delete-form/<form_id>/` - Delete form

### OCR API (Public)
- `GET /ocr/` - OCR Reader interface
- `POST /ocr/extract` - Extract text/data from uploaded file (images/PDFs)

## Examples

See `sample_form.json` for a complete example featuring:
- Multiple question types
- Conditional visibility (visibleWhen)
- Variable manipulation (onCondition)
- Nested logic with allOf/anyOf
- Various operators and action types

## Technology Stack

- **Backend**: Django 5.2, Python
- **Frontend**: HTML, CSS (TailwindCSS), JavaScript (Vanilla)
- **Database**: SQLite (development), PostgreSQL-ready
- **Additional**: django-htmx, OpenAI API integration (for cardgen)

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: OpenAI API key for AI-powered features (optional)
- `SECRET_KEY`: Django secret key (set in production)
- `DEBUG`: Debug mode (set to False in production)
- `ALLOWED_HOSTS`: Allowed hosts for production
- `CSRF_TRUSTED_ORIGINS`: Trusted origins for CSRF

### Production Settings

Update `formgen/settings.py`:
- Set `DEBUG = False`
- Configure `ALLOWED_HOSTS`
- Set strong `SECRET_KEY`
- Configure database (PostgreSQL recommended)
- Set up static files collection

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Development Roadmap

### Current Status
✅ Form schema and editor
✅ Conditional visibility (visibleWhen)
✅ onCondition schema and UI
✅ Multiple question types
✅ Documentation

### Upcoming
⏳ Runtime evaluation engine for onCondition
⏳ Form renderer with live preview
⏳ Form response collection and storage
⏳ Analytics and reporting
⏳ Form templates library
⏳ Custom themes

## Troubleshooting

### Common Issues

**Forms not saving:**
- Check browser console for JavaScript errors
- Verify CSRF token is present
- Check server logs for backend errors

**Questions not appearing:**
- Verify question ID is unique
- Check visibleWhen conditions
- Ensure question type is supported

**Variables not updating:**
- onCondition requires runtime evaluation implementation
- Currently only saves schema, not executed yet
- See implementation notes in documentation

## License

[Add your license here]

## Support

For questions, issues, or feature requests:
- Create an issue in the repository
- Check documentation files
- Review sample_form.json for examples

## Credits

Developed by AWRA team for Velia.se

## Version History

### v2.1.0 (October 2025) - NEW!
- **OCR Reader**: AI-powered text extraction from images and PDFs
- Public API endpoint for OCR processing (`/ocr/extract`)
- Enhanced security: in-memory file processing, content validation
- Comprehensive security documentation

### v2.0.0 (October 2025)
- Added onCondition variable manipulation system
- Enhanced editor UI
- Comprehensive documentation
- Sample forms with examples

### v1.0.0
- Initial release
- Basic form builder
- visibleWhen conditional logic
- Multiple question types

