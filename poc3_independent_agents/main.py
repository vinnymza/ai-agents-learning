#!/usr/bin/env python3
"""
Requirements to User Stories Agent - Main Entry Point

This is the main entry point for the PoC3 Independent Agents system.
It initializes all components, establishes their relationships, and starts
the interactive conversation loop for transforming requirements into user stories.

The system consists of three independent components:
1. Communication: Handles user interaction and I/O
2. Consciousness: Manages shared context and makes decisions
3. UserStoryCreator: Transforms requirements into user stories

Each component has its own memory and AI connection but they coordinate
through direct method calls to achieve the overall goal.

Usage:
    python main.py
"""
import sys
import os
from pathlib import Path

# Add shared directory to path for imports
sys.path.append(str(Path(__file__).parent / "shared"))
from anthropic_client import AnthropicClient

# Import all components
sys.path.append(str(Path(__file__).parent / "components" / "communication"))
from communication import CommunicationComponent

sys.path.append(str(Path(__file__).parent / "components" / "consciousness"))
from consciousness import ConsciousnessComponent

sys.path.append(str(Path(__file__).parent / "components" / "user_story_creator"))
from user_story_creator import UserStoryCreatorComponent


class RequirementsToStoriesAgent:
    """
    Main agent that coordinates all components to transform requirements into user stories.
    
    This class serves as the entry point and coordinator for the entire system,
    initializing components and establishing their relationships.
    """
    
    def __init__(self):
        """Initialize the agent with all components and their relationships."""
        self.anthropic_client = None
        self.communication = None
        self.consciousness = None
        self.user_story_creator = None
        
        self._initialize_system()
    
    def _initialize_system(self) -> None:
        """
        Initialize all components and establish their relationships.
        
        This method creates all components and sets up the communication
        pathways between them for coordinated operation.
        """
        try:
            print("🤖 Initializing Requirements to User Stories Agent...")
            
            # 1. Initialize shared AI client
            print("   📡 Connecting to Anthropic API...")
            self.anthropic_client = AnthropicClient()
            
            # Test API connection
            if not self.anthropic_client.is_api_available():
                raise ConnectionError("Failed to connect to Anthropic API. Please check your API key.")
            
            print("   ✅ Anthropic API connection established")
            
            # 2. Initialize all components with shared AI client
            print("   🧠 Initializing components...")
            
            self.communication = CommunicationComponent(self.anthropic_client)
            print("      ✅ Communication component ready")
            
            self.consciousness = ConsciousnessComponent(self.anthropic_client)
            print("      ✅ Consciousness component ready")
            
            self.user_story_creator = UserStoryCreatorComponent(self.anthropic_client)
            print("      ✅ User Story Creator component ready")
            
            # 3. Establish component relationships
            print("   🔗 Establishing component relationships...")
            self._setup_component_relationships()
            
            print("   ✅ System initialization complete!")
            print()
            
        except Exception as e:
            print(f"❌ Failed to initialize system: {str(e)}")
            print("\nPlease ensure:")
            print("1. ANTHROPIC_API_KEY is set in your environment or .env file")
            print("2. You have internet connection for API access")
            print("3. All required dependencies are installed")
            sys.exit(1)
    
    def _setup_component_relationships(self) -> None:
        """
        Establish the relationships between components.
        
        This creates the communication pathways that allow components
        to coordinate with each other while maintaining their independence.
        """
        # Communication component relationships
        self.communication.set_consciousness_component(self.consciousness)
        
        # Consciousness component relationships
        self.consciousness.set_communication_component(self.communication)
        self.consciousness.set_user_story_creator_component(self.user_story_creator)
        
        # User Story Creator component relationships  
        self.user_story_creator.set_communication_component(self.communication)
        self.user_story_creator.set_consciousness_component(self.consciousness)
        
        print("      🔗 Communication ↔ Consciousness")
        print("      🔗 Consciousness ↔ User Story Creator")
        print("      🔗 User Story Creator ↔ Communication")
    
    def start_interactive_session(self) -> None:
        """
        Start the interactive conversation session.
        
        This method begins the main conversation loop where users can
        input requirements and see them transformed into user stories.
        """
        try:
            print("🚀 Starting interactive session...")
            print("=" * 60)
            
            # Start the conversation loop through Communication component
            self.communication.start_conversation_loop()
            
        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted by user. Goodbye!")
        except Exception as e:
            print(f"\n❌ Session error: {str(e)}")
        finally:
            self._cleanup_session()
    
    def clear_all_memories(self) -> None:
        """
        Clear all component memories for a fresh start.
        
        This method clears the memory files of all components,
        useful for testing or starting completely fresh projects.
        """
        try:
            print("🧹 Clearing all component memories...")
            
            # Clear each component's memory
            if self.communication:
                self.communication.clear_conversation()
                print("   ✅ Communication memory cleared")
            
            if self.consciousness:
                self.consciousness.clear_context()
                print("   ✅ Consciousness memory cleared")
            
            if self.user_story_creator:
                self.user_story_creator.clear_all_stories()
                print("   ✅ User Story Creator memory cleared")
            
            print("   🎯 All memories cleared successfully!")
            print()
            
        except Exception as e:
            print(f"❌ Error clearing memories: {str(e)}")
    
    def _cleanup_session(self) -> None:
        """
        Clean up resources and display session summary.
        """
        try:
            print("\n📊 Session Summary:")
            print("-" * 40)
            
            # Get conversation statistics
            if self.communication:
                stats = self.communication.get_conversation_stats()
                print(f"Session ID: {stats.get('session_id', 'Unknown')}")
                print(f"Total Messages: {stats.get('total_messages', 0)}")
                print(f"User Messages: {stats.get('user_messages', 0)}")
                print(f"Agent Messages: {stats.get('agent_messages', 0)}")
            
            # Get project status
            if self.consciousness:
                project_status = self.consciousness.get_project_status()
                print(f"Active Requirements: {project_status.get('active_requirements', 0)}")
            
            # Get user story statistics
            if self.user_story_creator:
                story_stats = self.user_story_creator.get_story_statistics()
                print(f"User Stories Created: {story_stats.get('total_stories', 0)}")
                
                # Show stories by status
                by_status = story_stats.get('stories_by_status', {})
                if by_status:
                    print("Stories by Status:")
                    for status, count in by_status.items():
                        if count > 0:
                            print(f"  {status.title()}: {count}")
            
            print("-" * 40)
            print("Thank you for using the Requirements to User Stories Agent! 🎯")
            
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")
    
    def run_demo_mode(self) -> None:
        """
        Run a demonstration of the system with sample requirements.
        
        This method showcases the system's capabilities by processing
        predefined requirements and showing the generated user stories.
        """
        print("🎬 Running Demo Mode...")
        print("=" * 60)
        
        # Set demo project context
        self.consciousness.set_project_info(
            name="E-commerce Platform", 
            description="Online shopping platform with user management and product catalog"
        )
        
        # Demo requirements
        demo_requirements = [
            "Users need to be able to register and login to the platform",
            "The system should allow users to browse and search for products",
            "Users want to add products to a shopping cart and checkout",
            "Administrators need to manage product inventory and orders"
        ]
        
        print("\n📝 Processing demo requirements:")
        for i, requirement in enumerate(demo_requirements, 1):
            print(f"\n{i}. Processing: '{requirement}'")
            
            # Simulate user input through the system
            self.communication.process_user_input(requirement)
            
            print("   ✅ Processed")
        
        print("\n🎯 Demo completed! User stories have been generated.")
        
        # Show created user stories
        if self.user_story_creator:
            print("\n📋 Generated User Stories:")
            self.user_story_creator.list_user_stories()


def main():
    """
    Main entry point for the application.
    
    Handles command line arguments and starts the appropriate mode.
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Requirements to User Stories Agent - Transform requirements into professional user stories"
    )
    parser.add_argument(
        "--demo", 
        action="store_true", 
        help="Run demonstration mode with sample requirements"
    )
    parser.add_argument(
        "--clear", 
        action="store_true", 
        help="Clear all component memories and exit"
    )
    parser.add_argument(
        "--version", 
        action="version", 
        version="Requirements to User Stories Agent v1.0.0 (PoC3)"
    )
    
    args = parser.parse_args()
    
    # Initialize the agent system
    agent = RequirementsToStoriesAgent()
    
    if args.clear:
        # Clear all memories and exit
        agent.clear_all_memories()
    elif args.demo:
        # Run demo mode
        agent.run_demo_mode()
    else:
        # Run interactive mode
        agent.start_interactive_session()


if __name__ == "__main__":
    main()