"""
System automation utilities for the Assistant application.
Handles interactions with the operating system.
"""
import os
import subprocess
from typing import Optional, Dict, Any, List, Tuple

from core.logging import get_logger
from core.exceptions import AutomationError

# Configure logger
logger = get_logger(__name__)


def run_command(command: str) -> str:
    """
    Run a command in the terminal
    
    Args:
        command (str): Command to run
        
    Returns:
        str: Command output
        
    Raises:
        AutomationError: If the command fails
    """
    try:
        logger.info(f"Running command: {command}")
        result = subprocess.run(command, 
                              shell=True, 
                              check=True, 
                              capture_output=True, 
                              text=True)
        logger.info(f"Command completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        error_msg = f"Command failed with exit code {e.returncode}: {e.stderr}"
        logger.error(error_msg)
        raise AutomationError(f"Command execution error", 
                            details={"command": command, "error": error_msg})
    except Exception as e:
        logger.error(f"Error running command: {str(e)}")
        raise AutomationError(f"Command execution error", 
                            details={"command": command, "error": str(e)})


def get_system_info() -> Dict[str, Any]:
    """
    Get system information
    
    Returns:
        dict: System information including OS name, hostname, etc.
    """
    try:
        system_info = {
            "os_name": os.name,
            "platform": os.uname().sysname if hasattr(os, 'uname') else "Windows",
            "hostname": os.environ.get('COMPUTERNAME', 'Unknown'),
            "username": os.environ.get('USERNAME', 'Unknown'),
            "home_dir": os.environ.get('USERPROFILE', 'Unknown'),
        }
        
        # Get network information
        try:
            network_info = run_command("ipconfig")
            system_info["network"] = network_info
        except:
            system_info["network"] = "Failed to retrieve network information"
            
        return system_info
    except Exception as e:
        logger.error(f"Error getting system info: {str(e)}")
        return {"error": str(e)}


def list_running_processes() -> List[Dict[str, Any]]:
    """
    List currently running processes
    
    Returns:
        list: List of running processes with their details
    """
    try:
        if os.name == 'nt':  # Windows
            process_list_output = run_command("tasklist /fo csv /nh")
            processes = []
            for line in process_list_output.strip().split('\n'):
                if line:
                    # Parse CSV format
                    parts = line.strip('"').split('","')
                    if len(parts) >= 2:
                        processes.append({
                            "name": parts[0],
                            "pid": parts[1],
                            "memory": parts[4] if len(parts) > 4 else "Unknown"
                        })
            return processes
        else:  # Unix-like
            process_list_output = run_command("ps -ef")
            processes = []
            for line in process_list_output.strip().split('\n')[1:]:  # Skip header
                if line:
                    parts = line.split()
                    if len(parts) >= 8:
                        processes.append({
                            "user": parts[0],
                            "pid": parts[1],
                            "cpu": parts[2],
                            "mem": parts[3],
                            "start": parts[4],
                            "time": parts[6],
                            "command": ' '.join(parts[7:])
                        })
            return processes
    except Exception as e:
        logger.error(f"Error listing processes: {str(e)}")
        return [{"error": str(e)}]


def check_file_exists(file_path: str) -> bool:
    """
    Check if a file exists
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        bool: True if the file exists, False otherwise
    """
    return os.path.isfile(file_path)


def check_directory_exists(directory_path: str) -> bool:
    """
    Check if a directory exists
    
    Args:
        directory_path (str): Path to the directory
        
    Returns:
        bool: True if the directory exists, False otherwise
    """
    return os.path.isdir(directory_path)


def list_directory_contents(directory_path: str) -> List[str]:
    """
    List contents of a directory
    
    Args:
        directory_path (str): Path to the directory
        
    Returns:
        list: List of file and directory names
        
    Raises:
        AutomationError: If the directory does not exist
    """
    try:
        if not os.path.isdir(directory_path):
            raise AutomationError(f"Directory does not exist: {directory_path}")
            
        return os.listdir(directory_path)
    except Exception as e:
        logger.error(f"Error listing directory contents: {str(e)}")
        raise AutomationError(f"Directory listing error", 
                            details={"directory": directory_path, "error": str(e)})


def create_directory(directory_path: str) -> bool:
    """
    Create a directory if it doesn't exist
    
    Args:
        directory_path (str): Path to the directory
        
    Returns:
        bool: True if the directory was created or already exists
        
    Raises:
        AutomationError: If the directory could not be created
    """
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            logger.info(f"Created directory: {directory_path}")
        return True
    except Exception as e:
        logger.error(f"Error creating directory: {str(e)}")
        raise AutomationError(f"Directory creation error", 
                            details={"directory": directory_path, "error": str(e)}) 