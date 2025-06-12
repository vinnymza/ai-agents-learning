#!/usr/bin/env python3
"""
Communication Memory - Conversation Persistence Logic

This class handles all memory operations specific to the Communication component.
It understands the conversation data structure and provides high-level methods
for storing and retrieving conversation data.

Key responsibilities:
- Manage conversation history structure
- Add messages with proper metadata (timestamps, IDs)
- Retrieve conversation data for AI context
- Update conversation metadata automatically
- Abstract conversation storage logic from business logic

Design principle: The Communication component should not know about JSON structure
or file operations - it should only call high-level methods like add_message().
"""
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Add shared directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))
from memory_manager import MemoryManager


class CommunicationMemory:
    """
    Handles all persistent memory operations for conversation data.
    
    This class encapsulates the conversation memory structure and provides
    a clean interface for the Communication component to store and retrieve
    conversation history without dealing with file I/O or JSON structure.
    """
    
    def __init__(self, memory_manager: MemoryManager):
        """
        Initialize communication memory with storage backend.
        
        Args:
            memory_manager (MemoryManager): Storage abstraction for file operations
        """
        self.storage = memory_manager
        self._ensure_memory_structure()
    
    def _ensure_memory_structure(self) -> None:
        """
        Initialize the conversation memory structure if it doesn't exist.
        
        Creates the basic conversation structure with metadata when the
        component starts for the first time or memory file is empty.
        """
        data = self.storage.read()
        
        # Initialize structure if empty
        if not data:
            data = {
                "session_id": self._generate_session_id(),
                "started_at": datetime.now().isoformat(),
                "conversation": [],
                "metadata": {
                    "total_messages": 0,
                    "last_activity": datetime.now().isoformat()
                }
            }
            self.storage.write(data)
    
    def _generate_session_id(self) -> str:
        """
        Generate a unique session identifier.
        
        Returns:
            str: Session ID based on current timestamp
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"session_{timestamp}"
    
    def add_message(self, speaker: str, message: str) -> str:
        """
        Add a new message to the conversation history.
        
        This is the main method for storing conversation data. It handles
        message ID generation, timestamp creation, and metadata updates
        automatically.
        
        Args:
            speaker (str): Who said the message ("user" or "agent")
            message (str): The actual message content
            
        Returns:
            str: Generated message ID for reference
        """
        data = self.storage.read()
        
        # Generate message ID
        message_count = len(data.get("conversation", []))
        message_id = f"msg_{message_count + 1:03d}"
        
        # Create message entry
        message_entry = {
            "timestamp": datetime.now().isoformat(),
            "speaker": speaker,
            "message": message,
            "message_id": message_id
        }
        
        # Add to conversation
        data["conversation"].append(message_entry)
        
        # Update metadata
        self._update_metadata(data)
        
        # Persist changes
        self.storage.write(data)
        
        return message_id
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        Retrieve the complete conversation history.
        
        Returns conversation in chronological order, useful for providing
        context to AI components.
        
        Returns:
            List[Dict[str, Any]]: List of message objects with timestamps, speakers, and content
        """
        data = self.storage.read()
        return data.get("conversation", [])
    
    def get_recent_messages(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        Get the most recent messages from conversation.
        
        Useful for providing limited context to AI when full conversation
        history would be too long.
        
        Args:
            count (int): Number of recent messages to retrieve
            
        Returns:
            List[Dict[str, Any]]: Most recent messages in chronological order
        """
        conversation = self.get_conversation_history()
        return conversation[-count:] if len(conversation) > count else conversation
    
    def get_user_messages(self) -> List[Dict[str, Any]]:
        """
        Filter conversation to get only user messages.
        
        Useful for analyzing user requirements and patterns.
        
        Returns:
            List[Dict[str, Any]]: Only messages where speaker is "user"
        """
        conversation = self.get_conversation_history()
        return [msg for msg in conversation if msg.get("speaker") == "user"]
    
    def get_agent_messages(self) -> List[Dict[str, Any]]:
        """
        Filter conversation to get only agent messages.
        
        Useful for analyzing agent responses and patterns.
        
        Returns:
            List[Dict[str, Any]]: Only messages where speaker is "agent"
        """
        conversation = self.get_conversation_history()
        return [msg for msg in conversation if msg.get("speaker") == "agent"]
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        Get session metadata and statistics.
        
        Returns:
            Dict[str, Any]: Session information including ID, start time, and statistics
        """
        data = self.storage.read()
        return {
            "session_id": data.get("session_id"),
            "started_at": data.get("started_at"),
            "metadata": data.get("metadata", {})
        }
    
    def clear_conversation(self) -> None:
        """
        Clear all conversation history while preserving session structure.
        
        Useful for starting fresh conversations or testing.
        """
        data = self.storage.read()
        data["conversation"] = []
        data["started_at"] = datetime.now().isoformat()
        data["session_id"] = self._generate_session_id()
        self._update_metadata(data)
        self.storage.write(data)
    
    def _update_metadata(self, data: Dict[str, Any]) -> None:
        """
        Update conversation metadata with current statistics.
        
        Args:
            data (Dict[str, Any]): Current memory data to update
        """
        conversation_length = len(data.get("conversation", []))
        
        data["metadata"] = {
            "total_messages": conversation_length,
            "last_activity": datetime.now().isoformat(),
            "user_messages": len([msg for msg in data.get("conversation", []) if msg.get("speaker") == "user"]),
            "agent_messages": len([msg for msg in data.get("conversation", []) if msg.get("speaker") == "agent"])
        }
    
    def get_conversation_summary(self) -> str:
        """
        Generate a text summary of the conversation for AI context.
        
        Creates a formatted string representation of the conversation
        that can be easily used as context in AI prompts.
        
        Returns:
            str: Formatted conversation history
        """
        conversation = self.get_conversation_history()
        
        if not conversation:
            return "No conversation history yet."
        
        summary_lines = []
        for msg in conversation:
            speaker = msg.get("speaker", "unknown").title()
            message = msg.get("message", "")
            timestamp = msg.get("timestamp", "")
            summary_lines.append(f"{speaker} ({timestamp}): {message}")
        
        return "\n".join(summary_lines)
    
    def __str__(self) -> str:
        """String representation for debugging."""
        session_info = self.get_session_info()
        return f"CommunicationMemory(session={session_info.get('session_id')}, messages={session_info.get('metadata', {}).get('total_messages', 0)})"