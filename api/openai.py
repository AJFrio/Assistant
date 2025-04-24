"""
OpenAI API client for the Assistant application.
Manages interaction with OpenAI API services.
"""
from typing import Dict, Any, List, Optional, Union
import json
import openai

from core.config import config
from core.logging import get_logger
from core.exceptions import OpenAIError, ConfigurationError

# Configure logger
logger = get_logger(__name__)


class OpenAIClient:
    """Client for interacting with OpenAI API."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(OpenAIClient, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize OpenAI client."""
        if self._initialized:
            return
            
        try:
            # Get OpenAI API key from config
            api_key = config.get("OPENAI_API_KEY")
            if not api_key:
                raise ConfigurationError("Missing OpenAI API key")
                
            # Initialize OpenAI client
            self.client = openai.OpenAI(api_key=api_key)
            self._initialized = True
            logger.info("OpenAI client initialized")
            
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {str(e)}")
            raise OpenAIError(f"OpenAI initialization error: {str(e)}")
    
    def generate_chat_completion(self, 
                             system_message: str,
                             user_message: str,
                             model: str = "gpt-4o-mini",
                             max_tokens: int = 1000,
                             temperature: float = 0.7,
                             tools: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Generate a chat completion response
        
        Args:
            system_message (str): System message for the conversation
            user_message (str): User message for the conversation
            model (str): Model to use for completion
            max_tokens (int): Maximum tokens to generate
            temperature (float): Temperature for generation
            tools (list, optional): Tools for function calling
            
        Returns:
            str: Generated completion text
            
        Raises:
            OpenAIError: If the API request fails
        """
        try:
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
            
            completion_args = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            # Add tools if provided
            if tools:
                completion_args["tools"] = tools
            
            response = self.client.chat.completions.create(**completion_args)
            
            # Extract the completion text
            completion_text = response.choices[0].message.content
            logger.info(f"Generated completion with {len(completion_text)} characters")
            
            return completion_text
            
        except Exception as e:
            logger.error(f"Error generating chat completion: {str(e)}")
            raise OpenAIError(f"OpenAI API error: {str(e)}")
    
    def generate_with_function_calling(self,
                                  system_message: str,
                                  user_message: str,
                                  tools: List[Dict[str, Any]],
                                  model: str = "gpt-4o-mini") -> Dict[str, Any]:
        """
        Generate a response with function calling
        
        Args:
            system_message (str): System message for the conversation
            user_message (str): User message for the conversation
            tools (list): Tools for function calling
            model (str): Model to use for completion
            
        Returns:
            dict: Response with function call information
            
        Raises:
            OpenAIError: If the API request fails
        """
        try:
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
            
            # Check if there's a function call
            message = response.choices[0].message
            
            # Return the full message for processing
            return {
                "content": message.content,
                "tool_calls": message.tool_calls
            }
            
        except Exception as e:
            logger.error(f"Error generating function call: {str(e)}")
            raise OpenAIError(f"OpenAI API error: {str(e)}")


# Singleton instance to be imported by other modules
openai_client = OpenAIClient() 