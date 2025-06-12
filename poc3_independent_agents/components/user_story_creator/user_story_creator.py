#!/usr/bin/env python3
"""
User Story Creator Component - Requirements to User Stories Transformation

This component handles the core business logic of transforming user requirements
into well-structured user stories with acceptance criteria. It uses AI to analyze
requirements and create professional, actionable user stories.

Key responsibilities:
- Transform requirements into user story format
- Generate appropriate acceptance criteria for each story
- Maintain user story collection and status
- Provide feedback to users about created stories
- Handle user story updates and refinements

Design principle: This component owns the user story creation process
and maintains the collection of stories for the project.
"""
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add shared directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))
from anthropic_client import AnthropicClient
from memory_manager import MemoryManager

# Import memory handler
from user_story_memory import UserStoryMemory


class UserStoryCreatorComponent:
    """
    Creates and manages user stories from requirements.
    
    This component is responsible for the core transformation of user
    requirements into professional user stories with proper acceptance
    criteria and metadata.
    """
    
    def __init__(self, anthropic_client: AnthropicClient):
        """
        Initialize the User Story Creator component.
        
        Args:
            anthropic_client (AnthropicClient): Shared AI client for story generation
        """
        self.ai = anthropic_client
        
        # Initialize memory management
        memory_manager = MemoryManager("components/user_story_creator/memory/user_stories_memory.json")
        self.memory = UserStoryMemory(memory_manager)
        
        # References to other components (set externally)
        self.communication = None
        self.consciousness = None
        
        # AI prompt configuration for this component's role
        self.system_prompt = self._build_system_prompt()
    
    def set_communication_component(self, communication_component) -> None:
        """
        Set reference to Communication component for user feedback.
        
        Args:
            communication_component: Instance of CommunicationComponent
        """
        self.communication = communication_component
    
    def set_consciousness_component(self, consciousness_component) -> None:
        """
        Set reference to Consciousness component for context.
        
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
        return """You are a User Story Creator component in an AI agent system that transforms requirements into user stories.

Your responsibilities:
1. Transform user requirements into well-structured user stories
2. Create comprehensive acceptance criteria for each user story
3. Follow standard user story format: "As a [user type], I want [functionality] so that [benefit]"
4. Generate appropriate titles and prioritize stories
5. Ensure stories are testable and actionable

Best practices for user stories:
- Keep stories focused on user value and outcomes
- Make acceptance criteria specific and testable
- Use clear, non-technical language when possible
- Include edge cases and error conditions in criteria
- Ensure stories are appropriately sized (not too big or too small)

Standard user story template:
- Title: Short, descriptive name
- Description: "As a [user type], I want [functionality] so that [benefit]"
- Acceptance Criteria: List of specific, testable conditions

