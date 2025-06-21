import os
import json
import re
from typing import Dict, List, Optional, Any

class ProjectManager:
    """Manages conversation projects with separate JSON files."""
    
    def __init__(self, projects_dir: str = "projects"):
        self.projects_dir = projects_dir
        self.current_project = None
        self.ensure_projects_dir()
        
    def ensure_projects_dir(self):
        """Ensure the projects directory exists."""
        if not os.path.exists(self.projects_dir):
            os.makedirs(self.projects_dir)
    
    def validate_project_name(self, name: str) -> bool:
        """Validate project name: alphanumeric, -, &, _ only."""
        if not name:
            return False
        pattern = r'^[a-zA-Z0-9_&-]+$'
        return bool(re.match(pattern, name))
    
    def get_project_file_path(self, project_name: str) -> str:
        """Get the file path for a project."""
        return os.path.join(self.projects_dir, f"{project_name}.json")
    
    def project_exists(self, project_name: str) -> bool:
        """Check if a project exists."""
        return os.path.exists(self.get_project_file_path(project_name))
    
    def list_projects(self) -> List[str]:
        """List all available projects."""
        if not os.path.exists(self.projects_dir):
            return []
        
        projects = []
        for file in os.listdir(self.projects_dir):
            if file.endswith('.json'):
                project_name = file[:-5]  # Remove .json extension
                projects.append(project_name)
        
        return sorted(projects)
    
    def create_project(self, project_name: str) -> bool:
        """Create a new project with initial conversation state."""
        if not self.validate_project_name(project_name):
            return False
        
        if self.project_exists(project_name):
            return False
        
        initial_state = {
            "project_name": project_name,
            "created_at": self._get_current_timestamp(),
            "current_step": "input_processing",
            "user_input": "",
            "processed_input": {
                "text": "",
                "timestamp": "",
                "metadata": {}
            },
            "context": {
                "conversation_history": [],
                "session_info": {},
                "relevant_context": ""
            },
            "intent": {
                "primary_intent": "",
                "confidence": 0,
                "entities": [],
                "context_needed": False
            },
            "response": {
                "generated_text": "",
                "reasoning": "",
                "sources": []
            },
            "final_output": {
                "formatted_response": "",
                "metadata": {}
            },
            "pipeline_config": {
                "step_by_step": True,
                "allow_editing": True,
                "current_position": 0
            }
        }
        
        try:
            with open(self.get_project_file_path(project_name), 'w') as f:
                json.dump(initial_state, f, indent=2)
            return True
        except Exception:
            return False
    
    def select_project(self, project_name: str) -> bool:
        """Select a project as the current active project."""
        if not self.validate_project_name(project_name):
            return False
        
        if not self.project_exists(project_name):
            return False
        
        self.current_project = project_name
        return True
    
    def get_current_project(self) -> Optional[str]:
        """Get the current active project name."""
        return self.current_project
    
    def get_current_project_file_path(self) -> Optional[str]:
        """Get the file path for the current project."""
        if not self.current_project:
            return None
        return self.get_project_file_path(self.current_project)
    
    def load_project_state(self, project_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Load conversation state from a project file."""
        if not project_name:
            project_name = self.current_project
        
        if not project_name or not self.project_exists(project_name):
            return None
        
        try:
            with open(self.get_project_file_path(project_name), 'r') as f:
                return json.load(f)
        except Exception:
            return None
    
    def save_project_state(self, state: Dict[str, Any], project_name: Optional[str] = None) -> bool:
        """Save conversation state to a project file."""
        if not project_name:
            project_name = self.current_project
        
        if not project_name:
            return False
        
        try:
            # Ensure project name is in the state
            state["project_name"] = project_name
            
            with open(self.get_project_file_path(project_name), 'w') as f:
                json.dump(state, f, indent=2)
            return True
        except Exception:
            return False
    
    def get_project_info(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Get basic information about a project."""
        state = self.load_project_state(project_name)
        if not state:
            return None
        
        context = state.get("context", {})
        history = context.get("conversation_history", [])
        
        return {
            "name": project_name,
            "created_at": state.get("created_at", "Unknown"),
            "total_messages": len(history),
            "last_activity": history[-1].get("timestamp", "Never") if history else "Never"
        }
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()

# Global project manager instance
project_manager = ProjectManager()