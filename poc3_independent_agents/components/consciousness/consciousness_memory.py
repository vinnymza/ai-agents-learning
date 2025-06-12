#!/usr/bin/env python3
"""
Consciousness Memory - Shared Context Management

This class handles the shared context memory that all components can access
to understand the current state of requirements gathering and user story creation.
Unlike component-specific memories, this serves as the "global state" that
provides context about the overall project and process.

Key responsibilities:
- Manage project-wide context and state
- Track active requirements and their processing status
- Maintain decision history and patterns for learning
- Provide shared context to all components
- Track inter-component communication needs

Design principle: This is the "shared brain" memory that helps components
understand what's happening globally, not just in their local scope.
"""
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add shared directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))
from memory_manager import MemoryManager


class ConsciousnessMemory:
    """
    Manages shared context and global state across all components.
    
    This memory serves as the central knowledge base about the current
    project state, requirements, and decision-making context that all
    components can reference to stay coordinated.
    """
    
    def __init__(self, memory_manager: MemoryManager):
        """
        Initialize consciousness memory with storage backend.
        
        Args:
            memory_manager (MemoryManager): Storage abstraction for file operations
        """
        self.storage = memory_manager
        self._ensure_memory_structure()
    
    def _ensure_memory_structure(self) -> None:
        """
        Initialize the consciousness memory structure if it doesn't exist.
        
        Creates the foundational shared context structure when starting
        fresh or when memory file doesn't exist.
        """
        data = self.storage.read()
        
        # Initialize structure if empty
        if not data:
            data = {
                "project_context": {
                    "name": "",
                    "description": "",
                    "current_phase": "requirements_gathering",
                    "initialized_at": datetime.now().isoformat()
                },
                "shared_state": {
                    "active_requirements": [],
                    "pending_actions": [],
                    "completed_actions": [],
                    "current_focus": "initial_requirements"
                },
                "decision_history": [],
                "component_interactions": {
                    "last_communication_input": None,
                    "last_user_story_request": None,
                    "pending_user_story_creation": False
                },
                "metadata": {
                    "last_updated": datetime.now().isoformat(),
                    "total_decisions": 0,
                    "total_requirements": 0
                }
            }
            self.storage.write(data)
    
    def update_project_context(self, name: str = None, description: str = None, phase: str = None) -> None:
        """
        Update the overall project context information.
        
        Args:
            name (str, optional): Project name
            description (str, optional): Project description  
            phase (str, optional): Current project phase
        """
        data = self.storage.read()
        
        if name is not None:
            data["project_context"]["name"] = name
        if description is not None:
            data["project_context"]["description"] = description
        if phase is not None:
            data["project_context"]["current_phase"] = phase
            
        self._update_metadata(data)
        self.storage.write(data)
    
    def add_requirement(self, requirement_text: str, source: str = "user") -> str:
        """
        Add a new requirement to the shared context.
        
        Args:
            requirement_text (str): The requirement description
            source (str): Where the requirement came from (default: "user")
            
        Returns:
            str: Generated requirement ID for reference
        """
        data = self.storage.read()
        
        # Generate requirement ID
        req_count = len(data["shared_state"]["active_requirements"])
        req_id = f"REQ{req_count + 1:03d}"
        
        requirement = {
            "requirement_id": req_id,
            "text": requirement_text,
            "source": source,
            "status": "identified",
            "identified_at": datetime.now().isoformat(),
            "assigned_actions": []
        }
        
        data["shared_state"]["active_requirements"].append(requirement)
        self._update_metadata(data)
        self.storage.write(data)
        
        return req_id
    
    def update_requirement_status(self, requirement_id: str, new_status: str) -> bool:
        """
        Update the status of a specific requirement.
        
        Args:
            requirement_id (str): ID of requirement to update
            new_status (str): New status (identified, processing, completed, etc.)
            
        Returns:
            bool: True if requirement was found and updated, False otherwise
        """
        data = self.storage.read()
        
        for req in data["shared_state"]["active_requirements"]:
            if req["requirement_id"] == requirement_id:
                req["status"] = new_status
                req["last_updated"] = datetime.now().isoformat()
                self._update_metadata(data)
                self.storage.write(data)
                return True
        
        return False
    
    def add_pending_action(self, action_type: str, target_component: str, context: Dict[str, Any]) -> str:
        """
        Add an action that needs to be taken by a component.
        
        Args:
            action_type (str): Type of action (e.g., "create_user_story")
            target_component (str): Component that should handle this action
            context (Dict[str, Any]): Additional context for the action
            
        Returns:
            str: Generated action ID for tracking
        """
        data = self.storage.read()
        
        action_count = len(data["shared_state"]["pending_actions"]) + len(data["shared_state"]["completed_actions"])
        action_id = f"ACTION{action_count + 1:03d}"
        
        action = {
            "action_id": action_id,
            "action_type": action_type,
            "target_component": target_component,
            "context": context,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        data["shared_state"]["pending_actions"].append(action)
        self._update_metadata(data)
        self.storage.write(data)
        
        return action_id
    
    def complete_action(self, action_id: str, result: Dict[str, Any] = None) -> bool:
        """
        Mark an action as completed and move it to completed actions.
        
        Args:
            action_id (str): ID of action to complete
            result (Dict[str, Any], optional): Result of the action
            
        Returns:
            bool: True if action was found and completed, False otherwise
        """
        data = self.storage.read()
        
        # Find and remove from pending
        for i, action in enumerate(data["shared_state"]["pending_actions"]):
            if action["action_id"] == action_id:
                action["status"] = "completed"
                action["completed_at"] = datetime.now().isoformat()
                if result:
                    action["result"] = result
                
                # Move to completed actions
                completed_action = data["shared_state"]["pending_actions"].pop(i)
                data["shared_state"]["completed_actions"].append(completed_action)
                
                self._update_metadata(data)
                self.storage.write(data)
                return True
        
        return False
    
    def record_decision(self, trigger: str, analysis: str, decision: str, action_taken: str = None) -> None:
        """
        Record a decision made by the consciousness component.
        
        Args:
            trigger (str): What triggered this decision
            analysis (str): The analysis that led to the decision
            decision (str): The decision that was made
            action_taken (str, optional): What action was taken as a result
        """
        data = self.storage.read()
        
        decision_record = {
            "timestamp": datetime.now().isoformat(),
            "trigger": trigger,
            "analysis": analysis,
            "decision": decision,
            "action_taken": action_taken
        }
        
        data["decision_history"].append(decision_record)
        self._update_metadata(data)
        self.storage.write(data)
    
    def get_active_requirements(self) -> List[Dict[str, Any]]:
        """
        Get all currently active requirements.
        
        Returns:
            List[Dict[str, Any]]: List of active requirements
        """
        data = self.storage.read()
        return data["shared_state"]["active_requirements"]
    
    def get_pending_actions(self, target_component: str = None) -> List[Dict[str, Any]]:
        """
        Get pending actions, optionally filtered by target component.
        
        Args:
            target_component (str, optional): Filter by component name
            
        Returns:
            List[Dict[str, Any]]: List of pending actions
        """
        data = self.storage.read()
        pending = data["shared_state"]["pending_actions"]
        
        if target_component:
            return [action for action in pending if action["target_component"] == target_component]
        
        return pending
    
    def get_project_context(self) -> Dict[str, Any]:
        """
        Get the current project context.
        
        Returns:
            Dict[str, Any]: Project context information
        """
        data = self.storage.read()
        return data["project_context"]
    
    def get_shared_state(self) -> Dict[str, Any]:
        """
        Get the current shared state.
        
        Returns:
            Dict[str, Any]: Shared state information
        """
        data = self.storage.read()
        return data["shared_state"]
    
    def update_component_interaction(self, interaction_type: str, data_payload: Any) -> None:
        """
        Update component interaction tracking.
        
        Args:
            interaction_type (str): Type of interaction (e.g., "communication_input")
            data_payload (Any): Data associated with the interaction
        """
        data = self.storage.read()
        
        data["component_interactions"][interaction_type] = {
            "timestamp": datetime.now().isoformat(),
            "data": data_payload
        }
        
        self._update_metadata(data)
        self.storage.write(data)
    
    def get_context_summary(self) -> str:
        """
        Generate a summary of the current context for AI components.
        
        Returns:
            str: Formatted context summary
        """
        data = self.storage.read()
        
        project = data["project_context"]
        state = data["shared_state"]
        
        summary_parts = []
        
        # Project info
        summary_parts.append(f"Project: {project.get('name', 'Unnamed')} ({project.get('current_phase', 'unknown phase')})")
        if project.get('description'):
            summary_parts.append(f"Description: {project['description']}")
        
        # Requirements status
        active_reqs = len(state["active_requirements"])
        summary_parts.append(f"Active requirements: {active_reqs}")
        
        # Pending actions
        pending_actions = len(state["pending_actions"])
        if pending_actions > 0:
            summary_parts.append(f"Pending actions: {pending_actions}")
        
        # Current focus
        summary_parts.append(f"Current focus: {state.get('current_focus', 'general')}")
        
        return "\n".join(summary_parts)
    
    def clear_context(self) -> None:
        """
        Clear all context for a fresh start.
        
        Useful for starting a new project or testing.
        """
        # Delete existing data and reinitialize
        self.storage.delete()
        self._ensure_memory_structure()
    
    def _update_metadata(self, data: Dict[str, Any]) -> None:
        """
        Update metadata with current statistics.
        
        Args:
            data (Dict[str, Any]): Current memory data to update
        """
        data["metadata"] = {
            "last_updated": datetime.now().isoformat(),
            "total_decisions": len(data.get("decision_history", [])),
            "total_requirements": len(data.get("shared_state", {}).get("active_requirements", [])),
            "pending_actions": len(data.get("shared_state", {}).get("pending_actions", [])),
            "completed_actions": len(data.get("shared_state", {}).get("completed_actions", []))
        }
    
    def __str__(self) -> str:
        """String representation for debugging."""
        data = self.storage.read()
        metadata = data.get("metadata", {})
        return f"ConsciousnessMemory(requirements={metadata.get('total_requirements', 0)}, decisions={metadata.get('total_decisions', 0)})"