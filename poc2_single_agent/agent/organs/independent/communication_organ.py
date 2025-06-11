#!/usr/bin/env python3
import sys
from typing import Optional

class CommunicationOrgan:
    """
    Independent Communication Organ - Handles external I/O
    
    Responsible for:
    - Reading user input from console
    - Sending data to consciousness organ
    - Future: web interfaces, APIs, etc.
    """
    
    def __init__(self):
        pass
    
    def get_user_input(self, prompt: str = "Enter your message: ") -> Optional[str]:
        """
        Get input from user via console
        """
        try:
            user_input = input(prompt).strip()
            return user_input if user_input else None
        except (KeyboardInterrupt, EOFError):
            return None
    
    def send_to_consciousness(self, consciousness_organ, message: str):
        """
        Send message to consciousness organ
        """
        # Send to consciousness
        return consciousness_organ.process_input(message)
    
    
    def display_response(self, response: dict):
        """
        Display response to user
        """
        if response.get("status") == "error":
            print(f"Error: {response.get('message', 'Unknown error')}")
        else:
            print(f"✓ {response.get('message', 'Processed')}")
    
    def display_message(self, message: str, memory_organ=None):
        """
        Display a message to user and store it in memory if provided
        """
        print(f"\nAgente: {message}")
        if memory_organ:
            memory_organ.store("session", {"speaker": "agent", "message": message})
    
    def ask_user_question(self, question: str) -> str:
        """
        Ask user a question and get their response
        """
        print(f"\nAgente: {question}")
        response = self.get_user_input("Your answer: ")
        return response if response else ""

    
    def start_conversation_loop(self, consciousness_organ):
        """
        Start interactive conversation loop
        """
        print("Type 'exit' to quit.")
        
        while True:
            user_input = self.get_user_input("\n> ")
            
            if user_input is None:
                break
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("Goodbye!")
                break
            
            self.send_to_consciousness(consciousness_organ, user_input)