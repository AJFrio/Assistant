"""
Main entry point for the Assistant application.

This module initializes all components and starts the application.
"""
import sys
import os
import threading
import socket
from typing import Optional, Dict, Any

from core.config import config
from core.logging import get_logger
from core.exceptions import ConfigurationError
from api.firebase import Firebase
from tasks.processor import task_processor
from ui.gui import create_gui, run_gui

# Configure logger
logger = get_logger(__name__)


def register_firebase_handlers(firebase: Optional[Firebase] = None) -> None:
    """
    Register task handlers with Firebase
    
    Args:
        firebase (Firebase, optional): Firebase instance
    """
    if not firebase:
        firebase = Firebase()
    
    # Define task handlers
    def handle_command_task(task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a command execution task"""
        from automation.system import run_command
        
        logger.info(f"Executing command: {task_data}")
        params = task_data.get('params')
        
        # Handle both string params and dictionary params
        if isinstance(params, dict):
            command = params.get('command')
        elif isinstance(params, str):
            # If params is directly a string, use it as the command
            command = params
        else:
            command = None
            
        if command:
            result = run_command(command)
            return {"command_result": result}
        return {"error": "No command provided"}

    def handle_open_app_task(task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an open app task"""
        from automation.applications import focus_application
        
        logger.info(f"Opening app: {task_data}")
        params = task_data.get('params')
        
        # Handle both string params and dictionary params
        if isinstance(params, dict):
            app_name = params.get('app_name')
        elif isinstance(params, str):
            # If params is directly a string, use it as the app name
            app_name = params
        else:
            app_name = None
            
        if app_name:
            result = focus_application(app_name)
            return {"app_opened": app_name}
        return {"error": "No app name provided"}

    def handle_default_task(task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Default handler for unrecognized tasks"""
        task_type = task_data.get('type', 'unknown')
        logger.info(f"Received unhandled task type: {task_type}")
        logger.info(f"Task data: {task_data}")
        return {"status": "acknowledged", "task_id": task_id}

    # Register task handlers
    firebase.register_task_handler("command", handle_command_task)
    firebase.register_task_handler("open_app", handle_open_app_task)
    
    # Start task polling in the background
    firebase.start_task_polling(
        interval=config.get("TASK_POLL_INTERVAL", 300), 
        default_handler=handle_default_task
    )


def main() -> None:
    """Main entry point for the application."""
    try:
        # Print banner
        print(f"Starting {config.get('ASSISTANT_NAME')} {config.get('ASSISTANT_ID')}")
        print("=" * 50)
        
        # Validate configuration
        error_msg = config.validate_required_keys(["OPENAI_API_KEY"])
        if error_msg:
            raise ConfigurationError(error_msg)
        
        # Initialize Firebase
        try:
            firebase = Firebase()
            firebase.update_status("on")
            computers = firebase.get_all_computers()
            logger.info(f"Connected to Firebase. Available computers: {computers}")
            
            # Register Firebase task handlers
            register_firebase_handlers(firebase)
            
        except Exception as e:
            logger.error(f"Firebase initialization error: {str(e)}")
            logger.warning("Continuing without Firebase support")
            firebase = None
        
        # Start task processor
        task_processor.start_processing()
        logger.info("Task processor started")
        
        # Create and run GUI
        gui = create_gui()
        logger.info("GUI created")
        
        # Run the GUI (this will block until the GUI is closed)
        run_gui(gui)
        
        # Clean up
        if firebase:
            firebase.update_status("off")
            firebase.stop_task_polling()
        
        logger.info("Application exiting")
        
    except ConfigurationError as e:
        logger.error(f"Configuration error: {str(e)}")
        print(f"Error: {str(e)}")
        print("Please check your .env file and ensure all required keys are set.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)


main()