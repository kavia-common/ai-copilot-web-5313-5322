"""
Gemini API service wrapper for generating AI responses.
Handles communication with Google's Generative AI API.
"""
import os
from typing import List, Dict
import google.generativeai as genai


# PUBLIC_INTERFACE
class GeminiService:
    """
    Service for interacting with Google's Gemini API.
    
    Handles API key configuration, client initialization,
    and generation of AI responses based on conversation history.
    """
    
    def __init__(self):
        """
        Initialize the Gemini service.
        
        Reads GEMINI_API_KEY from environment variables and configures the client.
        
        Raises:
            ValueError: If GEMINI_API_KEY is not set in environment variables
        """
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is not set. "
                "Please set it in your .env file or environment. "
                "Get your API key from https://makersuite.google.com/app/apikey"
            )
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        
        # Initialize the model (using gemini-pro as default)
        self.model = genai.GenerativeModel('gemini-pro')
    
    # PUBLIC_INTERFACE
    def generate_reply(
        self,
        history: List[Dict[str, str]],
        user_message: str
    ) -> str:
        """
        Generate an AI reply based on conversation history and new user message.
        
        Args:
            history: List of previous messages with 'role' and 'content' keys
            user_message: New message from the user
            
        Returns:
            AI-generated response string
            
        Raises:
            Exception: If API call fails or returns invalid response
        """
        try:
            # Convert history to Gemini format
            chat_history = []
            for msg in history:
                role = msg.get("role", "")
                content = msg.get("content", "")
                
                # Map roles: 'assistant' -> 'model', 'user' -> 'user'
                gemini_role = "model" if role == "assistant" else "user"
                chat_history.append({
                    "role": gemini_role,
                    "parts": [content]
                })
            
            # Start a chat with the history
            chat = self.model.start_chat(history=chat_history)
            
            # Send the new message and get response
            response = chat.send_message(user_message)
            
            # Extract the text from the response
            if response and response.text:
                return response.text
            else:
                raise Exception("Received empty response from Gemini API")
                
        except Exception as e:
            # Log and re-raise with context
            error_message = f"Error generating reply from Gemini API: {str(e)}"
            raise Exception(error_message) from e
    
    # PUBLIC_INTERFACE
    def is_configured(self) -> bool:
        """
        Check if the service is properly configured with an API key.
        
        Returns:
            True if API key is set, False otherwise
        """
        return bool(self.api_key)
