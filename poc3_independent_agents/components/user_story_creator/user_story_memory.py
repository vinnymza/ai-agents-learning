#!/usr/bin/env python3
"""
User Story Memory - User Story Persistence Logic

This class handles all memory operations specific to the User Story Creator component.
It understands the user story data structure and provides high-level methods for
storing, retrieving, and managing user stories and their acceptance criteria.

Key responsibilities:
- Manage user story collection and structure
- Add user stories with proper metadata (IDs, timestamps, status)
- Update existing user stories and acceptance criteria
- Retrieve user stories for review and modification
- Track user story lifecycle and status changes

Design principle: The User Story Creator component should not know about JSON
structure or file operations - it should only call high-level methods like
add_user_story() and update_acceptance_criteria().
"""
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add shared directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))
from memory_manager import MemoryManager


class UserStoryMemory:
    """
    Handles all persistent memory operations for user story data.
    
    This class encapsulates the user story memory structure and provides
    a clean interface for the User Story Creator component to manage
    user stories without dealing with file I/O or JSON structure.
    """
    
    def __init__(self, memory_manager: MemoryManager):
        """
        Initialize user story memory with storage backend.
        
        Args:
            memory_manager (MemoryManager): Storage abstraction for file operations
        """
        self.storage = memory_manager
        self._ensure_memory_structure()
    
    def _ensure_memory_structure(self) -> None:
        """
        Initialize the user story memory structure if it doesn't exist.
        
        Creates the basic user story collection structure when starting
        fresh or when memory file is empty.
        """
        data = self.storage.read()
        
        # Initialize structure if empty
        if not data:
            data = {
                "project_context": {
                    "name": "",
                    "description": "",
                    "created_at": datetime.now().isoformat()
                },
                "user_stories": [],
                "story_templates": {
                    "default": "As a {user_type}, I want {functionality} so that {benefit}",
                    "system": "As a system, I need {functionality} so that {benefit}",
                    "stakeholder": "As a {stakeholder_type}, I want {functionality} so that {business_value}"
                },
                "metadata": {
                    "total_stories": 0,
                    "stories_by_status": {
                        "draft": 0,
                        "ready": 0,
                        "in_progress": 0,
                        "completed": 0
                    },
                    "last_updated": datetime.now().isoformat()
                }
            }
            self.storage.write(data)
    
    def add_user_story(self, title: str, description: str, acceptance_criteria: List[str], 
                      user_type: str = "user", priority: str = "medium") -> str:
        """
        Add a new user story to the collection.
        
        This is the main method for creating user stories. It handles
        story ID generation, timestamp creation, and metadata updates
        automatically.
        
        Args:
            title (str): Short title for the user story
            description (str): Full user story description (usually in "As a... I want... so that..." format)
            acceptance_criteria (List[str]): List of acceptance criteria
            user_type (str): Type of user this story is for (default: "user")
            priority (str): Priority level (low, medium, high, critical)
            
        Returns:
            str: Generated story ID for reference
        """
        data = self.storage.read()
        
        # Generate story ID
        story_count = len(data.get("user_stories", []))
        story_id = f"US{story_count + 1:03d}"
        
        # Create user story entry
        user_story = {
            "story_id": story_id,
            "title": title,
            "description": description,
            "user_type": user_type,
            "priority": priority,
            "acceptance_criteria": acceptance_criteria,
            "status": "draft",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "estimated_points": None,
            "tags": [],
            "related_requirements": []
        }
        
        # Add to collection
        data["user_stories"].append(user_story)
        
        # Update metadata
        self._update_metadata(data)
        
        # Persist changes
        self.storage.write(data)
        
        return story_id
    
    def update_user_story(self, story_id: str, **kwargs) -> bool:
        """
        Update an existing user story with new information.
        
        Args:
            story_id (str): ID of story to update
            **kwargs: Fields to update (title, description, acceptance_criteria, status, etc.)
            
        Returns:
            bool: True if story was found and updated, False otherwise
        """
        data = self.storage.read()
        
        for story in data.get("user_stories", []):
            if story["story_id"] == story_id:
                # Update provided fields
                for field, value in kwargs.items():
                    if field in story:
                        story[field] = value
                
                # Always update timestamp
                story["updated_at"] = datetime.now().isoformat()
                
                # Update metadata and persist
                self._update_metadata(data)
                self.storage.write(data)
                return True
        
        return False
    
    def get_user_story(self, story_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific user story by ID.
        
        Args:
            story_id (str): ID of story to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: User story data if found, None otherwise
        """
        data = self.storage.read()
        
        for story in data.get("user_stories", []):
            if story["story_id"] == story_id:
                return story.copy()
        
        return None
    
    def get_all_user_stories(self) -> List[Dict[str, Any]]:
        """
        Get all user stories in the collection.
        
        Returns:
            List[Dict[str, Any]]: All user stories ordered by creation date
        """
        data = self.storage.read()
        return data.get("user_stories", []).copy()
    
    def get_user_stories_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Filter user stories by status.
        
        Args:
            status (str): Status to filter by (draft, ready, in_progress, completed)
            
        Returns:
            List[Dict[str, Any]]: User stories with matching status
        """
        all_stories = self.get_all_user_stories()
        return [story for story in all_stories if story.get("status") == status]
    
    def get_user_stories_by_priority(self, priority: str) -> List[Dict[str, Any]]:
        """
        Filter user stories by priority.
        
        Args:
            priority (str): Priority to filter by (low, medium, high, critical)
            
        Returns:
            List[Dict[str, Any]]: User stories with matching priority
        """
        all_stories = self.get_all_user_stories()
        return [story for story in all_stories if story.get("priority") == priority]
    
    def add_acceptance_criteria(self, story_id: str, criteria: str) -> bool:
        """
        Add an acceptance criterion to an existing user story.
        
        Args:
            story_id (str): ID of story to update
            criteria (str): New acceptance criterion to add
            
        Returns:
            bool: True if criterion was added, False if story not found
        """
        data = self.storage.read()
        
        for story in data.get("user_stories", []):
            if story["story_id"] == story_id:
                story["acceptance_criteria"].append(criteria)
                story["updated_at"] = datetime.now().isoformat()
                
                self._update_metadata(data)
                self.storage.write(data)
                return True
        
        return False
    
    def remove_acceptance_criteria(self, story_id: str, criteria_index: int) -> bool:
        """
        Remove an acceptance criterion from a user story.
        
        Args:
            story_id (str): ID of story to update
            criteria_index (int): Index of criterion to remove
            
        Returns:
            bool: True if criterion was removed, False if story/index not found
        """
        data = self.storage.read()
        
        for story in data.get("user_stories", []):
            if story["story_id"] == story_id:
                criteria_list = story["acceptance_criteria"]
                if 0 <= criteria_index < len(criteria_list):
                    criteria_list.pop(criteria_index)
                    story["updated_at"] = datetime.now().isoformat()
                    
                    self._update_metadata(data)
                    self.storage.write(data)
                    return True
        
        return False
    
    def link_requirement(self, story_id: str, requirement_id: str) -> bool:
        """
        Link a user story to a requirement from the consciousness context.
        
        Args:
            story_id (str): ID of user story
            requirement_id (str): ID of requirement to link
            
        Returns:
            bool: True if link was created, False if story not found
        """
        data = self.storage.read()
        
        for story in data.get("user_stories", []):
            if story["story_id"] == story_id:
                if requirement_id not in story["related_requirements"]:
                    story["related_requirements"].append(requirement_id)
                    story["updated_at"] = datetime.now().isoformat()
                    
                    self._update_metadata(data)
                    self.storage.write(data)
                return True
        
        return False
    
    def get_project_context(self) -> Dict[str, Any]:
        """
        Get project context information.
        
        Returns:
            Dict[str, Any]: Project context data
        """
        data = self.storage.read()
        return data.get("project_context", {})
    
    def update_project_context(self, name: str = None, description: str = None) -> None:
        """
        Update project context information.
        
        Args:
            name (str, optional): Project name
            description (str, optional): Project description
        """
        data = self.storage.read()
        
        if name is not None:
            data["project_context"]["name"] = name
        if description is not None:
            data["project_context"]["description"] = description
        
        self._update_metadata(data)
        self.storage.write(data)
    
    def get_story_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the user story collection.
        
        Returns:
            Dict[str, Any]: Statistics including counts by status, priority, etc.
        """
        data = self.storage.read()
        return data.get("metadata", {})
    
    def export_user_stories(self, format_type: str = "list") -> str:
        """
        Export user stories in a formatted text representation.
        
        Args:
            format_type (str): Export format ("list", "detailed", "markdown")
            
        Returns:
            str: Formatted user stories text
        """
        stories = self.get_all_user_stories()
        
        if format_type == "markdown":
            return self._export_as_markdown(stories)
        elif format_type == "detailed":
            return self._export_detailed(stories)
        else:
            return self._export_as_list(stories)
    
    def _export_as_list(self, stories: List[Dict[str, Any]]) -> str:
        """Export stories as simple list."""
        lines = ["User Stories:", "=" * 50]
        
        for story in stories:
            lines.append(f"{story['story_id']}: {story['title']}")
            lines.append(f"  {story['description']}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _export_detailed(self, stories: List[Dict[str, Any]]) -> str:
        """Export stories with full details."""
        lines = ["Detailed User Stories:", "=" * 50]
        
        for story in stories:
            lines.append(f"\n{story['story_id']}: {story['title']}")
            lines.append(f"Priority: {story['priority']} | Status: {story['status']}")
            lines.append(f"Description: {story['description']}")
            lines.append("Acceptance Criteria:")
            for i, criteria in enumerate(story['acceptance_criteria'], 1):
                lines.append(f"  {i}. {criteria}")
            lines.append("-" * 40)
        
        return "\n".join(lines)
    
    def _export_as_markdown(self, stories: List[Dict[str, Any]]) -> str:
        """Export stories as markdown."""
        lines = ["# User Stories", ""]
        
        for story in stories:
            lines.append(f"## {story['story_id']}: {story['title']}")
            lines.append(f"**Priority:** {story['priority']} | **Status:** {story['status']}")
            lines.append(f"\n{story['description']}")
            lines.append("\n### Acceptance Criteria")
            for criteria in story['acceptance_criteria']:
                lines.append(f"- {criteria}")
            lines.append("")
        
        return "\n".join(lines)
    
    def clear_all_stories(self) -> None:
        """
        Clear all user stories for fresh start.
        
        Useful for testing or starting a new project.
        """
        # Reset to empty structure
        self.storage.delete()
        self._ensure_memory_structure()
    
    def _update_metadata(self, data: Dict[str, Any]) -> None:
        """
        Update metadata with current statistics.
        
        Args:
            data (Dict[str, Any]): Current memory data to update
        """
        stories = data.get("user_stories", [])
        
        # Count by status
        status_counts = {"draft": 0, "ready": 0, "in_progress": 0, "completed": 0}
        for story in stories:
            status = story.get("status", "draft")
            if status in status_counts:
                status_counts[status] += 1
        
        data["metadata"] = {
            "total_stories": len(stories),
            "stories_by_status": status_counts,
            "last_updated": datetime.now().isoformat()
        }
    
    def __str__(self) -> str:
        """String representation for debugging."""
        data = self.storage.read()
        total = data.get("metadata", {}).get("total_stories", 0)
        return f"UserStoryMemory(total_stories={total})"