#!/usr/bin/env python3
import sys
from pathlib import Path

# Add the agent directory to the Python path
sys.path.append(str(Path(__file__).parent / "agent"))

from organs.central.consciousness_organ import ConsciousnessOrgan
from organs.independent.communication_organ import CommunicationOrgan

def main():
    """Main entry point for the Product Owner Agent - Simple Flow"""
    
    # Get memory path
    memory_path = Path(__file__).parent / "memory"
    
    print("🧠 Brain Organs Agent")
    print("=" * 20)
    
    # Initialize organs
    consciousness = ConsciousnessOrgan(str(memory_path))
    communication = CommunicationOrgan()
    
    # Connect organs
    consciousness.set_communication_organ(communication)
    
    try:
        # Check if we have command line input
        if len(sys.argv) > 1:
            # Single message mode
            task = " ".join(sys.argv[1:])
            print(f"\n💭 Processing: {task}")
            response = communication.send_to_consciousness(consciousness, task)
            communication.display_response(response)
        else:
            # Interactive conversation mode
            communication.start_conversation_loop(consciousness)
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")

if __name__ == "__main__":
    main()