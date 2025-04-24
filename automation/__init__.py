"""
Automation package for the Assistant application.
Contains modules for system, application, and browser automation.
"""
from automation.system import (
    run_command,
    get_system_info,
    list_running_processes,
    check_file_exists,
    check_directory_exists,
    list_directory_contents,
    create_directory
)
from automation.applications import (
    open_app,
    get_open_windows,
    focus_application,
    move_mouse,
    click,
    type_text,
    press_key,
    hotkey,
    take_screenshot
)
from automation.browser import (
    BrowserAutomation,
    fetch_webpage_content
)

__all__ = [
    # System automation
    'run_command',
    'get_system_info',
    'list_running_processes',
    'check_file_exists',
    'check_directory_exists',
    'list_directory_contents',
    'create_directory',
    
    # Application automation
    'open_app',
    'get_open_windows',
    'focus_application',
    'move_mouse',
    'click',
    'type_text',
    'press_key',
    'hotkey',
    'take_screenshot',
    
    # Browser automation
    'BrowserAutomation',
    'fetch_webpage_content'
] 