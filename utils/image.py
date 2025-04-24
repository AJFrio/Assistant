"""
Image utilities for the Assistant application.
Handles image processing, capturing, and conversion.
"""
from typing import Optional, Dict, Any, Tuple
import base64
from io import BytesIO
import pyautogui
from PIL import Image, ImageDraw

from core.logging import get_logger

# Configure logger
logger = get_logger(__name__)


def take_screenshot() -> Image.Image:
    """
    Take a screenshot of the entire screen
    
    Returns:
        PIL.Image.Image: Screenshot image
        
    Raises:
        Exception: If the screenshot could not be taken
    """
    try:
        logger.info("Taking screenshot")
        image = pyautogui.screenshot()
        return image
    except Exception as e:
        logger.error(f"Error taking screenshot: {str(e)}")
        raise


def image_to_base64(image: Image.Image, format: str = "PNG") -> str:
    """
    Convert a PIL image to base64 string
    
    Args:
        image (PIL.Image.Image): Image to convert
        format (str): Image format (PNG, JPEG, etc.)
        
    Returns:
        str: Base64-encoded image string
        
    Raises:
        Exception: If the image could not be converted
    """
    try:
        buffered = BytesIO()
        image.save(buffered, format=format)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str
    except Exception as e:
        logger.error(f"Error converting image to base64: {str(e)}")
        raise


def base64_to_image(base64_str: str) -> Image.Image:
    """
    Convert a base64 string to a PIL image
    
    Args:
        base64_str (str): Base64-encoded image string
        
    Returns:
        PIL.Image.Image: Decoded image
        
    Raises:
        Exception: If the image could not be decoded
    """
    try:
        image_data = base64.b64decode(base64_str)
        image = Image.open(BytesIO(image_data))
        return image
    except Exception as e:
        logger.error(f"Error converting base64 to image: {str(e)}")
        raise


def highlight_region(image: Image.Image, 
                   left: int, top: int, right: int, bottom: int, 
                   color: Tuple[int, int, int] = (255, 0, 0),
                   width: int = 3) -> Image.Image:
    """
    Highlight a region in an image
    
    Args:
        image (PIL.Image.Image): Image to highlight
        left (int): Left coordinate
        top (int): Top coordinate
        right (int): Right coordinate
        bottom (int): Bottom coordinate
        color (tuple): RGB color tuple
        width (int): Line width
        
    Returns:
        PIL.Image.Image: Image with highlighted region
    """
    try:
        # Create a copy of the image
        result = image.copy()
        draw = ImageDraw.Draw(result)
        
        # Draw rectangle
        draw.rectangle([(left, top), (right, bottom)], outline=color, width=width)
        
        return result
    except Exception as e:
        logger.error(f"Error highlighting region: {str(e)}")
        return image  # Return original image on error


def resize_image(image: Image.Image, width: Optional[int] = None, 
               height: Optional[int] = None, keep_aspect_ratio: bool = True) -> Image.Image:
    """
    Resize an image
    
    Args:
        image (PIL.Image.Image): Image to resize
        width (int, optional): Target width
        height (int, optional): Target height
        keep_aspect_ratio (bool): Whether to maintain aspect ratio
        
    Returns:
        PIL.Image.Image: Resized image
        
    Raises:
        ValueError: If neither width nor height is provided
    """
    try:
        if width is None and height is None:
            raise ValueError("At least one of width or height must be provided")
            
        current_width, current_height = image.size
        
        if keep_aspect_ratio:
            # Calculate missing dimension
            if width is None:
                width = int(current_width * (height / current_height))
            elif height is None:
                height = int(current_height * (width / current_width))
        
        # Ensure both dimensions are set
        width = width or current_width
        height = height or current_height
        
        # Resize image
        resized_image = image.resize((width, height), Image.LANCZOS)
        return resized_image
        
    except Exception as e:
        logger.error(f"Error resizing image: {str(e)}")
        raise 