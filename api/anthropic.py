"""
Anthropic API client for the Assistant application.
Manages interaction with Claude and other Anthropic services.
"""
from typing import Dict, Any, List, Optional, Union
import json
import anthropic
import base64
import io
from PIL import Image

from core.config import config
from core.logging import get_logger
from core.exceptions import AnthropicError, ConfigurationError

# Configure logger
logger = get_logger(__name__)


class AnthropicClient:
    """Client for interacting with Anthropic Claude API."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AnthropicClient, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Anthropic client."""
        if self._initialized:
            return
            
        try:
            # Get Anthropic API key from config
            api_key = config.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise ConfigurationError("Missing Anthropic API key")
                
            # Initialize Anthropic client
            self.client = anthropic.Anthropic(api_key=api_key)
            self._initialized = True
            logger.info("Anthropic client initialized")
            
        except Exception as e:
            logger.error(f"Error initializing Anthropic client: {str(e)}")
            raise AnthropicError(f"Anthropic initialization error: {str(e)}")
    
    def generate_message(self, 
                        user_message: str,
                        system_message: Optional[str] = None,
                        model: str = "claude-3-5-sonnet-20241022",
                        max_tokens: int = 1024,
                        temperature: float = 0.7,
                        tools: Optional[List[Dict[str, Any]]] = None,
                        image: Optional[Image.Image] = None) -> str:
        """
        Generate a message response from Claude
        
        Args:
            user_message (str): User message for the conversation
            system_message (str, optional): System message for the conversation
            model (str): Model to use for completion
            max_tokens (int): Maximum tokens to generate
            temperature (float): Temperature for generation
            tools (list, optional): Tools for function calling
            image (PIL.Image, optional): Image to include in the message
            
        Returns:
            str: Generated message text
            
        Raises:
            AnthropicError: If the API request fails
        """
        try:
            messages = []
            
            # Add system message if provided
            if system_message:
                messages = [{"role": "system", "content": system_message}]
            
            # Handle images in user message if provided
            if image:
                # Convert image to base64
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                # Create a multi-part message with image
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_message},
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": img_str
                            }
                        }
                    ]
                })
            else:
                # Text-only message
                messages.append({"role": "user", "content": user_message})
            
            # Create message parameters
            message_params = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            # Add tools if provided
            if tools:
                message_params["tools"] = tools
                message_params["betas"] = ["computer-use-2024-10-22"]
            
            # Generate response
            response = self.client.beta.messages.create(**message_params)
            
            # Extract text from response
            response_text = response.content[0].text if response.content else ""
            
            logger.info(f"Generated Claude message with {len(response_text)} characters")
            return response_text
            
        except Exception as e:
            logger.error(f"Error generating Claude message: {str(e)}")
            raise AnthropicError(f"Anthropic API error: {str(e)}")
    
    def generate_with_tools(self,
                          user_message: str,
                          tools: List[Dict[str, Any]],
                          system_message: Optional[str] = None,
                          model: str = "claude-3-5-sonnet-20241022",
                          max_tokens: int = 1024) -> Dict[str, Any]:
        """
        Generate a response with tools (function calling)
        
        Args:
            user_message (str): User message for the conversation
            tools (list): Tools for function calling
            system_message (str, optional): System message for the conversation
            model (str): Model to use for completion
            max_tokens (int): Maximum tokens to generate
            
        Returns:
            dict: Complete response from Claude API
            
        Raises:
            AnthropicError: If the API request fails
        """
        try:
            messages = []
            
            # Add system message if provided
            if system_message:
                messages = [{"role": "system", "content": system_message}]
            
            # Add user message
            messages.append({"role": "user", "content": user_message})
            
            # Generate response with tools
            response = self.client.beta.messages.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                tools=tools,
                betas=["computer-use-2024-10-22"]
            )
            
            # Return the full response for processing
            return response
            
        except Exception as e:
            logger.error(f"Error generating Claude tool response: {str(e)}")
            raise AnthropicError(f"Anthropic API error: {str(e)}")


# Singleton instance to be imported by other modules
anthropic_client = AnthropicClient() 