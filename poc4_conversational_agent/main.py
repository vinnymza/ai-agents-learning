#!/usr/bin/env python3
"""
PoC4: Conversational Agent Pipeline

A simple pipeline-based conversational agent that demonstrates
the complexity of conversation through discrete processing steps.
"""

import os
import json
import sys
from typing import Dict, Any

# Import our pipeline functions
from input_processor import process_input
from context_builder import build_context
from intent_analyzer import analyze_intent
from response_generator import generate_response
from output_formatter import format_output, display_formatted_output
from project_manager import project_manager
from token_tracker import token_tracker
from constants import get_context_usage_percentage, should_compact_conversation, DISPLAY_SETTINGS, CONTEXT_SETTINGS

def main():
    """
    Main CLI interface for the conversational agent pipeline.
    """
    
    print("🤖 PoC4: Conversational Agent Pipeline")
    print("Type /help for commands")
    
    while True:
        user_input = input("\n💬 ").strip()
        
        if not user_input:
            continue
            
        # Handle slash commands
        if user_input.startswith('/'):
            handle_slash_command(user_input)
        else:
            # Check if project is selected before allowing conversation
            if not project_manager.get_current_project():
                print("❌ No project selected. Use /project <name> to select or create a project.")
                print("Use /projects to see available projects.")
                continue
            
            # Default behavior: run full pipeline
            run_full_pipeline_with_input(user_input)


def handle_slash_command(command: str):
    """Handle slash commands."""
    
    parts = command.strip().split()
    cmd = parts[0].lower()
    
    if cmd == '/help':
        show_help()
    elif cmd == '/projects':
        list_projects()
    elif cmd == '/project':
        if len(parts) > 1:
            select_or_create_project(parts[1])
        else:
            print("❌ Usage: /project <name>")
    elif cmd == '/project-new':
        if len(parts) > 1:
            create_new_project(parts[1])
        else:
            print("❌ Usage: /project-new <name>")
    elif cmd == '/project-current':
        show_current_project()
    elif cmd == '/step':
        if not check_project_selected():
            return
        run_step_by_step_pipeline()
    elif cmd == '/view':
        if not check_project_selected():
            return
        view_conversation_state()
    elif cmd == '/edit':
        if not check_project_selected():
            return
        edit_conversation_state()
    elif cmd == '/reset':
        if not check_project_selected():
            return
        reset_conversation()
    elif cmd == '/tokens':
        if not check_project_selected():
            return
        show_token_stats()
    elif cmd == '/compact':
        if not check_project_selected():
            return
        compact_conversation()
    elif cmd == '/exit':
        print("Goodbye! 👋")
        sys.exit(0)
    else:
        print(f"❌ Unknown command: {command}")
        print("Type /help for available commands")

def show_help():
    """Show available slash commands."""
    
    print("\n📋 Available Commands:")
    print("Project Management:")
    print("  /projects           - List all conversation projects")
    print("  /project <name>     - Select or create a project")
    print("  /project-new <name> - Create a new project")
    print("  /project-current    - Show current project")
    print("\nConversation:")
    print("  /step    - Run step-by-step pipeline")
    print("  /view    - View conversation state")
    print("  /edit    - Edit conversation state")
    print("  /reset   - Reset current project conversation")
    print("  /tokens  - Show token usage statistics")
    print("  /compact - Analyze and compact conversation")
    print("  /help    - Show this help message")
    print("  /exit    - Exit the program")
    print("\nDefault: Type any message to run full pipeline")
    print("Note: Project must be selected before starting conversations")

def check_project_selected() -> bool:
    """Check if a project is selected."""
    if not project_manager.get_current_project():
        print("❌ No project selected. Use /project <name> to select a project.")
        return False
    return True

def list_projects():
    """List all available conversation projects."""
    projects = project_manager.list_projects()
    
    if not projects:
        print("📁 No projects found.")
        print("Use /project-new <name> to create a new project.")
        return
    
    print("\n📁 Available Projects:")
    current = project_manager.get_current_project()
    
    for project in projects:
        info = project_manager.get_project_info(project)
        if info:
            marker = "→" if project == current else " "
            print(f"{marker} {project} ({info['total_messages']} messages)")
        else:
            marker = "→" if project == current else " "
            print(f"{marker} {project}")

