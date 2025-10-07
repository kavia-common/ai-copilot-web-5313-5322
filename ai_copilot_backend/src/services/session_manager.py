"""
Session manager for handling in-memory chat sessions and message history.
Thread-safe implementation using locks for concurrent access.
"""
import threading
from typing import Dict, List, Optional


# PUBLIC_INTERFACE
class SessionManager:
    """
    Thread-safe in-memory session manager for chat history.
    
    Manages chat sessions and their associated message histories.
    Each session maintains a list of messages with role and content.
    """
    
    def __init__(self):
        """Initialize the session manager with empty sessions and a lock."""
        self._sessions: Dict[str, List[Dict[str, str]]] = {}
        self._lock = threading.Lock()
    
    # PUBLIC_INTERFACE
    def create_session(self, session_id: str) -> None:
        """
        Create a new session with empty message history.
        
        Args:
            session_id: Unique identifier for the session
        """
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = []
    
    # PUBLIC_INTERFACE
    def session_exists(self, session_id: str) -> bool:
        """
        Check if a session exists.
        
        Args:
            session_id: Session identifier to check
            
        Returns:
            True if the session exists, False otherwise
        """
        with self._lock:
            return session_id in self._sessions
    
    # PUBLIC_INTERFACE
    def add_message(self, session_id: str, role: str, content: str) -> None:
        """
        Add a message to the session history.
        
        Args:
            session_id: Session identifier
            role: Message role ('user' or 'assistant')
            content: Message content
            
        Raises:
            ValueError: If session does not exist
        """
        with self._lock:
            if session_id not in self._sessions:
                raise ValueError(f"Session {session_id} does not exist")
            self._sessions[session_id].append({
                "role": role,
                "content": content
            })
    
    # PUBLIC_INTERFACE
    def get_history(self, session_id: str) -> Optional[List[Dict[str, str]]]:
        """
        Retrieve the message history for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of message dictionaries with 'role' and 'content' keys,
            or None if session does not exist
        """
        with self._lock:
            if session_id not in self._sessions:
                return None
            # Return a copy to prevent external modification
            return [msg.copy() for msg in self._sessions[session_id]]
    
    # PUBLIC_INTERFACE
    def clear_session(self, session_id: str) -> bool:
        """
        Clear all messages from a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session was cleared, False if session does not exist
        """
        with self._lock:
            if session_id in self._sessions:
                self._sessions[session_id] = []
                return True
            return False
    
    # PUBLIC_INTERFACE
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session completely.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session was deleted, False if session does not exist
        """
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                return True
            return False
