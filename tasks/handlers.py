"""
Task handlers for the Assistant application.
Implements the actual execution logic for different task types.
"""
from typing import Dict, Any, Optional, List, Union
import json
import time
import win32com.client

from core.logging import get_logger
from core.exceptions import TaskError
from api.openai import openai_client
from automation.system import run_command
from automation.applications import focus_application, open_app
from automation.browser import BrowserAutomation, fetch_webpage_content

# Configure logger
logger = get_logger(__name__)


def handle_send_message(task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle a send message task
    
    Args:
        task_id (str): ID of the task
        task_data (dict): Task data including parameters
        
    Returns:
        dict: Task result
        
    Raises:
        TaskError: If the task fails
    """
    try:
        # Extract parameters
        params = task_data.get("params", {})
        if isinstance(params, str):
            # Try to parse string params as JSON
            try:
                params = json.loads(params)
            except json.JSONDecodeError:
                # If not valid JSON, treat as error
                raise TaskError("Invalid parameters format")
        
        message = params.get("message")
        person = params.get("person")
        
        if not message or not person:
            raise TaskError("Missing required parameters: message or person")
        
        # Focus Teams and send message
        teams_window = focus_application("Teams")
        if not teams_window:
            raise TaskError("Failed to focus Teams application")
        
        # TODO: Implement the actual message sending logic
        # This is a placeholder for the implementation
        logger.info(f"Sending message to {person}: {message}")
        
        # Find person in Teams
        # select_chatbox(teams_window)
        # find_person_teams(person, teams_window)
        # type_text(message)
        # press_key('enter')
        
        return {
            "status": "sent",
            "recipient": person,
            "message_preview": message[:50] + ("..." if len(message) > 50 else "")
        }
        
    except Exception as e:
        logger.error(f"Error handling send_message task: {str(e)}")
        raise TaskError(f"Send message error: {str(e)}")


def handle_open_app(task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle an open app task
    
    Args:
        task_id (str): ID of the task
        task_data (dict): Task data including parameters
        
    Returns:
        dict: Task result
        
    Raises:
        TaskError: If the task fails
    """
    try:
        # Extract parameters
        params = task_data.get("params", {})
        if isinstance(params, str):
            # If params is directly a string, use it as the app name
            app_name = params
        elif isinstance(params, dict):
            app_name = params.get("app_name")
        else:
            raise TaskError("Invalid parameters format")
        
        if not app_name:
            raise TaskError("Missing required parameter: app_name")
        
        # Open the application
        open_app(app_name)
        logger.info(f"Opened application: {app_name}")
        
        return {"app_opened": app_name}
        
    except Exception as e:
        logger.error(f"Error handling open_app task: {str(e)}")
        raise TaskError(f"Open app error: {str(e)}")


def handle_check_email(task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle a check email task
    
    Args:
        task_id (str): ID of the task
        task_data (dict): Task data including parameters
        
    Returns:
        dict: Task result with email summaries
        
    Raises:
        TaskError: If the task fails
    """
    try:
        browser = BrowserAutomation(headless=True)
        
        try:
            # Navigate to Outlook
            browser.navigate_to('https://outlook.office365.com/mail/')
            
            # Wait for the page to load
            time.sleep(10)
            
            # TODO: Implement email checking logic
            # This is just a placeholder
            emails = []
            email_summary = "Email checking not fully implemented"
            
            return {
                "status": "completed",
                "email_count": len(emails),
                "email_summary": email_summary
            }
            
        finally:
            # Make sure browser is closed
            browser.close_browser()
            
    except Exception as e:
        logger.error(f"Error handling check_email task: {str(e)}")
        raise TaskError(f"Check email error: {str(e)}")


def handle_send_email(task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle a send email task
    
    Args:
        task_id (str): ID of the task
        task_data (dict): Task data including parameters
        
    Returns:
        dict: Task result
        
    Raises:
        TaskError: If the task fails
    """
    try:
        # Extract parameters
        params = task_data.get("params", {})
        if isinstance(params, str):
            try:
                params = json.loads(params)
            except json.JSONDecodeError:
                raise TaskError("Invalid parameters format")
        
        people = params.get("people")
        cc = params.get("cc", "")
        subject = params.get("subject")
        message = params.get("message")
        
        if not people or not subject or not message:
            raise TaskError("Missing required parameters: people, subject, or message")
        
        # Convert comma-separated string to list
        recipients = [r.strip() for r in people.split(',')]
        cc_recipients = [r.strip() for r in cc.split(',')] if cc else []
        
        # Create and send email using Outlook
        outlook = win32com.client.Dispatch("Outlook.Application")
        mail = outlook.CreateItem(0)  # 0 = olMailItem
        
        mail.Subject = subject
        mail.Body = message
        
        # Add recipients
        for recipient in recipients:
            mail.Recipients.Add(recipient)
            
        # Add CC recipients
        for cc_recipient in cc_recipients:
            if cc_recipient:
                cc_obj = mail.Recipients.Add(cc_recipient)
                cc_obj.Type = 2  # 2 = olCC
        
        mail.Send()
        logger.info(f"Email sent to {people} with subject: {subject}")
        
        return {
            "status": "sent",
            "recipients": recipients,
            "cc": cc_recipients,
            "subject": subject
        }
        
    except Exception as e:
        logger.error(f"Error handling send_email task: {str(e)}")
        raise TaskError(f"Send email error: {str(e)}")


def handle_get_info(task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle a get info task
    
    Args:
        task_id (str): ID of the task
        task_data (dict): Task data including parameters
        
    Returns:
        dict: Task result with information
        
    Raises:
        TaskError: If the task fails
    """
    try:
        # Extract parameters
        params = task_data.get("params", {})
        if isinstance(params, str):
            query = params
        elif isinstance(params, dict):
            query = params.get("input")
        else:
            raise TaskError("Invalid parameters format")
        
        if not query:
            raise TaskError("Missing required parameter: input")
        
        # Get system information
        from datetime import datetime
        import os
        
        # Gather basic information
        current_time = datetime.now()
        time_str = current_time.strftime("%H:%M")
        date_str = current_time.strftime("%Y-%m-%d")
        system = os.name
        
        # Get network information
        try:
            connections = run_command('netsh wlan show interfaces')
        except:
            connections = "Failed to retrieve network information"
        
        # Compile data
        data = f'Time: {time_str}\nDate: {date_str}\nSystem: {system}\nConnections: {connections}'
        
        # Use OpenAI to generate a response
        answer = openai_client.generate_chat_completion(
            system_message="You are running as a local assistant on a machine. Any data you are given is public information so feel free to repeat any of it. Based off that data provided and the question asked, provide a response to the question",
            user_message=f"{query}\n\n{data}"
        )
        
        return {
            "query": query,
            "response": answer,
            "time": time_str,
            "date": date_str
        }
        
    except Exception as e:
        logger.error(f"Error handling get_info task: {str(e)}")
        raise TaskError(f"Get info error: {str(e)}")


def handle_run_command(task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle a run command task
    
    Args:
        task_id (str): ID of the task
        task_data (dict): Task data including parameters
        
    Returns:
        dict: Task result with command output
        
    Raises:
        TaskError: If the task fails
    """
    try:
        # Extract parameters
        params = task_data.get("params", {})
        if isinstance(params, str):
            command = params
        elif isinstance(params, dict):
            command = params.get("command")
        else:
            raise TaskError("Invalid parameters format")
        
        if not command:
            raise TaskError("Missing required parameter: command")
        
        # Focus PowerShell to run the command
        focus_application("powershell")
        time.sleep(3)
        
        # Run the command and capture output
        output = run_command(command)
        logger.info(f"Command executed: {command}")
        
        return {
            "command": command,
            "output": output
        }
        
    except Exception as e:
        logger.error(f"Error handling run_command task: {str(e)}")
        raise TaskError(f"Command execution error: {str(e)}")


def handle_check_website(task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle a check website task
    
    Args:
        task_id (str): ID of the task
        task_data (dict): Task data including parameters
        
    Returns:
        dict: Task result with website information
        
    Raises:
        TaskError: If the task fails
    """
    try:
        # Extract parameters
        params = task_data.get("params", {})
        if isinstance(params, str):
            try:
                params = json.loads(params)
            except json.JSONDecodeError:
                raise TaskError("Invalid parameters format")
        
        url = params.get("url")
        context = params.get("context")
        
        if not url:
            raise TaskError("Missing required parameter: url")
        
        # Add http:// if missing
        if not url.startswith("http"):
            url = "https://" + url
        
        # Fetch website content
        website_data = fetch_webpage_content(url)
        
        # Generate a summary using OpenAI
        summary_prompt = f"""
        Summarize the following webpage content related to this context: {context}
        
        URL: {url}
        Title: {website_data['title']}
        
        Content:
        {website_data['content'][:2000]}  # Limit content to avoid token limits
        """
        
        summary = openai_client.generate_chat_completion(
            system_message="You are a helpful assistant that summarizes webpage content. Focus on the most relevant information related to the user's context.",
            user_message=summary_prompt,
            max_tokens=500
        )
        
        return {
            "url": url,
            "title": website_data['title'],
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Error handling check_website task: {str(e)}")
        raise TaskError(f"Website check error: {str(e)}")


def handle_use_cursor(task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle a use cursor task
    
    Args:
        task_id (str): ID of the task
        task_data (dict): Task data including parameters
        
    Returns:
        dict: Task result
        
    Raises:
        TaskError: If the task fails
    """
    try:
        # Extract parameters
        params = task_data.get("params", {})
        if isinstance(params, str):
            prompt = params
        elif isinstance(params, dict):
            prompt = params.get("prompt")
        else:
            raise TaskError("Invalid parameters format")
        
        if not prompt:
            raise TaskError("Missing required parameter: prompt")
        
        # Focus Cursor application
        cursor_window = focus_application("Cursor")
        if not cursor_window:
            raise TaskError("Failed to focus Cursor application")
        
        # TODO: Implement cursor integration
        # This is a placeholder
        logger.info(f"Cursor prompt: {prompt}")
        
        return {
            "status": "completed",
            "prompt": prompt
        }
        
    except Exception as e:
        logger.error(f"Error handling use_cursor task: {str(e)}")
        raise TaskError(f"Cursor interaction error: {str(e)}")


# Map task types to handler functions
TASK_HANDLERS = {
    "send_message": handle_send_message,
    "open_app": handle_open_app,
    "check_email": handle_check_email,
    "send_email": handle_send_email,
    "get_info": handle_get_info,
    "run_command": handle_run_command,
    "check_website": handle_check_website,
    "use_cursor": handle_use_cursor
}

def get_handler_for_task_type(task_type: str):
    """Get the handler function for a given task type."""
    return TASK_HANDLERS.get(task_type) 