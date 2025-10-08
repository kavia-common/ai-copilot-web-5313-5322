"""
Gemini API service wrapper for generating AI responses.
Handles communication with Google's Generative AI API.
"""
import os
from typing import List, Dict, Any
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
        Optionally reads GEMINI_MODEL to select a model; defaults to "gemini-1.5-flash".
        
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
        
        # Initialize the model using environment variable with sensible default
        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.model = genai.GenerativeModel(model_name)
    
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

    # PUBLIC_INTERFACE
    def list_models(self) -> List[Dict[str, Any]]:
        """
        List available Gemini models for the configured API key.

        Returns:
            A list of concise model descriptions containing:
            - name: API model name
            - displayName: Human-readable name
            - inputTokenLimit: Max input tokens (if provided by API)
            - outputTokenLimit: Max output tokens (if provided by API)
            - supportedGenerationMethods: Supported methods like 'generateContent', 'embedContent'
        
        Raises:
            Exception: If the SDK call fails
        """
        try:
            models = genai.list_models()  # returns an iterable of Model objects
            results: List[Dict[str, Any]] = []

            for m in models:
                # Some fields may be missing on certain models; default safely
                model_info = {
                    "name": getattr(m, "name", None),
                    "displayName": getattr(m, "display_name", None) or getattr(m, "displayName", None),
                    "inputTokenLimit": getattr(m, "input_token_limit", None) or getattr(m, "inputTokenLimit", None),
                    "outputTokenLimit": getattr(m, "output_token_limit", None) or getattr(m, "outputTokenLimit", None),
                    "supportedGenerationMethods": list(getattr(m, "supported_generation_methods", []) or getattr(m, "supportedGenerationMethods", []) or []),
                }

                # Only include models that expose a name (usable via API)
                if model_info["name"]:
                    results.append(model_info)

            return results
        except Exception as e:
            raise Exception(f"Failed to list Gemini models: {str(e)}") from e
