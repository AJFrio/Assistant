"""
Firebase API client for the Assistant application.
Manages interaction with Firebase Realtime Database.
"""
import requests
import socket
import time
import threading
from typing import Dict, Any, Optional, Callable, List, Union
import os

from core.config import config
from core.logging import get_logger
from core.exceptions import FirebaseError, ConfigurationError

# Configure logger
logger = get_logger(__name__)


class Firebase:
    """Firebase Realtime Database client with task management capabilities."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Firebase, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, verify_ssl: bool = False):
        """
        Initialize Firebase Realtime Database client
        
        Args:
            verify_ssl (bool): Whether to verify SSL certificates
        """
        if self._initialized:
            return
            
        try:
            # Load required configuration
            self.project_id = config.get("FIREBASE_PROJECT_ID")
            self.api_key = config.get("FIREBASE_API_KEY")
            self.descriptor = config.get("DESCRIPTOR")
            
            # Validate configuration
            error_msg = config.validate_required_keys(["FIREBASE_PROJECT_ID", "FIREBASE_API_KEY"])
            if error_msg:
                raise ConfigurationError(error_msg)
                
            # Initialize client properties
            self.computer_name = socket.gethostname()
            self.base_url = f"https://{self.project_id}-default-rtdb.firebaseio.com"
            self.verify_ssl = verify_ssl
            
            # Task polling configuration
            self._polling_thread = None
            self._polling_active = False
            self._task_handlers: Dict[str, Callable] = {}
            
            # Update descriptor if available
            if self.descriptor:
                self._update_descriptor()
                
            self._initialized = True
            logger.info(f"Firebase client initialized for project: {self.project_id}")
            
        except Exception as e:
            logger.error(f"Error initializing Firebase: {str(e)}")
            raise FirebaseError(f"Firebase initialization error: {str(e)}", 
                              details={"project_id": self.project_id if hasattr(self, "project_id") else None})
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a request to the Firebase Realtime Database
        
        Args:
            method (str): HTTP method (GET, POST, PUT, PATCH, DELETE)
            endpoint (str): API endpoint
            data (dict, optional): Data to send
            
        Returns:
            dict: Response from Firebase
            
        Raises:
            FirebaseError: If the request fails
        """
        url = f"{self.base_url}/{endpoint}.json"
        params = {"auth": self.api_key}
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, verify=self.verify_ssl)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, params=params, verify=self.verify_ssl)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, params=params, verify=self.verify_ssl)
            elif method.upper() == "PATCH":
                response = requests.patch(url, json=data, params=params, verify=self.verify_ssl)
            elif method.upper() == "DELETE":
                response = requests.delete(url, params=params, verify=self.verify_ssl)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Check if the request was successful
            if response.status_code not in range(200, 300):
                raise FirebaseError(
                    f"Firebase API error: {response.status_code}", 
                    details={"status_code": response.status_code, "text": response.text}
                )
                
            return response.json() if response.text.strip() else {}
            
        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise FirebaseError(f"Firebase request error: {str(e)}")
        
    def update_status(self, status: str = "on") -> Dict[str, Any]:
        """
        Update the status of this computer in the database
        
        Args:
            status (str): Status to set ("on" or "off")
            
        Returns:
            dict: Response from Firebase
        """
        endpoint = f"devices/{self.computer_name}"
        
        data = {
            "status": status,
            "last_seen": {".sv": "timestamp"},
            "tasks": {} if status == "on" else None  # Initialize tasks if online
        }
        
        # Include descriptor if available
        if self.descriptor:
            data["descriptor"] = self.descriptor
        
        result = self._make_request("PUT", endpoint, data)
        logger.info(f"Set status for {self.computer_name} to '{status}'")
        return result
    
    def get_tasks(self) -> Dict[str, Any]:
        """
        Get tasks assigned to this computer
        
        Returns:
            dict: Tasks or empty dict if no tasks found
        """
        endpoint = f"devices/{self.computer_name}/tasks"
        result = self._make_request("GET", endpoint)
        return result if result else {}
    
    def add_task_to_computer(self, target_computer: str, task_type: str, 
                            task_params: Optional[Union[Dict[str, Any], str]] = None) -> Dict[str, Any]:
        """
        Add a task to another computer's queue
        
        Args:
            target_computer (str): Name of the computer to add the task to
            task_type (str): Type of task to add
            task_params (dict or str): Parameters for the task
            
        Returns:
            dict: Response from Firebase
        """
        endpoint = f"devices/{target_computer}/tasks"
        
        # Generate a unique task ID based on timestamp
        task_id = f"task_{int(time.time() * 1000)}"
        
        data = {
            task_id: {
                "type": task_type,
                "params": task_params,
                "status": "pending",
                "created_by": self.computer_name,
                "created_at": {".sv": "timestamp"}
            }
        }
        
        result = self._make_request("PATCH", endpoint, data)
        logger.info(f"Added task {task_type} to {target_computer}")
        return result
    
    def complete_task(self, task_id: str, result: Optional[Dict[str, Any]] = None) -> bool:
        """
        Mark a task as completed and remove it from the queue
        
        Args:
            task_id (str): ID of the task to complete
            result (dict, optional): Optional result data
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Delete the task
        endpoint = f"devices/{self.computer_name}/tasks/{task_id}"
        self._make_request("DELETE", endpoint)
        logger.info(f"Completed and removed task {task_id}")
        
        # If there's a result, store it in a completed_tasks collection
        if result is not None:
            completed_endpoint = f"completed_tasks/{self.computer_name}/{task_id}"
            completed_data = {
                "result": result,
                "completed_at": {".sv": "timestamp"}
            }
            self._make_request("PUT", completed_endpoint, completed_data)
            
        return True
            
    def get_computer_status(self, computer_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of another computer
        
        Args:
            computer_name (str): Name of the computer to check
            
        Returns:
            dict: Computer status data or None if not found
        """
        endpoint = f"devices/{computer_name}"
        return self._make_request("GET", endpoint)
    
    def get_all_computers(self) -> List[str]:
        """
        Get the names of all computers in the database
        
        Returns:
            list: List of computer names or empty list if none found
        """
        endpoint = "devices"
        result = self._make_request("GET", endpoint)
        return list(result.keys()) if result else []
        
    def _update_descriptor(self) -> None:
        """Update the descriptor for this computer."""
        endpoint = f"devices/{self.computer_name}"
        data = {"descriptor": self.descriptor}
        self._make_request("PATCH", endpoint, data)
        logger.info(f"Updated descriptor for {self.computer_name} to '{self.descriptor}'")
    
    def start_task_polling(self, interval: int = 60, default_handler: Optional[Callable] = None) -> None:
        """
        Start polling for tasks in the background
        
        Args:
            interval (int): Interval between polls in seconds
            default_handler (callable, optional): Default handler for unrecognized tasks
        """
        if self._polling_active:
            logger.warning("Task polling is already active")
            return
            
        self._polling_active = True
        self._default_handler = default_handler
        
        # Start the polling thread
        self._polling_thread = threading.Thread(
            target=self._poll_tasks_worker,
            args=(interval,),
            daemon=True
        )
        self._polling_thread.start()
        logger.info(f"Started task polling with interval of {interval} seconds")
    
    def stop_task_polling(self) -> None:
        """Stop polling for tasks."""
        if not self._polling_active:
            logger.warning("Task polling is not active")
            return
            
        self._polling_active = False
        if self._polling_thread:
            self._polling_thread.join(timeout=1.0)
            self._polling_thread = None
        logger.info("Stopped task polling")
    
    def register_task_handler(self, task_type: str, handler_function: Callable) -> None:
        """
        Register a handler function for a specific task type
        
        Args:
            task_type (str): Type of task to handle
            handler_function (callable): Function to call when a task of this type is received
        """
        self._task_handlers[task_type] = handler_function
        logger.info(f"Registered handler for task type: {task_type}")
    
    def _poll_tasks_worker(self, interval: int) -> None:
        """
        Worker function for task polling thread
        
        Args:
            interval (int): Interval between polls in seconds
        """
        logger.info("Task polling worker started")
        while self._polling_active:
            try:
                # Get tasks from Firebase
                tasks = self.get_tasks()
                if tasks:
                    logger.info(f"Found {len(tasks)} tasks")
                    for task_id, task_data in tasks.items():
                        try:
                            self._handle_task(task_id, task_data)
                        except Exception as e:
                            logger.error(f"Error handling task {task_id}: {str(e)}")
                
                # Update status to show we're still alive
                self.update_status("on")
                
            except Exception as e:
                logger.error(f"Error in task polling: {str(e)}")
                
            # Sleep for the interval
            for _ in range(interval):
                if not self._polling_active:
                    break
                time.sleep(1)
    
    def _handle_task(self, task_id: str, task_data: Dict[str, Any]) -> None:
        """
        Handle a task received from Firebase
        
        Args:
            task_id (str): ID of the task
            task_data (dict): Task data
        """
        task_type = task_data.get("type", "unknown")
        logger.info(f"Handling task: {task_id} of type {task_type}")
        
        # Find a handler for this task type
        handler = self._task_handlers.get(task_type)
        
        if handler:
            # Call the handler
            try:
                result = handler(task_id, task_data)
                self.complete_task(task_id, result)
                logger.info(f"Task {task_id} completed successfully")
            except Exception as e:
                logger.error(f"Error in task handler for {task_id}: {str(e)}")
                # Mark the task as failed
                error_data = {"error": str(e), "status": "failed"}
                self.complete_task(task_id, error_data)
        elif self._default_handler:
            # Call the default handler
            try:
                result = self._default_handler(task_id, task_data)
                self.complete_task(task_id, result)
                logger.info(f"Task {task_id} completed with default handler")
            except Exception as e:
                logger.error(f"Error in default task handler for {task_id}: {str(e)}")
                error_data = {"error": str(e), "status": "failed"}
                self.complete_task(task_id, error_data)
        else:
            # No handler for this task type
            logger.warning(f"No handler for task type: {task_type}")
            error_data = {"error": f"No handler for task type: {task_type}", "status": "rejected"}
            self.complete_task(task_id, error_data) 