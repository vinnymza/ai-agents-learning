import json
import re
from typing import Dict, Any, List
from project_manager import project_manager

def analyze_intent() -> Dict[str, Any]:
    """
    Analyze user intent from processed input and context.
    Third step in the conversation pipeline.
    """
    
    # Load current state from project
    state = project_manager.load_project_state()
    if not state:
        raise Exception("No project selected or unable to load project state")
    
    processed_input = state.get("processed_input", {})
    context = state.get("context", {})
    user_text = processed_input.get("text", "").lower()
    
    # Simple intent classification
    intent_data = {
        "primary_intent": classify_intent(user_text),
        "confidence": calculate_confidence(user_text),
        "entities": extract_entities(user_text),
        "context_needed": determine_context_need(user_text, context)
    }
    
    # Update state
    state["intent"] = intent_data
    state["current_step"] = "response_generation"
    state["pipeline_config"]["current_position"] = 3
    
    # Save state to project
    project_manager.save_project_state(state)
    
    print(f"✅ Intent analyzed: {intent_data['primary_intent']} (confidence: {intent_data['confidence']:.2f})")
    return intent_data

def classify_intent(text: str) -> str:
    """
    Simple rule-based intent classification.
    In a real system, this would use ML models or LLMs.
    """
    
    # Define intent patterns
    patterns = {
        "question": [r"\?", r"^(what|how|why|when|where|who)", r"(tell me|explain)"],
        "greeting": [r"^(hi|hello|hey)", r"(good morning|good afternoon)", r"greetings"],
        "request": [r"(can you|could you|please)", r"(help me|assist)", r"(i need|i want)"],
        "information": [r"(about|regarding|concerning)", r"(information|details|facts)"],
        "goodbye": [r"(bye|goodbye|farewell)", r"(see you|talk later)", r"(thanks|thank you).*bye"],
        "clarification": [r"(what do you mean|clarify|explain that)", r"(i don't understand|confused)"],
        "feedback": [r"(good job|well done|excellent)", r"(not good|wrong|incorrect)"]
    }
    
    # Check patterns
    for intent, intent_patterns in patterns.items():
        for pattern in intent_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return intent
    
    return "general"

def calculate_confidence(text: str) -> float:
    """
    Calculate confidence score based on text characteristics.
    Simple heuristic - longer, more specific text = higher confidence.
    """
    if not text:
        return 0.0
    
    base_confidence = 0.5
    
    # Adjust based on length
    if len(text) > 50:
        base_confidence += 0.2
    elif len(text) < 10:
        base_confidence -= 0.2
    
    # Adjust based on specificity indicators
    specific_words = ["specific", "exactly", "precisely", "detailed", "particular"]
    if any(word in text.lower() for word in specific_words):
        base_confidence += 0.1
    
    # Adjust based on question marks (clear intent)
    if "?" in text:
        base_confidence += 0.1
    
    return min(1.0, max(0.0, base_confidence))

def extract_entities(text: str) -> List[Dict[str, str]]:
    """
    Simple entity extraction.
    In a real system, this would use NER models.
    """
    entities = []
    
    # Simple patterns for common entities
    patterns = {
        "number": r"\b\d+\b",
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "url": r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        "capitalized": r"\b[A-Z][a-z]+\b"
    }
    
    for entity_type, pattern in patterns.items():
        matches = re.findall(pattern, text)
        for match in matches:
            entities.append({
                "type": entity_type,
                "value": match
            })
    
    return entities

def determine_context_need(text: str, context: Dict) -> bool:
    """
    Determine if this intent needs historical context to be properly addressed.
    """
    context_indicators = [
        "that", "it", "this", "previous", "before", "earlier", 
        "what we discussed", "as mentioned", "continue", "also"
    ]
    
    return any(indicator in text.lower() for indicator in context_indicators)

if __name__ == "__main__":
    # Test the function
    result = analyze_intent()
    print(f"Intent: {result}")