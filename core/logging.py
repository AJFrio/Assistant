"""
Logging configuration for the Assistant application.
Provides a standardized logging setup for all application components.
"""
import logging
import os
import sys
from datetime import datetime
from typing import Optional

# Constants
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class LoggingManager:
    """Manages logging configuration for the application."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggingManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._setup_logging()
            self._initialized = True
    
    def _setup_logging(self) -> None:
        """Set up basic logging configuration."""
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # Set up basic configuration
        logging.basicConfig(
            level=DEFAULT_LOG_LEVEL,
            format=DEFAULT_LOG_FORMAT,
            datefmt=DEFAULT_DATE_FORMAT,
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(f"logs/assistant_{datetime.now().strftime('%Y%m%d')}.log")
            ]
        )
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger instance with the specified name."""
        return logging.getLogger(name)


# Singleton instance to be imported by other modules
logger_manager = LoggingManager()


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name.
    This is a convenience function to get loggers from the singleton manager.
    """
    return logger_manager.get_logger(name) 