def select_or_create_project(project_name: str):
    """Select an existing project or create a new one."""
    if not project_manager.validate_project_name(project_name):
        print("❌ Invalid project name. Use only alphanumeric characters, -, &, and _")
        return
    
    if project_manager.project_exists(project_name):
        if project_manager.select_project(project_name):
            print(f"✅ Selected project: {project_name}")
            info = project_manager.get_project_info(project_name)
            if info:
                print(f"   Messages: {info['total_messages']}")
                print(f"   Last activity: {info['last_activity'][:19] if info['last_activity'] != 'Never' else 'Never'}")
        else:
            print(f"❌ Failed to select project: {project_name}")
    else:
        if project_manager.create_project(project_name):
            project_manager.select_project(project_name)
            print(f"✅ Created and selected new project: {project_name}")
        else:
            print(f"❌ Failed to create project: {project_name}")

def create_new_project(project_name: str):
    """Create a new project (fails if exists)."""
    if not project_manager.validate_project_name(project_name):
        print("❌ Invalid project name. Use only alphanumeric characters, -, &, and _")
        return
    
    if project_manager.project_exists(project_name):
        print(f"❌ Project '{project_name}' already exists. Use /project {project_name} to select it.")
        return
    
    if project_manager.create_project(project_name):
        project_manager.select_project(project_name)
        print(f"✅ Created and selected new project: {project_name}")
    else:
        print(f"❌ Failed to create project: {project_name}")

def show_current_project():
    """Show the current selected project."""
    current = project_manager.get_current_project()
    if current:
        print(f"📋 Current project: {current}")
        info = project_manager.get_project_info(current)
        if info:
            print(f"   Messages: {info['total_messages']}")
            print(f"   Created: {info['created_at'][:19]}")
            print(f"   Last activity: {info['last_activity'][:19] if info['last_activity'] != 'Never' else 'Never'}")
    else:
        print("❌ No project selected")

def run_full_pipeline_with_input(user_input: str):
    """Run the complete pipeline with provided input."""
    
    try:
        # Run each pipeline step
        process_input(user_input)
        build_context()
        analyze_intent()
        generate_response()
        formatted_output = format_output()
        
        # Display the result
        display_formatted_output(formatted_output)
        
    except Exception as e:
        print(f"❌ Pipeline error: {e}")
        current_project = project_manager.get_current_project()
        if current_project:
            print(f"Check projects/{current_project}.json for current state")

def run_step_by_step_pipeline():
    """Run the pipeline step by step with pauses for inspection/editing."""
    
    user_input = input("\n💬 Enter your message: ").strip()
    if not user_input:
        print("❌ Empty input. Please try again.")
        return
    
    print("\n🔄 Running step-by-step pipeline...")
    
    steps = [
        ("Processing input", lambda: process_input(user_input)),
        ("Building context", build_context),
        ("Analyzing intent", analyze_intent),
        ("Generating response", generate_response),
        ("Formatting output", format_output)
    ]
    
    for i, (step_name, step_function) in enumerate(steps, 1):
        print(f"\nStep {i}/5: {step_name}...")
        
        try:
            result = step_function()
            print(f"✅ {step_name} completed")
            
            # Offer to view/edit state after each step
            if i < len(steps):  # Don't pause after the last step
                action = input("\nPress Enter to continue, 'v' to view state, 'e' to edit state: ").strip().lower()
                
                if action == 'v':
                    view_conversation_state()
                elif action == 'e':
                    edit_conversation_state()
                    
        except Exception as e:
            print(f"❌ Error in {step_name}: {e}")
            return
    
    # Display final result
    state = project_manager.load_project_state()
    if state:
        formatted_output = state.get('final_output', {})
        display_formatted_output(formatted_output)

