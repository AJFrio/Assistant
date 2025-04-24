"""
Configuration management for the Assistant application.
Centralizes all environment variables and configuration settings.
"""
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class Config:
    """Singleton class to manage application configuration."""
    
    _instance = None
    _initialized = False
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._load_config()
            self._initialized = True
    
    def _load_config(self) -> None:
        """Load configuration from environment variables."""
        # Load environment variables from .env file
        load_dotenv()
        
        # API Keys
        self._config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
        self._config['ANTHROPIC_API_KEY'] = os.getenv('ANTHROPIC_API_KEY')
        
        # Firebase Configuration
        self._config['FIREBASE_PROJECT_ID'] = os.getenv('FIREBASE_PROJECT_ID')
        self._config['FIREBASE_API_KEY'] = os.getenv('FIREBASE_API_KEY')
        self._config['DESCRIPTOR'] = os.getenv('DESCRIPTOR')
        
        # Application Configuration
        self._config['ASSISTANT_NAME'] = os.getenv('ASSISTANT_NAME', 'CAS-E')
        self._config['ASSISTANT_ID'] = os.getenv('ASSISTANT_ID', '(Central Automated System - Epic)')
        
        # Poll interval for Firebase tasks (in seconds)
        self._config['TASK_POLL_INTERVAL'] = int(os.getenv('TASK_POLL_INTERVAL', '300'))
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self._config[key] = value
    
    def validate_required_keys(self, keys: list) -> Optional[str]:
        """Validate that all required keys are present and not empty."""
        missing_keys = []
        for key in keys:
            if not self._config.get(key):
                missing_keys.append(key)
        
        if missing_keys:
            return f"Missing required configuration: {', '.join(missing_keys)}"
        return None


# Singleton instance to be imported by other modules
config = Config() 