#!/usr/bin/env python3
"""
Consciousness Component - Shared Context Manager and Decision Maker

This component manages the shared context that all other components need
to understand the current state of the requirements-to-user-stories process.
It analyzes communication inputs and decides when actions like user story
creation are needed.

Key responsibilities:
- Maintain shared project context and state
- Analyze user input to identify when requirements are mentioned
- Decide when to trigger user story creation
- Provide global context to other components
- Track the overall process flow and state

Design principle: This component is the "context keeper" and "decision maker"
that helps other components understand what's happening globally and what
actions need to be taken next.
"""
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Add shared directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))
from anthropic_client import AnthropicClient
from memory_manager import MemoryManager

# Import memory handler
from consciousness_memory import ConsciousnessMemory


class ConsciousnessComponent:
    """
    Manages shared context and makes decisions about process flow.
    
    This component serves as the "brain" that understands what's happening
    across all components and decides what actions need to be taken based
    on user input and current context.
    """
    
    def __init__(self, anthropic_client: AnthropicClient):
        """
        Initialize the Consciousness component.
        
        Args:
            anthropic_client (AnthropicClient): Shared AI client for analysis
        """
        self.ai = anthropic_client
        
        # Initialize memory management
        memory_manager = MemoryManager("components/consciousness/memory/shared_context_memory.json")
        self.memory = ConsciousnessMemory(memory_manager)
        
        # References to other components (set externally)
        self.communication = None
        self.user_story_creator = None
        
        # AI prompt configuration for this component's role
        self.system_prompt = self._build_system_prompt()
    
    def set_communication_component(self, communication_component) -> None:
        """
        Set reference to Communication component.
        
        Args:
            communication_component: Instance of CommunicationComponent
        """
        self.communication = communication_component
    
    def set_user_story_creator_component(self, user_story_creator_component) -> None:
        """
        Set reference to User Story Creator component.
        
        Args:
            user_story_creator_component: Instance of UserStoryCreatorComponent
        """
        self.user_story_creator = user_story_creator_component
    
    def _build_system_prompt(self) -> str:
        """
        Build the system prompt that defines this component's AI role.
        
        Returns:
            str: System prompt for AI analysis
        """
        return """You are a Consciousness component in an AI agent system that transforms requirements into user stories.

Your responsibilities:
1. Analyze user input to identify when new requirements are mentioned
2. Decide when user story creation should be triggered
3. Maintain awareness of the overall project context and progress
4. Make decisions about process flow based on current state

Your analysis should identify:
- When users mention new functional requirements
- When enough information exists to create meaningful user stories
- When clarifying questions are needed before proceeding
- When the user is asking for status or information vs providing requirements

Decision types you can make:
- "create_user_story": User has provided enough requirement detail
- "ask_clarification": Need more information before creating stories
- "continue_conversation": General conversation, no immediate action needed
- "update_context": User provided context but not specific requirements

Always provide your reasoning for the decision and what specific information triggered it."""
    
    def process_communication_input(self, user_input: str) -> None:
        """
        Process input from Communication component and decide on actions.
        
        This is the main decision-making method that analyzes user input
        in context and determines what actions should be taken.
        
        Args:
            user_input (str): User input received from Communication component
        """
        try:
            # Record the communication interaction
            self.memory.update_component_interaction("last_communication_input", user_input)
            
            # Get current context for analysis
            context_summary = self.memory.get_context_summary()
            active_requirements = self.memory.get_active_requirements()
            
            # Analyze the input and make decision
            decision = self._analyze_input_and_decide(user_input, context_summary, active_requirements)
            
            # Execute the decision
            self._execute_decision(decision, user_input)
            
        except Exception as e:
            print(f"ERROR: Failed to process communication input: {str(e)}")
            # Fallback: continue conversation
            if self.communication:
                self.communication.display_agent_response("I had trouble processing that. Could you please rephrase your requirement?")
    
    def _analyze_input_and_decide(self, user_input: str, context_summary: str, active_requirements: list) -> Dict[str, Any]:
        """
        Use AI to analyze user input and decide on appropriate action.
        
        Args:
            user_input (str): Latest user input
            context_summary (str): Current project context
            active_requirements (list): Currently active requirements
            
        Returns:
            Dict[str, Any]: Decision with action type and reasoning
        """
        # Build analysis prompt
        requirements_summary = "\n".join([f"- {req['text']} (Status: {req['status']})" for req in active_requirements])
        
        user_prompt = f"""
        Current Project Context:
        {context_summary}
        
        Active Requirements:
        {requirements_summary if requirements_summary else "No active requirements yet"}
        
        Latest User Input: "{user_input}"
        
        Analyze this input and decide what action should be taken. Consider:
        1. Does this input contain new functional requirements?
        2. Is there enough detail to create user stories?
        3. Does this need clarification before proceeding?
        4. Is this just general conversation?
        
        Respond in this JSON format:
        {{
            "action": "create_user_story|ask_clarification|continue_conversation|update_context",
            "reasoning": "Explanation of why this action was chosen",
            "extracted_requirements": ["List any new requirements identified"],
            "missing_information": ["List any information needed for user stories"],
            "confidence": 0.8
        }}
        """
        
        try:
            response = self.ai.generate_response(self.system_prompt, user_prompt)
            
            # Parse JSON response
            import json
            decision = json.loads(response.strip())
            
            # Record the decision
            self.memory.record_decision(
                trigger=f"User input: {user_input}",
                analysis=decision.get("reasoning", ""),
                decision=decision.get("action", "continue_conversation"),
                action_taken=None  # Will be updated after execution
            )
            
            return decision
            
        except Exception as e:
            print(f"ERROR: Failed to analyze input: {str(e)}")
            # Fallback decision
            return {
                "action": "continue_conversation",
                "reasoning": "Analysis failed, defaulting to conversation",
                "extracted_requirements": [],
                "missing_information": [],
                "confidence": 0.1
            }
    
    def _execute_decision(self, decision: Dict[str, Any], user_input: str) -> None:
        """
        Execute the decision made by the analysis.
        
        Args:
            decision (Dict[str, Any]): Decision from analysis
            user_input (str): Original user input
        """
        action = decision.get("action", "continue_conversation")
        
        if action == "create_user_story":
            self._handle_user_story_creation(decision, user_input)
            
        elif action == "ask_clarification":
            self._handle_clarification_request(decision)
            
        elif action == "update_context":
            self._handle_context_update(decision, user_input)
            
        else:  # continue_conversation
            self._handle_continue_conversation(decision)
    
    def _handle_user_story_creation(self, decision: Dict[str, Any], user_input: str) -> None:
        """
        Handle user story creation decision.
        
        Args:
            decision (Dict[str, Any]): Decision details
            user_input (str): Original user input
        """
        # Extract and add new requirements
        extracted_requirements = decision.get("extracted_requirements", [])
        
        for req_text in extracted_requirements:
            req_id = self.memory.add_requirement(req_text, "user")
            
        # Create action for User Story Creator
        if self.user_story_creator and extracted_requirements:
            action_id = self.memory.add_pending_action(
                action_type="create_user_story",
                target_component="user_story_creator",
                context={
                    "requirements": extracted_requirements,
                    "user_input": user_input,
                    "reasoning": decision.get("reasoning", "")
                }
            )
            
            # Trigger user story creation
            self.user_story_creator.process_requirements(extracted_requirements, user_input)
            
            # Update decision record
            latest_decision = self.memory.storage.read()["decision_history"][-1]
            latest_decision["action_taken"] = f"Triggered user story creation (Action: {action_id})"
            self.memory.storage.write(self.memory.storage.read())
            
        # Respond to user
        if self.communication:
            response = f"I've identified {len(extracted_requirements)} requirement(s) and will create user stories for them."
            self.communication.display_agent_response(response)
    
    def _handle_clarification_request(self, decision: Dict[str, Any]) -> None:
        """
        Handle clarification request decision.
        
        Args:
            decision (Dict[str, Any]): Decision details
        """
        missing_info = decision.get("missing_information", [])
        
        if missing_info and self.communication:
            # Ask for the first missing piece of information
            question = f"To create proper user stories, I need more information: {missing_info[0]}"
            self.communication.display_agent_response(question)
        elif self.communication:
            self.communication.display_agent_response("Could you provide more details about what you need?")
    
    def _handle_context_update(self, decision: Dict[str, Any], user_input: str) -> None:
        """
        Handle context update decision.
        
        Args:
            decision (Dict[str, Any]): Decision details
            user_input (str): Original user input
        """
        # Update project context if relevant information was provided
        extracted_requirements = decision.get("extracted_requirements", [])
        
        if extracted_requirements:
            for req_text in extracted_requirements:
                self.memory.add_requirement(req_text, "user")
        
        # Provide acknowledgment
        if self.communication:
            self.communication.display_agent_response("I've noted that information. Please continue with your requirements.")
    
    def _handle_continue_conversation(self, decision: Dict[str, Any]) -> None:
        """
        Handle continue conversation decision.
        
        Args:
            decision (Dict[str, Any]): Decision details
        """
        if self.communication:
            reasoning = decision.get("reasoning", "")
            
            if "greeting" in reasoning.lower() or "hello" in reasoning.lower():
                response = "Hello! I'm here to help you transform your requirements into user stories. What would you like to build?"
            else:
                response = "I understand. Please tell me more about your requirements, and I'll help create user stories for your project."
                
            self.communication.display_agent_response(response)
    
    def get_project_status(self) -> Dict[str, Any]:
        """
        Get current project status for monitoring.
        
        Returns:
            Dict[str, Any]: Current project status and statistics
        """
        context = self.memory.get_project_context()
        state = self.memory.get_shared_state()
        
        return {
            "project_name": context.get("name", "Unnamed"),
            "current_phase": context.get("current_phase", "unknown"),
            "active_requirements": len(state.get("active_requirements", [])),
            "pending_actions": len(state.get("pending_actions", [])),
            "current_focus": state.get("current_focus", "general")
        }
    
    def set_project_info(self, name: str, description: str = "") -> None:
        """
        Set project information in shared context.
        
        Args:
            name (str): Project name
            description (str): Project description
        """
        self.memory.update_project_context(name=name, description=description)
        
        if self.communication:
            self.communication.display_agent_response(f"Project '{name}' context updated. Ready to gather requirements!")
    
    def get_context_summary(self) -> str:
        """
        Get formatted context summary for other components.
        
        Returns:
            str: Formatted context summary
        """
        return self.memory.get_context_summary()
    
    def clear_context(self) -> None:
        """
        Clear all shared context for fresh start.
        """
        self.memory.clear_context()
        
        if self.communication:
            self.communication.display_to_user_only("Shared context cleared. Starting fresh project!")
    
    def __str__(self) -> str:
        """String representation for debugging."""
        status = self.get_project_status()
        return f"ConsciousnessComponent(project='{status['project_name']}', requirements={status['active_requirements']})"