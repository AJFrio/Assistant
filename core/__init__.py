"""
Core package for the Assistant application.
Contains configuration, logging, and exception handling modules.
"""
from core.config import config
from core.logging import get_logger
from core.exceptions import (
    AssistantBaseException,
    ConfigurationError,
    FirebaseError,
    APIError,
    OpenAIError,
    AnthropicError,
    AutomationError,
    TaskError
)

__all__ = [
    'config',
    'get_logger',
    'AssistantBaseException',
    'ConfigurationError',
    'FirebaseError',
    'APIError',
    'OpenAIError',
    'AnthropicError',
    'AutomationError',
    'TaskError'
] 