"""
Task type definitions for the Assistant application.
Defines interfaces and implementations for different task types.
"""
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, field


@dataclass
class TaskDefinition:
    """Base class for task definitions."""
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    required_parameters: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task definition to dictionary format."""
        properties = {}
        for param, param_info in self.parameters.items():
            properties[param] = {
                "type": param_info.get("type", "string"),
                "description": param_info.get("description", "")
            }
            
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": self.required_parameters
                }
            }
        }


# Messaging tasks
@dataclass
class SendMessageTask(TaskDefinition):
    """Send a message using Teams."""
    def __init__(self):
        super().__init__(
            name="send_message",
            description="Used to send a message using teams",
            parameters={
                "message": {
                    "type": "string",
                    "description": "The message to send"
                },
                "person": {
                    "type": "string",
                    "description": "The person to send the message to"
                }
            },
            required_parameters=["message", "person"]
        )


# Application tasks
@dataclass
class OpenAppTask(TaskDefinition):
    """Open an application."""
    def __init__(self):
        super().__init__(
            name="open_app",
            description="Used to open an application",
            parameters={
                "app_name": {
                    "type": "string",
                    "description": "The name of the application to open"
                }
            },
            required_parameters=["app_name"]
        )


# Email tasks
@dataclass
class CheckEmailTask(TaskDefinition):
    """Check recent emails."""
    def __init__(self):
        super().__init__(
            name="check_email",
            description="Used to check most recent emails",
            parameters={},
            required_parameters=[]
        )


@dataclass
class SendEmailTask(TaskDefinition):
    """Send an email."""
    def __init__(self):
        super().__init__(
            name="send_email",
            description="Used to send an email",
            parameters={
                "people": {
                    "type": "string",
                    "description": "The people to send the email to"
                },
                "cc": {
                    "type": "string",
                    "description": "The people to CC in the email"
                },
                "subject": {
                    "type": "string",
                    "description": "The subject of the email"
                },
                "message": {
                    "type": "string",
                    "description": "The message of the email"
                }
            },
            required_parameters=["people", "subject", "message"]
        )


# System tasks
@dataclass
class GetInfoTask(TaskDefinition):
    """Get system information."""
    def __init__(self):
        super().__init__(
            name="get_info",
            description="Used to get information about current date/time, and any system/connection information",
            parameters={
                "input": {
                    "type": "string",
                    "description": "The question to ask"
                }
            },
            required_parameters=["input"]
        )


@dataclass
class RunCommandTask(TaskDefinition):
    """Run a command in terminal."""
    def __init__(self):
        super().__init__(
            name="run_command",
            description="Used to run a command in a PowerShell window",
            parameters={
                "command": {
                    "type": "string",
                    "description": "The command to run"
                }
            },
            required_parameters=["command"]
        )


# Web tasks
@dataclass
class CheckWebsiteTask(TaskDefinition):
    """Check a website for information."""
    def __init__(self):
        super().__init__(
            name="check_website",
            description="Used to check a website for information",
            parameters={
                "url": {
                    "type": "string",
                    "description": "The url to check"
                },
                "context": {
                    "type": "string",
                    "description": "A summary of the question the user asked"
                }
            },
            required_parameters=["url", "context"]
        )


# Tool tasks
@dataclass
class UseCursorTask(TaskDefinition):
    """Use Cursor to complete a task."""
    def __init__(self):
        super().__init__(
            name="use_cursor",
            description="Used to interact with Cursor",
            parameters={
                "prompt": {
                    "type": "string",
                    "description": "The prompt to pass to cursor"
                }
            },
            required_parameters=["prompt"]
        )


# Remote tasks
@dataclass
class AddTaskToComputerTask(TaskDefinition):
    """Add a task to another computer."""
    def __init__(self):
        super().__init__(
            name="add_task_to_computer",
            description="Used to add a function to the queue of another computer",
            parameters={
                "target_computer": {
                    "type": "string",
                    "description": "The name of the computer to add the task to"
                },
                "task_type": {
                    "type": "string",
                    "description": "The type of task to add"
                },
                "task_params": {
                    "type": "string",
                    "description": "The parameters for the task"
                }
            },
            required_parameters=["target_computer", "task_type"]
        )


# Collection of all available tasks
AVAILABLE_TASKS = [
    SendMessageTask(),
    OpenAppTask(),
    CheckEmailTask(),
    SendEmailTask(),
    GetInfoTask(),
    RunCommandTask(),
    CheckWebsiteTask(),
    UseCursorTask(),
    AddTaskToComputerTask()
]

# Export task definitions as a list of dictionaries for AI models
TASK_DEFINITIONS = [task.to_dict() for task in AVAILABLE_TASKS] 