#!/usr/bin/env python3
"""
Communication Component - User Interaction and I/O Management

This component handles all interactions with users, including input processing,
output display, and conversation management. It serves as the interface between
the external world and the internal agent system.

Key responsibilities:
- Process user input and store in conversation history
- Display agent responses to users via console
- Coordinate with Consciousness component for decision making
- Maintain conversation context and flow
- Handle user interface concerns (prompts, formatting, etc.)

Design principle: This component owns the user interaction experience
and delegates decision-making to other components.
"""
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add shared directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))
from anthropic_client import AnthropicClient
from memory_manager import MemoryManager

# Import memory handler
from communication_memory import CommunicationMemory


class CommunicationComponent:
    """
    Manages all user interaction and communication flow.
    
    This component is responsible for the user experience and ensuring
    that conversation flows naturally while coordinating with other
    components for business logic decisions.
    """
    
    def __init__(self, anthropic_client: AnthropicClient):
        """
        Initialize the Communication component.
        
        Args:
            anthropic_client (AnthropicClient): Shared AI client for generating responses
        """
        self.ai = anthropic_client
        
        # Initialize memory management
        memory_manager = MemoryManager("components/communication/memory/conversation_memory.json")
        self.memory = CommunicationMemory(memory_manager)
        
        # Reference to Consciousness component (set externally)
        self.consciousness = None
        
        # AI prompt configuration for this component's role
        self.system_prompt = self._build_system_prompt()
    
    def set_consciousness_component(self, consciousness_component) -> None:
        """
        Set reference to Consciousness component for coordination.
        
        This allows the Communication component to send user input to
        Consciousness for decision making about what actions to take.
        
        Args:
            consciousness_component: Instance of ConsciousnessComponent
        """
        self.consciousness = consciousness_component
    
    def _build_system_prompt(self) -> str:
        """
        Build the system prompt that defines this component's AI role.
        
        Returns:
            str: System prompt for AI interactions
        """
        return """You are a Communication component in an AI agent system that transforms requirements into user stories.

Your responsibilities:
1. Interact naturally with users to gather requirements
2. Ask clarifying questions when requirements are unclear
3. Provide friendly, professional responses
4. Guide users through the requirements gathering process

Your communication style should be:
- Clear and concise
- Professional but approachable  
- Focused on gathering complete requirements
- Ask one question at a time to avoid overwhelming users

You work with other components:
- Consciousness: Makes decisions about when to create user stories
- UserStoryCreator: Actually creates the user stories

Keep responses focused on communication and avoid making decisions about user story creation - that's the Consciousness component's job."""
    
    def process_user_input(self, user_input: str) -> None:
        """
        Process input from user and coordinate appropriate responses.
        
        This is the main entry point for user interactions. It stores the
        user input, decides whether to handle directly or send to Consciousness,
        and manages the overall conversation flow.
        
        Args:
            user_input (str): What the user typed/said
        """
        # Store user input in conversation history
        self.memory.add_message("user", user_input)
        
        # Use AI to decide how to handle the input
        should_handle_directly = self._should_handle_directly_with_ai(user_input)
        
        if should_handle_directly:
            self._handle_input_directly(user_input)
        else:
            # Send to Consciousness for complex decision making
            if self.consciousness:
                self.consciousness.process_communication_input(user_input)
            else:
                # Fallback: handle directly if no Consciousness
                self._handle_input_directly(user_input)
    
    def _should_handle_directly_with_ai(self, user_input: str) -> bool:
        """
        Use AI to determine if Communication should handle input directly.
        
        This method uses AI to classify whether the user input should be
        handled directly by Communication (simple interactions) or sent
        to Consciousness for complex processing.
        
        Args:
            user_input (str): User input to classify
            
        Returns:
            bool: True if Communication should handle directly, False to send to Consciousness
        """
        system_prompt = """You are a Communication component filter that decides whether user input should be handled directly by Communication or sent to Consciousness for complex processing.

Handle directly by Communication ONLY:
- Simple greetings (hello, hi, hola, good morning)
- Generic help requests (help, what can you do)
- System commands (exit, quit, clear memories, reset)
- Empty or nonsensical input
- Conversational acknowledgments (ok, thanks, understood)
- General conversational responses

Send to Consciousness (everything project-related):
- Any mention of user stories, requirements, features
- Project queries (show story, list stories, project status)
- New requirements or modifications
- Business logic or functional requests
- Anything related to the actual project work
- Requests for creating, updating, or viewing user stories"""

        user_prompt = f"""
        User input: "{user_input}"
        
        Should Communication handle this directly (true) or send to Consciousness (false)?
        
        Respond with only: true or false
        """
        
        try:
            response = self.ai.generate_response(system_prompt, user_prompt).strip().lower()
            return response == "true"
        except Exception as e:
            print(f"ERROR: Failed to classify input: {str(e)}")
            return True  # Default to handling directly on error
    
    def _handle_input_directly(self, user_input: str) -> None:
        """
        Handle simple user input directly with conversational context.
        
        This method handles non-project-related input like greetings,
        acknowledgments, system commands, and general conversation using recent 
        conversation context to provide appropriate responses.
        
        Args:
            user_input (str): User input to process
        """
        try:
            # Check for clear memories command
            if self._is_clear_command(user_input):
                self._handle_clear_memories_command()
                return
            
            # Get recent conversation for context
            recent_messages = self.memory.get_recent_messages(5)
            conversation_context = self._format_recent_conversation(recent_messages)
            
            # Create user prompt with context
            user_prompt = f"""
            Recent conversation:
            {conversation_context}
            
            Latest user input: "{user_input}"
            
            Respond appropriately as a helpful assistant that transforms requirements into user stories.
            Keep responses friendly, concise, and focused on helping with requirements gathering.
            If this is a greeting, welcome the user and explain your purpose.
            If this is an acknowledgment, respond naturally and ask if there's anything else you can help with.
            If this is a help request, explain what you can do.
            """
            
            # Generate contextual response
            response = self.ai.generate_response(self.system_prompt, user_prompt)
            
            # Display and store response
            self.display_agent_response(response)
            
        except Exception as e:
            print(f"ERROR: Failed to process user input: {str(e)}")
            self.display_agent_response("I'm having trouble processing your request. Could you please try again?")
    
    def _is_clear_command(self, user_input: str) -> bool:
        """
        Check if user input is a command to clear memories.
        
        Args:
            user_input (str): User input to check
            
        Returns:
            bool: True if this is a clear command
        """
        clear_keywords = ['clear', 'reset', 'clear memories', 'clear all', 'fresh start', 'start over']
        user_lower = user_input.lower().strip()
        
        return any(keyword in user_lower for keyword in clear_keywords)
    
    def _handle_clear_memories_command(self) -> None:
        """
        Handle the clear memories command from user.
        """
        self.display_to_user_only("🧹 Clearing all memories...")
        
        # Clear own memory
        self.clear_conversation()
        
        # Clear other components' memories through their references
        if hasattr(self, 'consciousness') and self.consciousness:
            self.consciousness.clear_context()
        
        # Find user story creator through consciousness reference
        if (hasattr(self, 'consciousness') and 
            self.consciousness and 
            hasattr(self.consciousness, 'user_story_creator') and 
            self.consciousness.user_story_creator):
            self.consciousness.user_story_creator.clear_all_stories()
        
        self.display_to_user_only("✅ All memories cleared! Starting fresh.")
        self.display_agent_response("Hello! I'm ready to help you transform your requirements into user stories. What would you like to build?")
    
    def _format_recent_conversation(self, messages: List[Dict[str, Any]]) -> str:
        """
        Format recent messages for AI context.
        
        Converts recent conversation messages into a readable format
        that can be used as context for AI responses.
        
        Args:
            messages (List[Dict[str, Any]]): Recent conversation messages
            
        Returns:
            str: Formatted conversation history
        """
        if not messages:
            return "No previous conversation."
        
        formatted_lines = []
        for msg in messages:
            speaker = msg.get("speaker", "unknown").title()
            message = msg.get("message", "")
            formatted_lines.append(f"{speaker}: {message}")
        
        return "\n".join(formatted_lines)
    
    def display_agent_response(self, message: str) -> None:
        """
        Display agent response to user and store in conversation history.
        
        This method handles both the user interface (console output) and
        the persistence (conversation storage) in one operation.
        
        Args:
            message (str): Agent response message to display and store
        """
        # Display to user via console
        print(f"\nAgent: {message}")
        
        # Store in conversation history
        self.memory.add_message("agent", message)
    
    def display_to_user_only(self, message: str) -> None:
        """
        Display message to user without storing in conversation history.
        
        Useful for system messages, errors, or temporary notifications
        that shouldn't be part of the conversation context.
        
        Args:
            message (str): Message to display (not stored)
        """
        print(f"\nSystem: {message}")
    
    def get_user_input(self, prompt: str = "You: ") -> Optional[str]:
        """
        Get input from user with custom prompt.
        
        Handles user input collection with error handling for
        interruptions (Ctrl+C) and EOF conditions.
        
        Args:
            prompt (str): Custom prompt to display to user
            
        Returns:
            Optional[str]: User input string, or None if interrupted
        """
        try:
            user_input = input(f"\n{prompt}").strip()
            return user_input if user_input else None
        except (KeyboardInterrupt, EOFError):
            return None
    
    def start_conversation_loop(self) -> None:
        """
        Start interactive conversation loop with user.
        
        This method runs the main conversation interface, continuously
        accepting user input and processing it until the user decides to exit.
        """
        self.display_to_user_only("Requirements to User Stories Agent")
        self.display_to_user_only("=====================================")
        self.display_to_user_only("I'll help you transform your requirements into well-structured user stories.")
        self.display_to_user_only("Type 'exit', 'quit', or 'bye' to end the conversation.")
        
        while True:
            user_input = self.get_user_input()
            
            if user_input is None:
                # Handle interruption (Ctrl+C)
                self.display_to_user_only("Conversation interrupted. Goodbye!")
                break
            
            if user_input.lower() in ['exit', 'quit', 'bye', 'stop']:
                self.display_to_user_only("Thank you for using the Requirements to User Stories Agent. Goodbye!")
                break
            
            if not user_input:
                # Empty input, ask again
                continue
            
            # Process the user input
            self.process_user_input(user_input)
    
    def get_conversation_context(self) -> str:
        """
        Get formatted conversation context for other components.
        
        This method provides conversation history in a format suitable
        for sharing with other components like Consciousness for decision making.
        
        Returns:
            str: Formatted conversation history
        """
        return self.memory.get_conversation_summary()
    
    def get_recent_user_requirements(self, count: int = 3) -> str:
        """
        Extract recent user requirements from conversation.
        
        Analyzes recent user messages to identify requirements mentioned,
        useful for providing context to other components.
        
        Args:
            count (int): Number of recent user messages to analyze
            
        Returns:
            str: Summary of recent requirements mentioned by user
        """
        recent_user_messages = self.memory.get_user_messages()[-count:]
        
        if not recent_user_messages:
            return "No user requirements identified yet."
        
        requirements = []
        for msg in recent_user_messages:
            requirements.append(f"- {msg.get('message', '')}")
        
        return "Recent user requirements:\n" + "\n".join(requirements)
    
    def clear_conversation(self) -> None:
        """
        Clear conversation history for fresh start.
        
        Useful for testing or starting a new requirements gathering session.
        """
        self.memory.clear_conversation()
        self.display_to_user_only("Conversation history cleared. Starting fresh!")
    
    def get_conversation_stats(self) -> dict:
        """
        Get conversation statistics for monitoring.
        
        Returns:
            dict: Statistics about current conversation
        """
        session_info = self.memory.get_session_info()
        return {
            "session_id": session_info.get("session_id"),
            "total_messages": session_info.get("metadata", {}).get("total_messages", 0),
            "user_messages": session_info.get("metadata", {}).get("user_messages", 0),
            "agent_messages": session_info.get("metadata", {}).get("agent_messages", 0),
            "started_at": session_info.get("started_at"),
            "last_activity": session_info.get("metadata", {}).get("last_activity")
        }
    
    def __str__(self) -> str:
        """String representation for debugging."""
        stats = self.get_conversation_stats()
        return f"CommunicationComponent(session={stats.get('session_id')}, messages={stats.get('total_messages')})"