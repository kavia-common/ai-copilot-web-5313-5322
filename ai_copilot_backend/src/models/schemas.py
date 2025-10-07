"""
Pydantic schemas for AI Copilot API request and response validation.
All public models follow OpenAPI standards for documentation.
"""
from typing import List
from pydantic import BaseModel, Field


# PUBLIC_INTERFACE
class ChatRequest(BaseModel):
    """
    Request model for sending a chat message.
    
    Attributes:
        session_id: Unique identifier for the chat session
        message: User's message content to send to the AI
    """
    session_id: str = Field(
        ...,
        description="Unique session identifier for maintaining conversation context",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    message: str = Field(
        ...,
        description="User message to send to the AI assistant",
        example="Can you help me write a Python function?"
    )


# PUBLIC_INTERFACE
class ChatResponse(BaseModel):
    """
    Response model for chat messages.
    
    Attributes:
        session_id: The session identifier for this conversation
        reply: AI-generated response to the user's message
    """
    session_id: str = Field(
        ...,
        description="Session identifier for the conversation",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    reply: str = Field(
        ...,
        description="AI assistant's response message",
        example="Sure! Here's a Python function..."
    )


# PUBLIC_INTERFACE
class SessionCreateResponse(BaseModel):
    """
    Response model for session creation.
    
    Attributes:
        session_id: Newly created unique session identifier
    """
    session_id: str = Field(
        ...,
        description="Newly created unique session identifier",
        example="550e8400-e29b-41d4-a716-446655440000"
    )


# PUBLIC_INTERFACE
class Message(BaseModel):
    """
    Model for a single message in conversation history.
    
    Attributes:
        role: The role of the message sender (user or assistant)
        content: The message content
    """
    role: str = Field(
        ...,
        description="Role of the message sender: 'user' or 'assistant'",
        example="user"
    )
    content: str = Field(
        ...,
        description="Content of the message",
        example="Hello, how can you help me?"
    )


# PUBLIC_INTERFACE
class HistoryResponse(BaseModel):
    """
    Response model for retrieving session message history.
    
    Attributes:
        session_id: The session identifier
        messages: Chronological list of messages in the conversation
    """
    session_id: str = Field(
        ...,
        description="Session identifier",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    messages: List[Message] = Field(
        ...,
        description="Chronological list of messages in the conversation",
        example=[
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hi! How can I help you today?"}
        ]
    )
