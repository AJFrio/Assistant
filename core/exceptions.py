"""
Custom exceptions for the Assistant application.
Provides specific exception types for different error scenarios.
"""
from typing import Optional


class AssistantBaseException(Exception):
    """Base exception class for all Assistant-specific exceptions."""
    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ConfigurationError(AssistantBaseException):
    """Exception raised for errors in the application configuration."""
    pass


class FirebaseError(AssistantBaseException):
    """Exception raised for errors in Firebase operations."""
    pass


class APIError(AssistantBaseException):
    """Exception raised for errors in API calls."""
    pass


class OpenAIError(APIError):
    """Exception raised for errors in OpenAI API calls."""
    pass


class AnthropicError(APIError):
    """Exception raised for errors in Anthropic API calls."""
    pass


class AutomationError(AssistantBaseException):
    """Exception raised for errors in automation operations."""
    pass


class TaskError(AssistantBaseException):
    """Exception raised for errors in task handling."""
    pass 