"""
Utilities package for the Assistant application.
Contains helper modules for common operations.
"""
from utils.image import (
    take_screenshot,
    image_to_base64,
    base64_to_image,
    highlight_region,
    resize_image
)

__all__ = [
    'take_screenshot',
    'image_to_base64',
    'base64_to_image',
    'highlight_region',
    'resize_image'
] 