#!/usr/bin/env python3
"""
Anthropic Client - Shared AI Communication Infrastructure

This class provides a unified interface to interact with Anthropic's Claude API.
It abstracts the complexity of API calls and provides a simple interface for
all components to generate AI responses.

Key responsibilities:
- Manage API connection and authentication
- Handle system and user prompts consistently
- Provide error handling for API failures
- Abstract API specifics from business logic components
"""
import os
import anthropic
from dotenv import load_dotenv
from typing import Optional


class AnthropicClient:
    """
    Shared client for all components to interact with Anthropic's Claude API.
    
    This class encapsulates all API communication logic, allowing components
    to focus on their business logic while delegating AI interactions to this
    centralized service.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Anthropic client with API key.
        
        Args:
            api_key (Optional[str]): API key for Anthropic. If None, loads from environment.
                                   
        Raises:
            ValueError: If API key is not provided and not found in environment.
        """
        self._load_api_key(api_key)
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def _load_api_key(self, provided_key: Optional[str]) -> None:
        """
        Load API key from parameter or environment variables.
        
        Args:
            provided_key (Optional[str]): API key provided directly
            
        Raises:
            ValueError: If no API key is found
        """
        if provided_key:
            self.api_key = provided_key
        else:
            load_dotenv()
            self.api_key = os.getenv('ANTHROPIC_API_KEY')
            
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be provided or set in environment variables")
    
    def generate_response(self, system_prompt: str, user_prompt: str, model: str = "claude-3-haiku-20240307") -> str:
        """
        Generate a response from Claude using system and user prompts.
        
        This is the main interface for all components to interact with Claude.
        Each component can provide its specific role context via system_prompt
        and the actual input via user_prompt.
        
        Args:
            system_prompt (str): Context and role definition for Claude
                                Example: "You are a communication component that handles user interactions..."
            user_prompt (str): The actual input/request for Claude
                              Example: "User said: 'I need a login system'"
            model (str): Claude model to use (default: haiku for cost efficiency)
            
        Returns:
            str: Claude's response text
            
        Raises:
            Exception: If API call fails, prints error and re-raises
        """
        try:
            message = self.client.messages.create(
                model=model,
                max_tokens=2000,
                temperature=0.3,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            return message.content[0].text.strip()
            
        except Exception as e:
            # Print error for debugging (not same as user communication)
            print(f"ERROR: Anthropic API call failed: {str(e)}")
            raise
    
    def is_api_available(self) -> bool:
        """
        Check if the API is available and credentials are valid.
        
        Useful for health checks and initialization validation.
        
        Returns:
            bool: True if API is accessible, False otherwise
        """
        try:
            # Simple test call to verify connectivity
            self.generate_response(
                system_prompt="You are a test assistant.",
                user_prompt="Say 'OK' if you can hear me."
            )
            return True
        except Exception:
            return False