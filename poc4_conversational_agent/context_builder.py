import json
from typing import Dict, Any, List
from project_manager import project_manager

def build_context() -> Dict[str, Any]:
    """
    Build conversation context from history and current state.
    Second step in the conversation pipeline.
    """
    
    # Load current state from project
    state = project_manager.load_project_state()
    if not state:
        raise Exception("No project selected or unable to load project state")
    
    processed_input = state.get("processed_input", {})
    history = state.get("context", {}).get("conversation_history", [])
    
    # Build context
    context_data = {
        "conversation_history": history,
        "session_info": {
            "total_messages": len(history),
            "session_start": history[0]["timestamp"] if history else processed_input.get("timestamp"),
            "last_user_message": processed_input.get("text", ""),
            "context_length": sum(len(msg.get("text", "")) for msg in history)
        },
        "relevant_context": extract_relevant_context(processed_input.get("text", ""), history)
    }
    
    # Add current message to history
    if processed_input.get("text"):
        history.append({
            "role": "user",
            "text": processed_input["text"],
            "timestamp": processed_input["timestamp"],
            "metadata": processed_input["metadata"]
        })
        context_data["conversation_history"] = history
    
    # Update state
    state["context"] = context_data
    state["current_step"] = "intent_analysis"
    state["pipeline_config"]["current_position"] = 2
    
    # Save state to project
    project_manager.save_project_state(state)
    
    print(f"✅ Context built: {context_data['session_info']['total_messages']} messages in history")
    return context_data

def extract_relevant_context(current_input: str, history: List[Dict]) -> str:
    """
    Simple context extraction - looks for related keywords in recent history.
    In a real system, this would use embeddings or more sophisticated matching.
    """
    if not history or not current_input:
        return ""
    
    # Get last 3 messages for simplicity
    recent_messages = history[-3:] if len(history) > 3 else history
    
    # Simple keyword matching
    current_words = set(current_input.lower().split())
    relevant_context = []
    
    for msg in recent_messages:
        msg_words = set(msg.get("text", "").lower().split())
        if current_words.intersection(msg_words):
            relevant_context.append(msg["text"])
    
    return " | ".join(relevant_context)

if __name__ == "__main__":
    # Test the function
    result = build_context()
    print(f"Context: {result}")