def view_conversation_state():
    """Display the current conversation state."""
    
    try:
        state = project_manager.load_project_state()
        if not state:
            print("❌ No project state available")
            return
        
        print("\n" + "="*50)
        print("CURRENT CONVERSATION STATE")
        print("="*50)
        print(f"Current step: {state.get('current_step', 'unknown')}")
        print(f"Pipeline position: {state.get('pipeline_config', {}).get('current_position', 0)}/5")
        
        print(f"\nUser input: {state.get('user_input', 'None')}")
        
        processed = state.get('processed_input', {})
        if processed.get('text'):
            print(f"Processed input: {processed['text'][:100]}...")
            print(f"Word count: {processed.get('metadata', {}).get('word_count', 0)}")
        
        intent = state.get('intent', {})
        if intent.get('primary_intent'):
            print(f"\nIntent: {intent['primary_intent']} (confidence: {intent.get('confidence', 0):.2f})")
            print(f"Entities: {len(intent.get('entities', []))}")
        
        response = state.get('response', {})
        if response.get('generated_text'):
            print(f"\nResponse length: {len(response['generated_text'])} characters")
            print(f"Response preview: {response['generated_text'][:100]}...")
        
        context = state.get('context', {})
        history = context.get('conversation_history', [])
        print(f"\nConversation history: {len(history)} messages")
        
        print("="*50)
        
    except Exception as e:
        print(f"❌ Error viewing state: {e}")

def edit_conversation_state():
    """Allow manual editing of the conversation state."""
    
    current_project = project_manager.get_current_project()
    if not current_project:
        print("❌ No project selected")
        return
    
    project_file = f"projects/{current_project}.json"
    
    print("\n📝 Edit Conversation State")
    print(f"This will open {project_file} in your default editor.")
    print("Make your changes and save the file.")
    
    # Try to open with common editors
    editors = ['code', 'nano', 'vim', 'notepad']  # VS Code, nano, vim, Windows notepad
    
    for editor in editors:
        try:
            os.system(f"{editor} {project_file}")
            break
        except:
            continue
    else:
        print(f"Could not open editor. Please manually edit {project_file}")
    
    input("Press Enter when you've finished editing...")
    print("✅ Ready to continue with modified state")

def reset_conversation():
    """Reset the conversation state to initial values."""
    
    current_project = project_manager.get_current_project()
    if not current_project:
        print("❌ No project selected")
        return
    
    confirm = input(f"\n⚠️  Reset conversation for project '{current_project}'? This will clear all history (y/N): ").strip().lower()
    
    if confirm == 'y':
        if project_manager.create_project(current_project):
            print(f"✅ Project '{current_project}' conversation reset")
        else:
            print(f"❌ Failed to reset project '{current_project}'")
    else:
        print("❌ Reset cancelled")

def show_token_stats():
    """Show token usage statistics for current project and overall."""
    
    current_project = project_manager.get_current_project()
    colors = DISPLAY_SETTINGS["colors"]
    
    print(f"\n{colors['bold']}📊 Token Usage Statistics{colors['normal']}")
    print("=" * 50)
    
    # Project stats
    project_stats = token_tracker.get_project_stats(current_project)
    if project_stats:
        print(f"\n{colors['bold']}Current Project: {current_project}{colors['normal']}")
        print(f"Total messages: {project_stats['total_messages']}")
        print(f"Total tokens: {project_stats['total_input_tokens'] + project_stats['total_output_tokens']:,}")
        print(f"  Input tokens: {project_stats['total_input_tokens']:,}")
        print(f"  Output tokens: {project_stats['total_output_tokens']:,}")
        print(f"Total cost: ${project_stats['total_cost']:.6f}")
        
        # Show models used
        if project_stats.get('models_used'):
            print(f"\nModels used:")
            for model, stats in project_stats['models_used'].items():
                print(f"  {model}: {stats['messages']} messages, ${stats['cost']:.6f}")
    else:
        print(f"\n{current_project}: No token usage data yet")
    
    # Context analysis
    state = project_manager.load_project_state()
    if state:
        conversation_history = state.get("context", {}).get("conversation_history", [])
        estimated_tokens = token_tracker.calculate_project_context_tokens(current_project, conversation_history)
        percentage = get_context_usage_percentage(estimated_tokens)
        
        print(f"\n{colors['bold']}Context Usage:{colors['normal']}")
        print(f"Estimated context tokens: {estimated_tokens:,}")
        print(f"Context usage: {percentage:.1f}%")
        
        if should_compact_conversation(estimated_tokens):
            print(f"{colors['yellow']}⚠️  Compaction recommended - use /compact{colors['normal']}")
        elif percentage > 50:
            print(f"{colors['yellow']}💡 Context usage is getting high{colors['normal']}")
        else:
            print(f"{colors['green']}✅ Context usage is healthy{colors['normal']}")
    
    # Recent usage
    recent = token_tracker.get_recent_usage(5)
    if recent:
        print(f"\n{colors['bold']}Recent Messages:{colors['normal']}")
        for log in recent[-5:]:
            if log['project'] == current_project:
                timestamp = log['timestamp'][:19].replace('T', ' ')
                print(f"  {timestamp}: {log['total_tokens']} tokens (${log['total_cost']:.6f})")
    
    # Overall stats
    agg_stats = token_tracker.get_aggregated_stats()
    print(f"\n{colors['bold']}Overall Statistics:{colors['normal']}")
    print(f"Total messages: {agg_stats['total_messages']:,}")
    print(f"Total tokens: {agg_stats['total_input_tokens'] + agg_stats['total_output_tokens']:,}")
    print(f"Total cost: ${agg_stats['total_cost']:.6f}")

