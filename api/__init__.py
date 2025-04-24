"""
API package for the Assistant application.
Contains client modules for Firebase, OpenAI, and Anthropic services.
"""
from api.firebase import Firebase
from api.openai import openai_client
from api.anthropic import anthropic_client

__all__ = [
    'Firebase',
    'openai_client',
    'anthropic_client'
] 