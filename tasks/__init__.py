"""
Tasks package for the Assistant application.
Handles task definitions, processing, and execution.
"""
from tasks.types import TASK_DEFINITIONS
from tasks.processor import task_processor
from tasks.handlers import (
    handle_send_message,
    handle_open_app,
    handle_check_email,
    handle_send_email,
    handle_get_info,
    handle_run_command,
    handle_check_website,
    handle_use_cursor,
    get_handler_for_task_type
)

__all__ = [
    'TASK_DEFINITIONS',
    'task_processor',
    'handle_send_message',
    'handle_open_app',
    'handle_check_email',
    'handle_send_email',
    'handle_get_info',
    'handle_run_command',
    'handle_check_website',
    'handle_use_cursor',
    'get_handler_for_task_type'
] 