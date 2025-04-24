"""
Task processor for the Assistant application.
Manages task scheduling, execution, and result handling.
"""
from typing import Dict, Any, Optional, List, Union, Callable
import threading
import queue
import time

from core.logging import get_logger
from core.exceptions import TaskError
from tasks.handlers import get_handler_for_task_type

# Configure logger
logger = get_logger(__name__)


class TaskProcessor:
    """Processes tasks in a dedicated thread."""
    
    def __init__(self):
        """Initialize task processor."""
        self.task_queue = queue.Queue()
        self._processing_thread = None
        self._processing_active = False
        self._results_cache: Dict[str, Dict[str, Any]] = {}
        self._max_cache_size = 100
    
    def start_processing(self) -> bool:
        """
        Start processing tasks in a background thread
        
        Returns:
            bool: True if started, False if already running
        """
        if self._processing_active:
            logger.warning("Task processor is already running")
            return False
            
        self._processing_active = True
        self._processing_thread = threading.Thread(
            target=self._process_tasks_worker,
            daemon=True
        )
        self._processing_thread.start()
        logger.info("Task processor started")
        return True
    
    def stop_processing(self) -> bool:
        """
        Stop processing tasks
        
        Returns:
            bool: True if stopped, False if not running
        """
        if not self._processing_active:
            logger.warning("Task processor is not running")
            return False
            
        self._processing_active = False
        if self._processing_thread:
            self._processing_thread.join(timeout=1.0)
            self._processing_thread = None
        logger.info("Task processor stopped")
        return True
    
    def add_task(self, task_id: str, task_type: str, 
                params: Optional[Union[Dict[str, Any], str]] = None, 
                priority: int = 0) -> bool:
        """
        Add a task to the processing queue
        
        Args:
            task_id (str): Unique ID for the task
            task_type (str): Type of task to execute
            params (dict or str, optional): Parameters for the task
            priority (int): Task priority (higher is more important)
            
        Returns:
            bool: True if the task was added
        """
        # Create task data
        task_data = {
            "id": task_id,
            "type": task_type,
            "params": params,
            "status": "pending",
            "created_at": time.time(),
            "priority": priority
        }
        
        # Add to queue
        try:
            self.task_queue.put((priority, task_data))
            logger.info(f"Added task {task_id} of type {task_type} to queue")
            return True
        except Exception as e:
            logger.error(f"Error adding task to queue: {str(e)}")
            return False
    
    def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the result of a completed task
        
        Args:
            task_id (str): ID of the task
            
        Returns:
            dict or None: Task result or None if not found
        """
        return self._results_cache.get(task_id)
    
    def _process_tasks_worker(self) -> None:
        """Worker function for task processing thread."""
        logger.info("Task processing worker started")
        
        while self._processing_active:
            try:
                # Get task from queue with timeout
                try:
                    # Use priority queue (lower number = higher priority)
                    priority, task_data = self.task_queue.get(timeout=1.0)
                    task_id = task_data.get("id")
                    task_type = task_data.get("type")
                    
                    # Update task status
                    task_data["status"] = "processing"
                    task_data["started_at"] = time.time()
                    
                    # Execute task
                    logger.info(f"Processing task {task_id} of type {task_type}")
                    result = self._execute_task(task_id, task_type, task_data)
                    
                    # Update task status and store result
                    task_data["status"] = "completed"
                    task_data["completed_at"] = time.time()
                    task_data["result"] = result
                    
                    # Add to results cache
                    self._cache_result(task_id, task_data)
                    
                    # Mark as done in queue
                    self.task_queue.task_done()
                    logger.info(f"Task {task_id} completed")
                    
                except queue.Empty:
                    # No tasks in queue
                    pass
                    
            except Exception as e:
                logger.error(f"Error in task processor: {str(e)}")
                # Sleep briefly before continuing
                time.sleep(0.1)
    
    def _execute_task(self, task_id: str, task_type: str, 
                     task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task
        
        Args:
            task_id (str): ID of the task
            task_type (str): Type of task
            task_data (dict): Task data
            
        Returns:
            dict: Task result
        """
        try:
            # Get handler for task type
            handler = get_handler_for_task_type(task_type)
            
            if not handler:
                error_msg = f"No handler for task type: {task_type}"
                logger.error(error_msg)
                return {"error": error_msg, "status": "failed"}
            
            # Execute handler
            result = handler(task_id, task_data)
            return result
            
        except TaskError as e:
            logger.error(f"Task error for {task_id}: {str(e)}")
            return {"error": str(e), "status": "failed", "details": e.details if hasattr(e, "details") else None}
        except Exception as e:
            logger.error(f"Unexpected error for task {task_id}: {str(e)}")
            return {"error": str(e), "status": "failed"}
    
    def _cache_result(self, task_id: str, result: Dict[str, Any]) -> None:
        """
        Cache task result
        
        Args:
            task_id (str): ID of the task
            result (dict): Task result
        """
        # Add to cache
        self._results_cache[task_id] = result
        
        # Trim cache if needed
        if len(self._results_cache) > self._max_cache_size:
            # Remove oldest entries
            oldest_keys = sorted(self._results_cache.keys(), 
                               key=lambda k: self._results_cache[k].get("completed_at", 0))
            for key in oldest_keys[:len(oldest_keys) - self._max_cache_size]:
                del self._results_cache[key]


# Singleton instance to be imported by other modules
task_processor = TaskProcessor() 