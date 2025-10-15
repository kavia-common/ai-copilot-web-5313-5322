"""
FastAPI main application for AI Copilot Backend.
Provides REST API endpoints for session-based chat using Google Gemini API.
"""
import uuid
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from src.models.schemas import (
    ChatRequest,
    ChatResponse,
    SessionCreateResponse,
    Message,
    HistoryResponse,
    ModelsListResponse
)
from src.services.gemini_service import GeminiService
from src.services.session_manager import SessionManager

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app with metadata
app = FastAPI(
    title="AI Copilot Backend API",
    description="Backend API for AI Copilot web application with session-based chat using Google Gemini API",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "health",
            "description": "Health check endpoints"
        },
        {
            "name": "sessions",
            "description": "Session management operations"
        },
        {
            "name": "chat",
            "description": "Chat operations with AI assistant"
        },
        {
            "name": "models",
            "description": "Model discovery and capabilities"
        }
    ]
)

# -----------------------------------------------------------------------------
# CORS Configuration
# -----------------------------------------------------------------------------
# PUBLIC NOTE:
# CORS behavior can be customized via:
#   - CORS_ALLOWED_ORIGINS: Comma-separated list of exact origins to allow
#   - CORS_ALLOW_ORIGIN_REGEX: Optional regex to allow origin patterns
#
# Defaults below allow:
#   - http://localhost / http://127.0.0.1 (any port)
#   - https://<any-subdomain>.beta01.cloud.kavia.ai (any port)
#
# For the current deployment, the frontend runs at:
#   https://vscode-internal-13141-beta.beta01.cloud.kavia.ai:3000
# and the backend at:
#   https://vscode-internal-13141-beta.beta01.cloud.kavia.ai:3001
#
# We intentionally set:
#   - allow_credentials=False (no cookies used)
#   - allow_methods=["GET", "POST", "OPTIONS"]
#   - allow_headers=["Content-Type", "Authorization"]
# -----------------------------------------------------------------------------
allowed_origins_env = os.getenv("CORS_ALLOWED_ORIGINS", "").strip()
allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

default_origin_regex = (
    r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"
    r"|^https://[a-z0-9-]+\.beta01\.cloud\.kavia\.ai(:\d+)?$"
)

allowed_origin_regex_env = os.getenv("CORS_ALLOW_ORIGIN_REGEX", "").strip()
origin_regex_to_use = allowed_origin_regex_env or default_origin_regex

cors_kwargs = {
    # We are not using cookies; keep credentials disabled
    "allow_credentials": False,
    # Restrict to standard browser methods including preflight
    "allow_methods": ["GET", "POST", "OPTIONS"],
    # Only allow necessary headers for typical API calls
    "allow_headers": ["Content-Type", "Authorization"],
    # Use regex to safely allow wildcard subdomains on beta01.cloud.kavia.ai
    "allow_origin_regex": origin_regex_to_use,
}

# If explicit origins are provided, include them alongside the regex
if allowed_origins:
    cors_kwargs["allow_origins"] = allowed_origins

app.add_middleware(CORSMiddleware, **cors_kwargs)

# Initialize services
session_manager = SessionManager()

# Initialize Gemini service (will raise error if API key not set)
try:
    gemini_service = GeminiService()
except ValueError as e:
    # Avoid crashing the app; endpoints will respond with helpful errors
    print(f"Warning: {e}")
    gemini_service = None


# PUBLIC_INTERFACE
@app.get(
    "/",
    tags=["health"],
    summary="Health check",
    description="Check if the API is running and healthy"
)
def health_check():
    """
    Health check endpoint.

    Returns:
        dict: Health status message
    """
    return {"status": "healthy", "message": "AI Copilot Backend API is running"}


# PUBLIC_INTERFACE
@app.get(
    "/health",
    tags=["health"],
    summary="Health check",
    description="Secondary health endpoint for uptime monitors and load balancers"
)
def health_check_alt():
    """
    Secondary health check endpoint.

    Returns:
        dict: Health status message (same as root health check)
    """
    return {"status": "healthy", "message": "AI Copilot Backend API is running"}


