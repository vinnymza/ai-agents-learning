import json
import datetime
from typing import Dict, Any
from project_manager import project_manager

def process_input(user_input: str) -> Dict[str, Any]:
    """
    Process raw user input and extract basic metadata.
    First step in the conversation pipeline.
    """
    
    # Load current state from project
    state = project_manager.load_project_state()
    if not state:
        raise Exception("No project selected or unable to load project state")
    
    # Process the input
    processed_data = {
        "text": user_input.strip(),
        "timestamp": datetime.datetime.now().isoformat(),
        "metadata": {
            "length": len(user_input),
            "word_count": len(user_input.split()),
            "has_question": "?" in user_input,
            "has_exclamation": "!" in user_input,
            "is_empty": len(user_input.strip()) == 0
        }
    }
    
    # Update state
    state["user_input"] = user_input
    state["processed_input"] = processed_data
    state["current_step"] = "context_building"
    state["pipeline_config"]["current_position"] = 1
    
    # Save state to project
    project_manager.save_project_state(state)
    
    print(f"✅ Input processed: {processed_data['metadata']['word_count']} words")
    return processed_data

if __name__ == "__main__":
    # Test the function
    test_input = input("Enter test input: ")
    result = process_input(test_input)
    print(f"Processed: {result}")