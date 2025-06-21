import json
import datetime
from typing import Dict, Any
from project_manager import project_manager

def format_output() -> Dict[str, Any]:
    """
    Format the final response for user display.
    Fifth and final step in the conversation pipeline.
    """
    
    # Load current state from project
    state = project_manager.load_project_state()
    if not state:
        raise Exception("No project selected or unable to load project state")
    
    response = state.get("response", {})
    intent = state.get("intent", {})
    processed_input = state.get("processed_input", {})
    
    # Format the output
    formatted_output = {
        "formatted_response": format_response_text(response.get("generated_text", "")),
        "metadata": {
            "timestamp": datetime.datetime.now().isoformat(),
            "intent": intent.get("primary_intent", "unknown"),
            "confidence": intent.get("confidence", 0),
            "processing_time": calculate_processing_time(processed_input.get("timestamp")),
            "pipeline_steps": 5,
            "response_length": len(response.get("generated_text", ""))
        }
    }
    
    # Add assistant response to conversation history
    conversation_history = state.get("context", {}).get("conversation_history", [])
    conversation_history.append({
        "role": "assistant",
        "text": formatted_output["formatted_response"],
        "timestamp": formatted_output["metadata"]["timestamp"],
        "metadata": formatted_output["metadata"]
    })
    
    # Update state
    state["final_output"] = formatted_output
    state["current_step"] = "completed"
    state["pipeline_config"]["current_position"] = 5
    state["context"]["conversation_history"] = conversation_history
    
    # Save state to project
    project_manager.save_project_state(state)
    
    print(f"✅ Output formatted: {formatted_output['metadata']['response_length']} characters")
    return formatted_output

def format_response_text(raw_response: str) -> str:
    """
    Apply formatting rules to the raw response.
    This could include:
    - Adding conversational markers
    - Formatting for specific output channels (CLI, web, etc.)
    - Adding context hints
    """
    
    if not raw_response:
        return "I'm sorry, I couldn't generate a response. Please try again."
    
    # Clean up the response
    formatted = raw_response.strip()
    
    # Ensure proper sentence ending
    if not formatted.endswith(('.', '!', '?')):
        formatted += '.'
    
    return formatted

def calculate_processing_time(start_timestamp: str) -> float:
    """
    Calculate how long the pipeline took to process.
    """
    if not start_timestamp:
        return 0.0
    
    try:
        start_time = datetime.datetime.fromisoformat(start_timestamp)
        end_time = datetime.datetime.now()
        return (end_time - start_time).total_seconds()
    except:
        return 0.0

def display_formatted_output(formatted_output: Dict[str, Any]) -> None:
    """
    Display the formatted output to the user.
    This function handles the actual presentation.
    """
    
    response = formatted_output.get("formatted_response", "")
    metadata = formatted_output.get("metadata", {})
    
    print("\n" + "="*50)
    print("CONVERSATIONAL AGENT RESPONSE")
    print("="*50)
    print(f"\n{response}\n")
    
    print("-" * 30)
    print("PIPELINE METADATA:")
    print(f"Intent: {metadata.get('intent', 'unknown')} (confidence: {metadata.get('confidence', 0):.2f})")
    print(f"Processing time: {metadata.get('processing_time', 0):.2f}s")
    print(f"Response length: {metadata.get('response_length', 0)} characters")
    print(f"Pipeline steps: {metadata.get('pipeline_steps', 0)}")
    print("-" * 30)

if __name__ == "__main__":
    # Test the function
    result = format_output()
    display_formatted_output(result)
    print(f"Final output: {result}")