# PUBLIC_INTERFACE
@app.post(
    "/api/sessions",
    response_model=SessionCreateResponse,
    status_code=status.HTTP_200_OK,
    tags=["sessions"],
    summary="Create a new chat session",
    description="Creates a new chat session with a unique UUID identifier"
)
def create_session():
    """
    Create a new chat session.

    Generates a unique session ID and initializes an empty message history.

    Returns:
        SessionCreateResponse: Object containing the new session_id
    """
    session_id = str(uuid.uuid4())
    session_manager.create_session(session_id)

    return SessionCreateResponse(session_id=session_id)


# PUBLIC_INTERFACE
@app.post(
    "/api/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    tags=["chat"],
    summary="Send a chat message",
    description="Send a message to the AI assistant and receive a reply"
)
def chat(request: ChatRequest):
    """
    Send a chat message and get AI response.

    Validates the session, adds the user message to history,
    generates an AI reply using Gemini API, and stores the assistant's response.

    Args:
        request: ChatRequest containing session_id and message

    Returns:
        ChatResponse: Object containing session_id and AI reply

    Raises:
        HTTPException: If session doesn't exist, Gemini service is unavailable,
                      or API call fails
    """
    # Check if Gemini service is available
    if gemini_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemini API is not configured. Please set GEMINI_API_KEY environment variable."
        )

    # Validate session exists
    if not session_manager.session_exists(request.session_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {request.session_id} not found. Please create a session first."
        )

    try:
        # Add user message to history
        session_manager.add_message(
            request.session_id,
            role="user",
            content=request.message
        )

        # Get conversation history
        history = session_manager.get_history(request.session_id)

        # Remove the just-added user message from history for API call
        # (we'll pass it separately)
        history_for_api = history[:-1] if len(history) > 1 else []

        # Generate AI reply
        ai_reply = gemini_service.generate_reply(
            history=history_for_api,
            user_message=request.message
        )

        # Add assistant message to history
        session_manager.add_message(
            request.session_id,
            role="assistant",
            content=ai_reply
        )

        return ChatResponse(
            session_id=request.session_id,
            reply=ai_reply
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating response: {str(e)}"
        )


# PUBLIC_INTERFACE
@app.get(
    "/api/sessions/{session_id}/history",
    response_model=HistoryResponse,
    status_code=status.HTTP_200_OK,
    tags=["sessions"],
    summary="Get session message history",
    description="Retrieve the chronological message history for a given session"
)
def get_session_history(session_id: str):
    """
    Retrieve message history for a session.

    Returns all messages in chronological order for the specified session.

    Args:
        session_id: The session identifier

    Returns:
        HistoryResponse: Object containing session_id and list of messages

    Raises:
        HTTPException: If session doesn't exist
    """
    history = session_manager.get_history(session_id)

    if history is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )

    # Convert history to Message objects
    messages = [
        Message(role=msg["role"], content=msg["content"])
        for msg in history
    ]

    return HistoryResponse(
        session_id=session_id,
        messages=messages
    )


# PUBLIC_INTERFACE
@app.get(
    "/api/models",
    response_model=ModelsListResponse,
    status_code=status.HTTP_200_OK,
    tags=["models"],
    summary="List available Gemini models",
    description="Return a concise list of available Gemini models for the configured API key, including name, displayName, token limits, and supported methods."
)
def list_gemini_models():
    """
    List available Gemini models.

    Reads the GEMINI_API_KEY from the environment via the configured GeminiService
    and uses the SDK to list models. Returns a concise JSON structure.

    Returns:
        ModelsListResponse: Object containing a list of models and total count

    Raises:
        HTTPException:
            - 400 if GEMINI_API_KEY is not set
            - 500 if an error occurs while calling the Gemini API
    """
    # If service couldn't initialize due to missing key, return 400 with a clear message
    if gemini_service is None or not gemini_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GEMINI_API_KEY is missing or not configured. Set it in your environment or .env file."
        )

    try:
        models = gemini_service.list_models()
        return ModelsListResponse(models=models, count=len(models))
    except Exception as e:
        # Avoid leaking sensitive internal details; provide a helpful message
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve Gemini models. Reason: {str(e)}"
        )