Priority levels: critical, high, medium, low
User types: Consider different user roles (end user, admin, system, etc.)"""
    
    def process_requirements(self, requirements: List[str], context: str = "") -> List[str]:
        """
        Process a list of requirements and create user stories.
        
        This is the main entry point for transforming requirements into
        user stories. It handles multiple requirements and creates stories
        for each one.
        
        Args:
            requirements (List[str]): List of requirement descriptions
            context (str): Additional context about the requirements
            
        Returns:
            List[str]: List of created user story IDs
        """
        created_story_ids = []
        
        try:
            for requirement in requirements:
                story_id = self._create_user_story_from_requirement(requirement, context)
                if story_id:
                    created_story_ids.append(story_id)
            
            # Provide feedback about created stories
            self._provide_creation_feedback(created_story_ids)
            
            return created_story_ids
            
        except Exception as e:
            print(f"ERROR: Failed to process requirements: {str(e)}")
            if self.communication:
                self.communication.display_agent_response("I had trouble creating user stories from those requirements. Could you please clarify them?")
            return []
    
    def _create_user_story_from_requirement(self, requirement: str, context: str = "") -> Optional[str]:
        """
        Create a single user story from a requirement.
        
        Args:
            requirement (str): Individual requirement description
            context (str): Additional context for the requirement
            
        Returns:
            Optional[str]: Created story ID if successful, None otherwise
        """
        try:
            # Get project context if available
            project_context = ""
            if self.consciousness:
                project_context = self.consciousness.get_context_summary()
            
            # Generate user story using AI
            story_data = self._generate_user_story_with_ai(requirement, context, project_context)
            
            if story_data:
                # Create and store the user story
                story_id = self.memory.add_user_story(
                    title=story_data["title"],
                    description=story_data["description"],
                    acceptance_criteria=story_data["acceptance_criteria"],
                    user_type=story_data.get("user_type", "user"),
                    priority=story_data.get("priority", "medium")
                )
                
                return story_id
            
            return None
            
        except Exception as e:
            print(f"ERROR: Failed to create user story: {str(e)}")
            return None
    
    def _generate_user_story_with_ai(self, requirement: str, context: str, project_context: str) -> Optional[Dict[str, Any]]:
        """
        Use AI to generate a user story from a requirement.
        
        Args:
            requirement (str): The requirement to transform
            context (str): Additional context about the requirement
            project_context (str): Overall project context
            
        Returns:
            Optional[Dict[str, Any]]: Generated user story data or None if failed
        """
        # Build prompt for AI generation
        user_prompt = f"""
        Project Context:
        {project_context if project_context else "No specific project context available"}
        
        Additional Context:
        {context if context else "No additional context provided"}
        
        Requirement to Transform:
        "{requirement}"
        
        Create a well-structured user story from this requirement. Consider:
        1. Who is the user or beneficiary?
        2. What functionality do they need?
        3. What value or benefit does this provide?
        4. What are the specific, testable acceptance criteria?
        
        Respond in this JSON format:
        {{
            "title": "Short descriptive title for the user story",
            "description": "As a [user type], I want [functionality] so that [benefit]",
            "user_type": "The type of user (user, admin, system, etc.)",
            "priority": "critical|high|medium|low",
            "acceptance_criteria": [
                "Specific, testable criterion 1",
                "Specific, testable criterion 2",
                "Specific, testable criterion 3"
            ]
        }}
        """
        
        try:
            response = self.ai.generate_response(self.system_prompt, user_prompt)
            
            # Parse JSON response
            import json
            story_data = json.loads(response.strip())
            
            # Validate required fields
            required_fields = ["title", "description", "acceptance_criteria"]
            if all(field in story_data for field in required_fields):
                return story_data
            else:
                print(f"ERROR: Generated story missing required fields: {required_fields}")
                return None
                
        except Exception as e:
            print(f"ERROR: Failed to generate user story with AI: {str(e)}")
            return None
    
    def _provide_creation_feedback(self, created_story_ids: List[str]) -> None:
        """
        Provide feedback to user about created stories.
        
        Args:
            created_story_ids (List[str]): List of created story IDs
        """
        if not self.communication or not created_story_ids:
            return
        
        if len(created_story_ids) == 1:
            story = self.memory.get_user_story(created_story_ids[0])
            if story:
                response = f"I've created user story {story['story_id']}: {story['title']}\n\n"
                response += f"{story['description']}\n\n"
                response += "Acceptance Criteria:\n"
                for i, criteria in enumerate(story['acceptance_criteria'], 1):
                    response += f"{i}. {criteria}\n"
                self.communication.display_agent_response(response.strip())
        else:
            response = f"I've created {len(created_story_ids)} user stories:\n"
            for story_id in created_story_ids:
                story = self.memory.get_user_story(story_id)
                if story:
                    response += f"• {story['story_id']}: {story['title']}\n"
            self.communication.display_agent_response(response.strip())
    
    def update_user_story(self, story_id: str, **updates) -> bool:
        """
        Update an existing user story.
        
        Args:
            story_id (str): ID of story to update
            **updates: Fields to update
            
        Returns:
            bool: True if updated successfully
        """
        success = self.memory.update_user_story(story_id, **updates)
        
        if success and self.communication:
            self.communication.display_agent_response(f"User story {story_id} has been updated.")
        elif not success and self.communication:
            self.communication.display_agent_response(f"Could not find user story {story_id} to update.")
        
        return success
    
    def refine_user_story(self, story_id: str, refinement_request: str) -> bool:
        """
        Refine an existing user story based on user feedback.
        
        Args:
            story_id (str): ID of story to refine
            refinement_request (str): What the user wants to change or improve
            
        Returns:
            bool: True if refinement was successful
        """
        try:
            # Get existing story
            story = self.memory.get_user_story(story_id)
            if not story:
                if self.communication:
                    self.communication.display_agent_response(f"User story {story_id} not found.")
                return False
            
            # Generate refinement using AI
            refined_story = self._refine_story_with_ai(story, refinement_request)
            
            if refined_story:
                # Update the story
                success = self.memory.update_user_story(story_id, **refined_story)
                
                if success and self.communication:
                    updated_story = self.memory.get_user_story(story_id)
                    response = f"I've refined user story {story_id}:\n\n"
                    response += f"{updated_story['description']}\n\n"
                    response += "Updated Acceptance Criteria:\n"
                    for i, criteria in enumerate(updated_story['acceptance_criteria'], 1):
                        response += f"{i}. {criteria}\n"
                    self.communication.display_agent_response(response.strip())
                
                return success
            
            return False
            
        except Exception as e:
            print(f"ERROR: Failed to refine user story: {str(e)}")
            return False
    
    def _refine_story_with_ai(self, story: Dict[str, Any], refinement_request: str) -> Optional[Dict[str, Any]]:
        """
        Use AI to refine an existing user story.
        
        Args:
            story (Dict[str, Any]): Current story data
            refinement_request (str): What to refine
            
        Returns:
            Optional[Dict[str, Any]]: Refined story data
        """
        user_prompt = f"""
        Current User Story:
        Title: {story['title']}
        Description: {story['description']}
        Priority: {story['priority']}
        Acceptance Criteria:
        {chr(10).join([f"- {criteria}" for criteria in story['acceptance_criteria']])}
        
        Refinement Request:
        "{refinement_request}"
        
        Please refine this user story based on the request. Maintain the same format and improve the relevant aspects.
        
        Respond in this JSON format:
        {{
            "title": "Refined title if needed",
            "description": "Refined description maintaining user story format",
            "priority": "Updated priority if relevant",
            "acceptance_criteria": [
                "Refined or new acceptance criteria"
            ]
        }}
        """
        
        try:
            response = self.ai.generate_response(self.system_prompt, user_prompt)
            
            import json
            refined_data = json.loads(response.strip())
            return refined_data
            
        except Exception as e:
            print(f"ERROR: Failed to refine story with AI: {str(e)}")
            return None
    
    def list_user_stories(self, status_filter: str = None) -> None:
        """
        Display list of user stories to the user.
        
        Args:
            status_filter (str, optional): Filter by status (draft, ready, etc.)
        """
        if not self.communication:
            return
        
        if status_filter:
            stories = self.memory.get_user_stories_by_status(status_filter)
            header = f"User Stories ({status_filter} status):"
        else:
            stories = self.memory.get_all_user_stories()
            header = "All User Stories:"
        
        if not stories:
            self.communication.display_agent_response("No user stories found.")
            return
        
        response = f"{header}\n"
        for story in stories:
            response += f"• {story['story_id']}: {story['title']} [{story['status']}]\n"
        
        self.communication.display_agent_response(response.strip())
    
    def show_user_story_details(self, story_id: str) -> None:
        """
        Display detailed information about a specific user story.
        
        Args:
            story_id (str): ID of story to show
        """
        if not self.communication:
            return
        
        story = self.memory.get_user_story(story_id)
        if not story:
            self.communication.display_agent_response(f"User story {story_id} not found.")
            return
        
        response = f"User Story {story['story_id']}: {story['title']}\n"
        response += f"Priority: {story['priority']} | Status: {story['status']}\n\n"
        response += f"{story['description']}\n\n"
        response += "Acceptance Criteria:\n"
        for i, criteria in enumerate(story['acceptance_criteria'], 1):
            response += f"{i}. {criteria}\n"
        
        self.communication.display_agent_response(response.strip())
    
    def export_stories(self, format_type: str = "detailed") -> None:
        """
        Export all user stories in specified format.
        
        Args:
            format_type (str): Export format (list, detailed, markdown)
        """
        if not self.communication:
            return
        
        exported_text = self.memory.export_user_stories(format_type)
        self.communication.display_agent_response(f"User Stories Export ({format_type} format):\n\n{exported_text}")
    
    def get_story_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about current user stories.
        
        Returns:
            Dict[str, Any]: Statistics about the story collection
        """
        return self.memory.get_story_statistics()
    
    def clear_all_stories(self) -> None:
        """
        Clear all user stories for fresh start.
        """
        self.memory.clear_all_stories()
        
        if self.communication:
            self.communication.display_to_user_only("All user stories cleared. Starting fresh!")
    
    def __str__(self) -> str:
        """String representation for debugging."""
        stats = self.get_story_statistics()
        total = stats.get("total_stories", 0)
        return f"UserStoryCreatorComponent(total_stories={total})"