def compact_conversation():
    """Analyze and compact the current conversation."""
    
    current_project = project_manager.get_current_project()
    state = project_manager.load_project_state()
    
    if not state:
        print("❌ No conversation state available")
        return
    
    conversation_history = state.get("context", {}).get("conversation_history", [])
    
    if len(conversation_history) < CONTEXT_SETTINGS["min_messages_to_keep"] * 2:
        print("❌ Conversation too short to compact")
        return
    
    estimated_tokens = token_tracker.calculate_project_context_tokens(current_project, conversation_history)
    percentage = get_context_usage_percentage(estimated_tokens)
    colors = DISPLAY_SETTINGS["colors"]
    
    print(f"\n{colors['bold']}📦 Conversation Compaction Analysis{colors['normal']}")
    print("=" * 50)
    print(f"Current messages: {len(conversation_history)}")
    print(f"Estimated tokens: {estimated_tokens:,}")
    print(f"Context usage: {percentage:.1f}%")
    
    if not should_compact_conversation(estimated_tokens):
        print(f"\n{colors['green']}✅ Compaction not needed yet{colors['normal']}")
        print(f"Compaction recommended at {CONTEXT_SETTINGS['compaction_threshold_percent']}% usage")
        return
    
    # Calculate compaction strategy
    keep_recent_count = max(
        CONTEXT_SETTINGS["min_messages_to_keep"],
        int(len(conversation_history) * CONTEXT_SETTINGS["compaction_keep_recent_percent"] / 100)
    )
    
    messages_to_remove = len(conversation_history) - keep_recent_count
    
    print(f"\n{colors['yellow']}⚠️  Compaction recommended{colors['normal']}")
    print(f"Strategy: Keep {keep_recent_count} most recent messages")
    print(f"Will remove: {messages_to_remove} older messages")
    
    # Estimate token savings
    old_messages = conversation_history[:-keep_recent_count]
    estimated_removed_tokens = token_tracker.calculate_project_context_tokens("", old_messages)
    new_estimated_tokens = estimated_tokens - estimated_removed_tokens
    new_percentage = get_context_usage_percentage(new_estimated_tokens)
    
    print(f"\nEstimated result:")
    print(f"  Tokens after compaction: ~{new_estimated_tokens:,}")
    print(f"  New context usage: ~{new_percentage:.1f}%")
    print(f"  Token reduction: ~{estimated_removed_tokens:,}")
    
    # Ask for confirmation
    confirm = input(f"\n{colors['bold']}Proceed with compaction? (y/N): {colors['normal']}").strip().lower()
    
    if confirm == 'y':
        # Perform compaction
        new_history = conversation_history[-keep_recent_count:]
        
        # Update conversation state
        state["context"]["conversation_history"] = new_history
        state["context"]["session_info"]["total_messages"] = len(new_history)
        
        # Recalculate context length
        total_chars = sum(len(msg.get("text", "")) for msg in new_history)
        state["context"]["session_info"]["context_length"] = total_chars
        
        # Save updated state
        if project_manager.save_project_state(state):
            print(f"{colors['green']}✅ Conversation compacted successfully{colors['normal']}")
            print(f"Kept {len(new_history)} most recent messages")
        else:
            print(f"{colors['red']}❌ Failed to save compacted conversation{colors['normal']}")
    else:
        print("❌ Compaction cancelled")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)