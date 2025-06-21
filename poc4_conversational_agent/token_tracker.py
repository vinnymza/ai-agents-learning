import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from constants import TOKEN_TRACKING, get_model_info

class TokenTracker:
    """Tracks token usage for conversations."""
    
    def __init__(self, usage_file: str = None):
        self.usage_file = usage_file or TOKEN_TRACKING["usage_file"]
        self.ensure_usage_file()
    
    def ensure_usage_file(self):
        """Ensure the token usage file exists with proper structure."""
        if not os.path.exists(self.usage_file):
            initial_structure = {
                "aggregated": {
                    "total_input_tokens": 0,
                    "total_output_tokens": 0,
                    "total_cost": 0.0,
                    "total_messages": 0,
                    "models_used": {},
                    "created_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat()
                },
                "projects": {},
                "detailed_logs": []
            }
            
            with open(self.usage_file, 'w') as f:
                json.dump(initial_structure, f, indent=2)
    
    def load_usage_data(self) -> Dict[str, Any]:
        """Load token usage data from file."""
        try:
            with open(self.usage_file, 'r') as f:
                return json.load(f)
        except Exception:
            self.ensure_usage_file()
            with open(self.usage_file, 'r') as f:
                return json.load(f)
    
    def save_usage_data(self, data: Dict[str, Any]):
        """Save token usage data to file."""
        try:
            with open(self.usage_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving token usage data: {e}")
    
    def track_message_tokens(self, 
                           project_name: str,
                           model_name: str,
                           input_tokens: int,
                           output_tokens: int,
                           user_message: str = "",
                           assistant_response: str = "") -> Dict[str, Any]:
        """Track token usage for a single message."""
        
        data = self.load_usage_data()
        timestamp = datetime.now().isoformat()
        model_info = get_model_info(model_name)
        
        # Calculate costs
        input_cost = input_tokens * model_info["cost_per_input_token"]
        output_cost = output_tokens * model_info["cost_per_output_token"]
        total_cost = input_cost + output_cost
        
        # Update aggregated stats
        agg = data["aggregated"]
        agg["total_input_tokens"] += input_tokens
        agg["total_output_tokens"] += output_tokens
        agg["total_cost"] += total_cost
        agg["total_messages"] += 1
        agg["last_updated"] = timestamp
        
        # Track model usage
        if model_name not in agg["models_used"]:
            agg["models_used"][model_name] = {
                "input_tokens": 0,
                "output_tokens": 0,
                "cost": 0.0,
                "messages": 0
            }
        
        model_stats = agg["models_used"][model_name]
        model_stats["input_tokens"] += input_tokens
        model_stats["output_tokens"] += output_tokens
        model_stats["cost"] += total_cost
        model_stats["messages"] += 1
        
        # Update project stats
        if project_name not in data["projects"]:
            data["projects"][project_name] = {
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_cost": 0.0,
                "total_messages": 0,
                "models_used": {},
                "created_at": timestamp,
                "last_updated": timestamp
            }
        
        project = data["projects"][project_name]
        project["total_input_tokens"] += input_tokens
        project["total_output_tokens"] += output_tokens
        project["total_cost"] += total_cost
        project["total_messages"] += 1
        project["last_updated"] = timestamp
        
        # Track model usage for project
        if model_name not in project["models_used"]:
            project["models_used"][model_name] = {
                "input_tokens": 0,
                "output_tokens": 0,
                "cost": 0.0,
                "messages": 0
            }
        
        project_model_stats = project["models_used"][model_name]
        project_model_stats["input_tokens"] += input_tokens
        project_model_stats["output_tokens"] += output_tokens
        project_model_stats["cost"] += total_cost
        project_model_stats["messages"] += 1
        
        # Add detailed log entry
        if TOKEN_TRACKING["track_per_message"]:
            log_entry = {
                "timestamp": timestamp,
                "project": project_name,
                "model": model_name,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "input_cost": input_cost,
                "output_cost": output_cost,
                "total_cost": total_cost,
                "user_message_length": len(user_message),
                "assistant_response_length": len(assistant_response)
            }
            
            data["detailed_logs"].append(log_entry)
            
            # Limit detailed logs to prevent file bloat
            max_entries = TOKEN_TRACKING["max_detailed_entries"]
            if len(data["detailed_logs"]) > max_entries:
                # Keep the most recent entries
                data["detailed_logs"] = data["detailed_logs"][-max_entries:]
        
        # Save updated data
        self.save_usage_data(data)
        
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "total_cost": total_cost,
            "model": model_name
        }
    
    def get_project_stats(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Get token usage stats for a specific project."""
        data = self.load_usage_data()
        return data["projects"].get(project_name)
    
    def get_aggregated_stats(self) -> Dict[str, Any]:
        """Get aggregated token usage stats."""
        data = self.load_usage_data()
        return data["aggregated"]
    
    def get_recent_usage(self, limit: int = 10) -> list:
        """Get recent detailed usage logs."""
        data = self.load_usage_data()
        logs = data["detailed_logs"]
        return logs[-limit:] if logs else []
    
    def calculate_project_context_tokens(self, project_name: str, conversation_history: list) -> int:
        """Estimate tokens used by conversation history for context calculation."""
        # Simple estimation: ~4 characters per token
        # This is rough but good enough for context management
        total_chars = 0
        
        for message in conversation_history:
            text = message.get("text", "")
            total_chars += len(text)
        
        # Add some overhead for message structure, system prompts, etc.
        estimated_tokens = (total_chars // 4) + 500
        return estimated_tokens

# Global token tracker instance
token_tracker = TokenTracker()