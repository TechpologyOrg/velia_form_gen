from openai import OpenAI
from django.conf import settings
import json
import logging

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

def get_ai_assistant_response(user_message, template_data=None, global_vars=None, selected_component=None, thread_id=None):
    """
    Get response from OpenAI Assistant API for card template help
    
    Args:
        user_message (str): User's question/message
        template_data (list): Current template component structure
        global_vars (dict): Global variables
        selected_component (dict): Currently selected component
        thread_id (str): OpenAI thread ID for this template (optional, will create new if None)
    
    Returns:
        dict: {"response": str, "thread_id": str}
    """
    # Check if OpenAI is available
    if not OPENAI_AVAILABLE or not client:
        return {
            "response": "AI assistant is currently unavailable. Please check your OpenAI API key configuration.",
            "thread_id": None
        }
    
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
        
        # Use existing thread or create new one
        if thread_id:
            try:
                # Verify thread exists
                client.beta.threads.retrieve(thread_id)
                current_thread_id = thread_id
            except:
                # Thread doesn't exist, create new one
                thread = client.beta.threads.create()
                current_thread_id = thread.id
                logger.info(f"Thread {thread_id} not found, created new thread: {current_thread_id}")
        else:
            # Create new thread
            thread = client.beta.threads.create()
            current_thread_id = thread.id
            logger.info(f"Created new thread: {current_thread_id}")
        
        # Add message to thread
        message = client.beta.threads.messages.create(
            thread_id=current_thread_id,
            role="user",
            content=full_message
        )
        
        # Run the assistant
        assistant_id = "asst_mPqnH9SVVX2hLLTeXp1ss18j"
        run = client.beta.threads.runs.create(
            thread_id=current_thread_id,
            assistant_id=assistant_id
        )
        
        # Wait for completion
        import time
        while run.status in ['queued', 'in_progress', 'cancelling']:
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=current_thread_id,
                run_id=run.id
            )
        
        if run.status == 'completed':
            # Get the assistant's response
            messages = client.beta.threads.messages.list(
                thread_id=current_thread_id
            )
            
            # Get the latest assistant message
            for message in messages.data:
                if message.role == 'assistant':
                    return {
                        "response": message.content[0].text.value,
                        "thread_id": current_thread_id
                    }
        else:
            logger.error(f"Assistant run failed with status: {run.status}")
            return {
                "response": "Sorry, I encountered an error while processing your request. Please try again.",
                "thread_id": current_thread_id
            }
            
    except Exception as e:
        logger.error(f"Error in get_ai_assistant_response: {str(e)}")
        return {
            "response": "Sorry, I'm having trouble connecting to the AI assistant. Please try again later.",
            "thread_id": thread_id
        }

def estimate_project_time(problem_description, worker_types, stage):
    """
    Estimate project time using the published prompt
    """
    # Check if OpenAI is available
    if not OPENAI_AVAILABLE or not client:
        return {"error": "AI assistant is currently unavailable. Please check your OpenAI API key configuration."}
    
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
            input=message_content  # Try 'input' parameter
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
