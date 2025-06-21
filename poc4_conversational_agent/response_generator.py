import json
import os
from typing import Dict, Any
from anthropic import Anthropic
from dotenv import load_dotenv
from project_manager import project_manager
from token_tracker import token_tracker
from constants import DEFAULT_MODEL, API_SETTINGS, get_context_usage_percentage, should_compact_conversation, DISPLAY_SETTINGS

load_dotenv()

def generate_response() -> Dict[str, Any]:
    """
    Generate response using Claude API based on intent and context.
    Fourth step in the conversation pipeline.
    """
    
    # Load current state from project
    state = project_manager.load_project_state()
    if not state:
        raise Exception("No project selected or unable to load project state")
    
    processed_input = state.get("processed_input", {})
    context = state.get("context", {})
    intent = state.get("intent", {})
    
    # Generate response using Claude and capture token usage
    api_result = call_claude_api(
        processed_input.get("text", ""),
        intent,
        context
    )
    
    generated_text = api_result["text"]
    token_usage = api_result["token_usage"]
    
    # Track token usage
    current_project = project_manager.get_current_project()
    if current_project and token_usage:
        token_tracker.track_message_tokens(
            project_name=current_project,
            model_name=token_usage["model"],
            input_tokens=token_usage["input_tokens"],
            output_tokens=token_usage["output_tokens"],
            user_message=processed_input.get("text", ""),
            assistant_response=generated_text
        )
    
    response_data = {
        "generated_text": generated_text,
        "reasoning": f"Responded to {intent.get('primary_intent', 'general')} intent with confidence {intent.get('confidence', 0):.2f}",
        "sources": [token_usage.get("model", "claude-3-haiku")],
        "token_usage": token_usage
    }
    
    # Update state
    state["response"] = response_data
    state["current_step"] = "output_formatting"
    state["pipeline_config"]["current_position"] = 4
    
    # Save state to project
    project_manager.save_project_state(state)
    
    # Display response info with token usage
    display_response_info(response_data, context)
    
    return response_data

def display_response_info(response_data: Dict, context: Dict):
    """Display response generation info including token usage and context percentage."""
    
    generated_text = response_data.get("generated_text", "")
    token_usage = response_data.get("token_usage", {})
    
    # Basic info
    print(f"✅ Response generated: {len(generated_text)} characters")
    
    # Token usage info
    if token_usage and DISPLAY_SETTINGS["show_token_usage"]:
        input_tokens = token_usage.get("input_tokens", 0)
        output_tokens = token_usage.get("output_tokens", 0)
        total_tokens = input_tokens + output_tokens
        cost = token_usage.get("total_cost", 0)
        
        print(f"   Tokens: {input_tokens} in + {output_tokens} out = {total_tokens} total")
        print(f"   Cost: ${cost:.6f}")
    
    # Context usage info
    if DISPLAY_SETTINGS["show_context_percentage"]:
        conversation_history = context.get("conversation_history", [])
        estimated_context_tokens = token_tracker.calculate_project_context_tokens("", conversation_history)
        
        percentage = get_context_usage_percentage(estimated_context_tokens)
        colors = DISPLAY_SETTINGS["colors"]
        
        # Color coding based on usage level
        if percentage >= 75:
            color = colors["red"]
        elif percentage >= 65:
            color = colors["yellow"] 
        else:
            color = colors["green"]
        
        print(f"   Context usage: {color}{percentage:.1f}%{colors['normal']} of available window")
        
        # Compaction warning
        if should_compact_conversation(estimated_context_tokens):
            print(f"   {colors['yellow']}⚠️  Consider running /compact to optimize context usage{colors['normal']}")

def call_claude_api(user_text: str, intent: Dict, context: Dict) -> Dict[str, Any]:
    """
    Call Claude API to generate response based on user input and context.
    Returns both the response text and token usage information.
    """
    
    # Initialize Claude client
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    # Build context for Claude
    conversation_history = context.get("conversation_history", [])
    intent_info = intent.get("primary_intent", "general")
    confidence = intent.get("confidence", 0)
    context_needed = intent.get("context_needed", False)
    
    # Create system prompt
    system_prompt = f"""You are a conversational assistant in a pipeline demonstration. 
    
Current conversation analysis:
- User intent: {intent_info} (confidence: {confidence:.2f})
- Context needed: {context_needed}
- Conversation history length: {len(conversation_history)} messages

Respond naturally and helpfully to the user's message."""
    
    # Build conversation context
    messages = []
    
    # Add recent conversation history (last 5 messages)
    recent_history = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history
    for msg in recent_history[:-1]:  # Exclude current message
        if msg.get("role") == "user":
            messages.append({"role": "user", "content": msg.get("text", "")})
        elif msg.get("role") == "assistant":
            messages.append({"role": "assistant", "content": msg.get("text", "")})
    
    # Add current user message
    messages.append({"role": "user", "content": user_text})
    
    try:
        # Call Claude API
        response = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=API_SETTINGS["max_tokens"],
            temperature=API_SETTINGS["temperature"],
            system=system_prompt,
            messages=messages
        )
        
        # Extract token usage from API response
        usage = response.usage
        input_tokens = usage.input_tokens
        output_tokens = usage.output_tokens
        
        # Calculate costs
        from constants import get_model_info
        model_info = get_model_info(DEFAULT_MODEL)
        input_cost = input_tokens * model_info["cost_per_input_token"]
        output_cost = output_tokens * model_info["cost_per_output_token"]
        total_cost = input_cost + output_cost
        
        return {
            "text": response.content[0].text,
            "token_usage": {
                "model": DEFAULT_MODEL,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "input_cost": input_cost,
                "output_cost": output_cost,
                "total_cost": total_cost
            }
        }
        
    except Exception as e:
        print(f"Error calling Claude API: {e}")
        error_message = f"I apologize, but I encountered an error while processing your request: {str(e)}"
        
        # Return error response with no token usage
        return {
            "text": error_message,
            "token_usage": {
                "model": DEFAULT_MODEL,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "input_cost": 0.0,
                "output_cost": 0.0,
                "total_cost": 0.0
            }
        }

if __name__ == "__main__":
    # Test the function
    result = generate_response()
    print(f"Response: {result}")