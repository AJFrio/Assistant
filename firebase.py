import requests
import json
import socket
import os
import dotenv
import time
import threading

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
            
        try:
            self.project_id = os.getenv("FIREBASE_PROJECT_ID")
            self.api_key = os.getenv("FIREBASE_API_KEY")
            self.descriptor = os.getenv("DESCRIPTOR")
            
            if not self.project_id or not self.api_key:
                raise ValueError("Missing required environment variables: FIREBASE_PROJECT_ID or FIREBASE_API_KEY")
                
            self.computer_name = socket.gethostname()
            self.base_url = f"https://{self.project_id}-default-rtdb.firebaseio.com"
            self.verify_ssl = verify_ssl
            
            # For task polling
            self._polling_thread = None
            self._polling_active = False
            self._task_handlers = {}
            
            # Update descriptor if available
            if self.descriptor:
                self._update_descriptor()
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            raise
        
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
        
        # Include descriptor if available
        if hasattr(self, 'descriptor') and self.descriptor:
            data["descriptor"] = self.descriptor
        
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
    
    def get_all_computers(self):
        """
        Get the names of all computers in the database
        
        Returns:
            list: List of computer names or empty list if none found
        """
        url = f"{self.base_url}/devices.json"
        params = {"auth": self.api_key, "shallow": "true"}
        
        response = requests.get(url, params=params, verify=self.verify_ssl)
        
        if response.status_code == 200:
            devices = response.json()
            if devices:
                return list(devices.keys())
            return []
        else:
            print(f"Error getting computers: {response.status_code}")
            print(response.text)
            return []
            
    def _update_descriptor(self):
        """
        Update the descriptor for this computer in the database if it doesn't exist
        or is different from the current descriptor
        """
        url = f"{self.base_url}/devices/{self.computer_name}.json"
        params = {"auth": self.api_key}
        
        # First check if the descriptor already exists and matches current value
        response = requests.get(url, params=params, verify=self.verify_ssl)
        
        if response.status_code == 200:
            current_data = response.json()
            
            # Check if descriptor exists and is the same
            if current_data and 'descriptor' in current_data and current_data['descriptor'] == self.descriptor:
                print(f"Descriptor for {self.computer_name} already up to date: '{self.descriptor}'")
                return
        
        # Update the descriptor
        data = {"descriptor": self.descriptor}
        response = requests.patch(url, json=data, params=params, verify=self.verify_ssl)
        
        if response.status_code == 200:
            print(f"Updated descriptor for {self.computer_name} to '{self.descriptor}'")
        else:
            print(f"Error updating descriptor: {response.status_code}")
            print(response.text)

    def start_task_polling(self, interval=60, default_handler=None):
        """
        Start polling for tasks in a background thread
        
        Args:
            interval (int): Polling interval in seconds
            default_handler (callable): Default handler for tasks without specific handlers
                                       Function should accept (task_id, task_data) parameters
                                       
        Returns:
            bool: True if polling started, False if already running
        """
        if self._polling_active:
            print("Task polling is already active")
            return False
        
        self._polling_active = True
        self._default_handler = default_handler
        
        # Create and start the polling thread
        self._polling_thread = threading.Thread(
            target=self._poll_tasks_worker,
            args=(interval,),
            daemon=True
        )
        self._polling_thread.start()
        print(f"Started task polling with {interval}s interval")
        return True
    
    def stop_task_polling(self):
        """
        Stop the task polling thread
        
        Returns:
            bool: True if polling was stopped, False if not running
        """
        if not self._polling_active:
            print("Task polling is not active")
            return False
        
        self._polling_active = False
        if self._polling_thread and self._polling_thread.is_alive():
            self._polling_thread.join(timeout=1.0)
        
        print("Stopped task polling")
        return True
    
    def register_task_handler(self, task_type, handler_function):
        """
        Register a handler function for a specific task type
        
        Args:
            task_type (str): The type of task to handle
            handler_function (callable): Function to call when task is received
                                         Function should accept (task_id, task_data) parameters
        """
        self._task_handlers[task_type] = handler_function
        print(f"Registered handler for '{task_type}' tasks")
    
    def _poll_tasks_worker(self, interval):
        """
        Worker thread function that polls for tasks
        
        Args:
            interval (int): Polling interval in seconds
        """
        while self._polling_active:
            try:
                tasks = self.get_tasks()
                if tasks and isinstance(tasks, dict):
                    for task_id, task_data in tasks.items():
                        self._handle_task(task_id, task_data)
            except Exception as e:
                print(f"Error in task polling: {e}")
            
            # Sleep for the interval
            time_slept = 0
            while time_slept < interval and self._polling_active:
                time.sleep(1)
                time_slept += 1
    
    def _handle_task(self, task_id, task_data):
        """
        Process a task with the appropriate handler
        
        Args:
            task_id (str): ID of the task
            task_data (dict): Task data
        """
        try:
            task_type = task_data.get('type')
            if not task_type:
                print(f"Warning: Task {task_id} has no type, skipping")
                return
            
            # Find the appropriate handler
            handler = self._task_handlers.get(task_type)
            
            if handler:
                # Call the task-specific handler
                result = handler(task_id, task_data)
                # Complete the task if the handler returned a result
                if result is not None:
                    self.complete_task(task_id, result)
            elif self._default_handler:
                # Call the default handler
                result = self._default_handler(task_id, task_data)
                # Complete the task if the handler returned a result
                if result is not None:
                    self.complete_task(task_id, result)
            else:
                print(f"No handler registered for task type '{task_type}' and no default handler")
        except Exception as e:
            print(f"Error handling task {task_id}: {e}")

# Example usage when run directly
if __name__ == "__main__":
    import sys
    
    # Example task handlers
    def handle_echo_task(task_id, task_data):
        print(f"Echo task received: {task_data}")
        message = task_data.get('params', {}).get('message', 'No message')
        print(f"Message: {message}")
        return {"echoed": message}
    
    def handle_default_task(task_id, task_data):
        print(f"Default handler processing task: {task_id}")
        print(f"Task data: {task_data}")
        return {"status": "processed by default handler"}
    
    # Initialize Firebase client
    firebase = Firebase()
    
    # Register task handlers
    firebase.register_task_handler("echo", handle_echo_task)
    
    # Usage example
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "poll":
            # Start polling for tasks
            firebase.update_status("on")  # Set status to online
            firebase.start_task_polling(interval=10, default_handler=handle_default_task)
            
            try:
                print("Polling for tasks. Press Ctrl+C to stop.")
                # Keep the main thread alive
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("Stopping...")
            finally:
                firebase.stop_task_polling()
                firebase.update_status("off")  # Set status to offline
                
        elif command == "add-task":
            # Add a task to another computer
            target = sys.argv[2] if len(sys.argv) > 2 else firebase.computer_name
            message = sys.argv[3] if len(sys.argv) > 3 else "Hello from Firebase!"
            
            firebase.add_task_to_computer(
                target_computer=target,
                task_type="echo",
                task_params={"message": message}
            )
            print(f"Added echo task to {target}")
            
        elif command == "status":
            # Update status
            status = sys.argv[2] if len(sys.argv) > 2 else "on"
            firebase.update_status(status)
            print(f"Updated status to {status}")
            
        else:
            print(f"Unknown command: {command}")
            print("Available commands: poll, add-task, status")
    else:
        print("Usage:")
        print("  python firebase.py poll - Start polling for tasks")
        print("  python firebase.py add-task [computer_name] [message] - Add an echo task")
        print("  python firebase.py status [on|off] - Update computer status")
