from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST, require_http_methods
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import card_template, generated_card
from core.models import organisation

def index(request):
    """Card dashboard index page"""
    return render(request, "cardgen/index.html", {"orgs": organisation.objects.all()})

def get_card_templates(request, org_id):
    """Get all card templates for an organisation"""
    org = get_object_or_404(organisation, id=org_id)
    templates = card_template.objects.filter(organisation=org)
    return render(request, "cardgen/templates_list.html", {"templates": templates, "org": org})

def editor(request, template_id):
    """Card template editor"""
    template_obj = get_object_or_404(card_template, id=template_id)
    return render(request, "cardgen/editor.html", {"template": template_obj})

@require_POST
def create_card_template(request):
    """Create a new card template"""
    try:
        data = json.loads(request.body)
        org_id = data.get('organisation_id')
        name = data.get('name')
        
        if not org_id or not name:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        org = get_object_or_404(organisation, id=org_id)
        
        # Create template with default schema structure
        default_template_data = [
            {
                "tag": "div",
                "class": "flex flex-col gap-4 p-4",
                "children": [
                    {
                        "tag": "h2",
                        "class": "text-xl font-bold",
                        "value": "New Card Template"
                    },
                    {
                        "tag": "p",
                        "class": "text-gray-600",
                        "value": "Add your components here"
                    }
                ]
            }
        ]
        
        new_template = card_template.objects.create(
            name=name,
            organisation=org,
            template_data=default_template_data,
            global_vars={}
        )
        
        return JsonResponse({
            'success': True,
            'template_id': new_template.id,
            'redirect_url': f'/cardgen/editor/{new_template.id}/'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_POST
def save_card_template_schema(request, template_id):
    """Save card template schema"""
    try:
        template_obj = get_object_or_404(card_template, id=template_id)
        data = json.loads(request.body)
        
        # Validate the schema structure
        if not validate_card_schema(data):
            return JsonResponse({'error': 'Invalid schema structure'}, status=400)
        
        template_obj.template_data = data
        template_obj.save()
        
        return JsonResponse({'success': True})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_POST
def import_card_template(request):
    """Import card template from JSON"""
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
        if not validate_card_schema(imported_schema):
            return JsonResponse({'error': 'Invalid schema structure'}, status=400)
        
        # Create template with imported schema
        new_template = card_template.objects.create(
            name=name,
            organisation=org,
            template_data=imported_schema,
            global_vars={}
        )
        
        return JsonResponse({
            'success': True,
            'template_id': new_template.id,
            'redirect_url': f'/cardgen/editor/{new_template.id}/'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def validate_card_schema(data):
    """Validate the card template schema structure"""
    # Card template should be an array of components
    if not isinstance(data, list):
        return False
    
    # Validate each component in the template
    for component in data:
        if not isinstance(component, dict):
            return False
        
        # Each component must have a tag
        if 'tag' not in component:
            return False
        
        # Validate component structure recursively
        if not validate_component(component):
            return False
    
    return True

def validate_component(component):
    """Validate a single component structure"""
    if not isinstance(component, dict):
        return False
    
    # Must have a tag
    if 'tag' not in component:
        return False
    
    tag = component['tag']
    
    # Valid HTML tags
    html_tags = ['div', 'p', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'img', 'a', 'button']
    
    # Valid interactive component tags
    interactive_tags = ['Itext', 'IBool', 'IChoice', 'IToggle', 'Imultiline', 'Ibutton', 'I_V_Button']
    
    if tag not in html_tags + interactive_tags:
        return False
    
    # If it's an interactive component, validate required fields
    if tag in interactive_tags:
        if 'type' not in component:
            return False
        if component['type'] not in ['Editable', 'display']:
            return False
    
    # If it has children, validate them recursively
    if 'children' in component:
        if not isinstance(component['children'], list):
            return False
        for child in component['children']:
            if not validate_component(child):
                return False
    
    return True

@require_POST
def delete_card_template(request, template_id):
    """Delete a card template"""
    try:
        template_obj = get_object_or_404(card_template, id=template_id)
        org_id = template_obj.organisation.id
        template_obj.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Card template deleted successfully',
            'org_id': org_id
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_POST
def generate_card(request, template_id):
    """Generate a card from template"""
    try:
        template_obj = get_object_or_404(card_template, id=template_id)
        data = json.loads(request.body)
        name = data.get('name')
        
        if not name:
            return JsonResponse({'error': 'Missing card name'}, status=400)
        
        # Create generated card with template data
        new_card = generated_card.objects.create(
            name=name,
            template=template_obj,
            card_data=template_obj.template_data,  # Copy template data as starting point
            global_vars=template_obj.global_vars
        )
        
        return JsonResponse({
            'success': True,
            'card_id': new_card.id,
            'message': 'Card generated successfully'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)