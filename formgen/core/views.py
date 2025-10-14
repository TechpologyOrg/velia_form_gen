from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST, require_http_methods
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import organisation, form

def index(request):
    return render(request, "core/index.html", {"orgs": organisation.objects.all()})

def get_forms(request, org_id):
    org = get_object_or_404(organisation, id=org_id)
    forms = form.objects.filter(organisation=org)
    return render(request, "core/forms_list.html", {"forms": forms, "org": org})

def editor(request, form_id):
    form_obj = get_object_or_404(form, id=form_id)
    # Serialize form data to JSON to ensure proper boolean handling
    form_data_json = json.dumps(form_obj.data)
    return render(request, "core/editor.html", {"form": form_obj, "form_data_json": form_data_json})

@require_POST
def create_form(request):
    try:
        data = json.loads(request.body)
        org_id = data.get('organisation_id')
        name = data.get('name')
        
        if not org_id or not name:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        org = get_object_or_404(organisation, id=org_id)
        
        # Create form with default schema structure
        default_schema = {
            "answers": [],
            "vars": {},
            "title": name,
            "description": ""
        }
        
        new_form = form.objects.create(
            name=name,
            organisation=org,
            data=default_schema
        )
        
        return JsonResponse({
            'success': True,
            'form_id': new_form.id,
            'redirect_url': f'/editor/{new_form.id}/'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_POST
def save_form_schema(request, form_id):
    try:
        form_obj = get_object_or_404(form, id=form_id)
        data = json.loads(request.body)
        
        # Validate the schema structure
        if not validate_schema(data):
            return JsonResponse({'error': 'Invalid schema structure'}, status=400)
        
        form_obj.data = data
        form_obj.save()
        
        return JsonResponse({'success': True})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_POST
def import_form(request):
    try:
        data = json.loads(request.body)
        org_id = data.get('organisation_id')
        name = data.get('name')
        json_data = data.get('json_data')
        
        if not org_id or not name or not json_data:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        org = get_object_or_404(organisation, id=org_id)
        
        # Parse and validate the JSON data
        try:
            imported_schema = json.loads(json_data)
        except json.JSONDecodeError as e:
            return JsonResponse({'error': f'Invalid JSON: {str(e)}'}, status=400)
        
        # Validate the schema structure
        if not validate_schema(imported_schema):
            return JsonResponse({'error': 'Invalid schema structure'}, status=400)
        
        # Create form with imported schema
        new_form = form.objects.create(
            name=name,
            organisation=org,
            data=imported_schema
        )
        
        return JsonResponse({
            'success': True,
            'form_id': new_form.id,
            'redirect_url': f'/editor/{new_form.id}/'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def validate_schema(data):
    """Validate the form schema structure"""
    required_fields = ['answers']
    if not all(field in data for field in required_fields):
        return False
    
    if not isinstance(data['answers'], list):
        return False
    
    # Validate each form in answers
    for form_data in data['answers']:
        if not isinstance(form_data, dict):
            return False
        
        required_form_fields = ['id', 'title', 'type', 'questions']
        if not all(field in form_data for field in required_form_fields):
            return False
        
        if form_data['type'] != 'form':
            return False
        
        if not isinstance(form_data['questions'], list):
            return False
        
        # Validate each question
        for question in form_data['questions']:
            if not isinstance(question, dict):
                return False
            
            required_question_fields = ['id', 'title', 'type']
            if not all(field in question for field in required_question_fields):
                return False
    
    return True

@require_POST
def delete_form(request, form_id):
    try:
        form_obj = get_object_or_404(form, id=form_id)
        org_id = form_obj.organisation.id
        form_obj.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Form deleted successfully',
            'org_id': org_id
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
