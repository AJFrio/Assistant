import requests
import json
import socket
import os
import dotenv

class Firebase:
    def __init__(self, load_env=True, verify_ssl=False):
        """
        Initialize Firebase Realtime Database client
        
        Args:
            load_env (bool): Whether to load environment variables from .env file
            verify_ssl (bool): Whether to verify SSL certificates
        """
        if load_env:
            dotenv.load_dotenv()
            
        self.project_id = os.getenv("FIREBASE_PROJECT_ID")
        self.api_key = os.getenv("FIREBASE_API_KEY")
        self.computer_name = socket.gethostname()
        self.base_url = f"https://{self.project_id}-default-rtdb.firebaseio.com"
        self.verify_ssl = verify_ssl
        
    def update_status(self, status="on"):
        """
        Update the status of this computer in the database
        
        Args:
            status (str): Status to set ("on" or "off")
            
        Returns:
            dict: Response from Firebase
        """
        url = f"{self.base_url}/devices/{self.computer_name}.json"
        params = {"auth": self.api_key}
        
        data = {
            "status": status,
            "last_seen": {".sv": "timestamp"},
            "tasks": {} if status == "on" else None  # Initialize tasks if online
        }
        
        response = requests.put(url, json=data, params=params, verify=self.verify_ssl)
        
        if response.status_code == 200:
            print(f"Set status for {self.computer_name} to '{status}'")
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
    
    def get_tasks(self):
        """
        Get tasks assigned to this computer
        
        Returns:
            dict: Tasks or None if no tasks found
        """
        url = f"{self.base_url}/devices/{self.computer_name}/tasks.json"
        params = {"auth": self.api_key}
        
        response = requests.get(url, params=params, verify=self.verify_ssl)
        
        if response.status_code == 200:
            tasks = response.json()
            return tasks if tasks else {}
        else:
            print(f"Error getting tasks: {response.status_code}")
            print(response.text)
            return {}
    
    def add_task_to_computer(self, target_computer, task_type, task_params=None):
        """
        Add a task to another computer's queue
        
        Args:
            target_computer (str): Name of the computer to add the task to
            task_type (str): Type of task to add
            task_params (any): Parameters for the task
            
        Returns:
            dict: Response from Firebase
        """
        url = f"{self.base_url}/devices/{target_computer}/tasks.json"
        params = {"auth": self.api_key}
        
        # Generate a unique task ID based on timestamp
        import time
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
        
        response = requests.patch(url, json=data, params=params, verify=self.verify_ssl)
        
        if response.status_code == 200:
            print(f"Added task {task_type} to {target_computer}")
            return response.json()
        else:
            print(f"Error adding task: {response.status_code}")
            print(response.text)
            return None
    
    def complete_task(self, task_id, result=None):
        """
        Mark a task as completed and remove it from the queue
        
        Args:
            task_id (str): ID of the task to complete
            result (any): Optional result data
            
        Returns:
            bool: True if successful, False otherwise
        """
        url = f"{self.base_url}/devices/{self.computer_name}/tasks/{task_id}.json"
        params = {"auth": self.api_key}
        
        # Delete the task
        response = requests.delete(url, params=params, verify=self.verify_ssl)
        
        if response.status_code == 200:
            print(f"Completed and removed task {task_id}")
            
            # If there's a result, store it in a completed_tasks collection
            if result is not None:
                completed_url = f"{self.base_url}/completed_tasks/{self.computer_name}/{task_id}.json"
                completed_data = {
                    "result": result,
                    "completed_at": {".sv": "timestamp"}
                }
                requests.put(completed_url, json=completed_data, params=params, verify=self.verify_ssl)
                
            return True
        else:
            print(f"Error completing task: {response.status_code}")
            print(response.text)
            return False
            
    def get_computer_status(self, computer_name):
        """
        Get the status of another computer
        
        Args:
            computer_name (str): Name of the computer to check
            
        Returns:
            dict: Computer status data or None if not found
        """
        url = f"{self.base_url}/devices/{computer_name}.json"
        params = {"auth": self.api_key}
        
        response = requests.get(url, params=params, verify=self.verify_ssl)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting status: {response.status_code}")
            print(response.text)
            return None

# Example usage when run directly
