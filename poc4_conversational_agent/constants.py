# Configuration constants for the conversational agent

# Available models and their context windows
MODELS = {
    "claude-3-5-haiku-latest": {
        "context_window": 200000,  # 200K tokens
        "display_name": "Claude 3.5 Haiku",
        "cost_per_input_token": 0.00000080,  # $0.80 per million tokens
        "cost_per_output_token": 0.00000400   # $4 per million tokens
    },
    "claude-sonnet-4-0": {
        "context_window": 200000,  # 200K tokens
        "display_name": "Claude 4 Sonnet", 
        "cost_per_input_token": 0.000003,    # $3 per million tokens
        "cost_per_output_token": 0.000015    # $15 per million tokens
    },
    "claude-opus-4-0": {
        "context_window": 200000,  # 200K tokens
        "display_name": "Claude 4 Opus",
        "cost_per_input_token": 0.000015,    # $15 per million tokens
        "cost_per_output_token": 0.000075    # $75 per million tokens
    }
}

# Default model to use
DEFAULT_MODEL = "claude-3-5-haiku-latest"

# Context management settings
CONTEXT_SETTINGS = {
    # Maximum percentage of context window to use before suggesting compaction
    "compaction_threshold_percent": 75,
    
    # Maximum number of messages to keep in context (regardless of tokens)
    "max_messages_in_context": 50,
    
    # Minimum number of messages to always keep (recent conversation)
    "min_messages_to_keep": 10,
    
    # When compacting, keep this percentage of recent messages
    "compaction_keep_recent_percent": 30,
    
    # Reserve tokens for response generation
    "response_token_reserve": 4000
}

# Token tracking settings
TOKEN_TRACKING = {
    # Track token usage per project
    "track_per_project": True,
    
    # Track token usage per message
    "track_per_message": True,
    
    # Track aggregated statistics
    "track_aggregated": True,
    
    # File to store token usage data
    "usage_file": "token_usage.json",
    
    # Maximum entries to keep in detailed logs (to prevent file bloat)
    "max_detailed_entries": 1000
}

# API settings
API_SETTINGS = {
    # Maximum tokens to request from API
    "max_tokens": 4000,
    
    # Temperature for response generation
    "temperature": 0.7,
    
    # Top-p for response generation
    "top_p": 0.9
}

# Display settings
DISPLAY_SETTINGS = {
    # Show token usage in pipeline output
    "show_token_usage": True,
    
    # Show context percentage in pipeline output
    "show_context_percentage": True,
    
    # Warn when approaching context limit
    "warn_context_threshold": 65,
    
    # Colors for different warning levels (if terminal supports)
    "colors": {
        "normal": "\033[0m",
        "green": "\033[92m", 
        "yellow": "\033[93m",
        "red": "\033[91m",
        "bold": "\033[1m"
    }
}

def get_model_info(model_name: str = None) -> dict:
    """Get information about a specific model."""
    if model_name is None:
        model_name = DEFAULT_MODEL
    return MODELS.get(model_name, MODELS[DEFAULT_MODEL])

def get_context_limit(model_name: str = None) -> int:
    """Get the context window limit for a model."""
    return get_model_info(model_name)["context_window"]

def calculate_available_context(model_name: str = None) -> int:
    """Calculate available context tokens after reserving for response."""
    total_context = get_context_limit(model_name)
    reserved = CONTEXT_SETTINGS["response_token_reserve"]
    return total_context - reserved

def should_compact_conversation(current_tokens: int, model_name: str = None) -> bool:
    """Determine if conversation should be compacted based on token usage."""
    available = calculate_available_context(model_name)
    threshold = CONTEXT_SETTINGS["compaction_threshold_percent"] / 100
    return current_tokens >= (available * threshold)

def get_context_usage_percentage(current_tokens: int, model_name: str = None) -> float:
    """Calculate what percentage of context window is being used."""
    available = calculate_available_context(model_name)
    return (current_tokens / available) * 100

def get_warning_level(percentage: float) -> str:
    """Get warning level based on context usage percentage."""
    if percentage >= CONTEXT_SETTINGS["compaction_threshold_percent"]:
        return "critical"
    elif percentage >= DISPLAY_SETTINGS["warn_context_threshold"]:
        return "warning"
    else:
        return "normal"