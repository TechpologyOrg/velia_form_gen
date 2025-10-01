from openai import OpenAI
from django.conf import settings
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def get_ai_assistant_response(user_message, template_data=None, global_vars=None, selected_component=None):
    """
    Get response from OpenAI Published Prompt for card template help
    
    Args:
        user_message (str): User's question/message
        template_data (list): Current template component structure
        global_vars (dict): Global variables
        selected_component (dict): Currently selected component
    
    Returns:
        str: Assistant's response
    """
    try:
        # Prepare context information
        context_info = ""
        if template_data:
            context_info += f"\nCurrent template has {len(template_data)} root components.\n"
            context_info += f"Template structure: {json.dumps(template_data, indent=2)}\n"
        
        if global_vars:
            context_info += f"Global variables: {json.dumps(global_vars, indent=2)}\n"
        
        if selected_component:
            context_info += f"Currently selected component: {json.dumps(selected_component, indent=2)}\n"
        
        # Combine user message with context
        full_message = f"{user_message}\n\nContext:\n{context_info}"
        
        # Use the Published Prompt API
        response = client.responses.create(
            prompt={
                "id": "pmpt_68dda5c5844c81939419c1ccd2e0ce6001e32a296b29b91d",
                "version": "1"
            },
            # Pass the user message and context as additional data
            messages=[
                {
                    "role": "user", 
                    "content": full_message
                }
            ]
        )
        
        # Extract the response content
        if hasattr(response, 'choices') and len(response.choices) > 0:
            return response.choices[0].message.content
        else:
            logger.error(f"Unexpected response format: {response}")
            return "Sorry, I encountered an error while processing your request. Please try again."
            
    except Exception as e:
        logger.error(f"Error in get_ai_assistant_response: {str(e)}")
        return "Sorry, I'm having trouble connecting to the AI assistant. Please try again later."

def estimate_project_time(problem_description, worker_types, stage):
    """
    Estimate project time using the published prompt
    """
    try:
        # Prepare the message with all parameters
        message_content = f"""
        Problem Description: {problem_description}
        Worker Types: {worker_types}
        Stage: {stage}
        
        Please provide an estimate for this project.
        """
        
        response = client.responses.create(
            prompt={
                "id": "pmpt_68dda5c5844c81939419c1ccd2e0ce6001e32a296b29b91d",
                "version": "1"
            },
            messages=[
                {
                    "role": "user",
                    "content": message_content
                }
            ]
        )
        
        if hasattr(response, 'choices') and len(response.choices) > 0:
            # Try to parse as JSON if it's structured data
            try:
                return json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                # If it's not JSON, return as string
                return response.choices[0].message.content
        else:
            logger.error(f"Unexpected response format: {response}")
            return {"error": "Failed to get response from assistant"}
            
    except Exception as e:
        logger.error(f"Error in estimate_project_time: {str(e)}")
        return {"error": str(e)}
