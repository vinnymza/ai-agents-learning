#!/usr/bin/env python3
import sys
from pathlib import Path

# Add organs to path
sys.path.append(str(Path(__file__).parent.parent))
from core.memory_organ import MemoryOrgan
from core.reasoning_organ import ReasoningOrgan

class ConsciousnessOrgan:
    """
    The Consciousness Organ - Simple mediator between organs
    Routes requests and maintains context, no business logic
    """
    
    def __init__(self, memory_path: str):
        self.memory_path = Path(memory_path)
        self.memory_organ = MemoryOrgan(memory_path)
        self.reasoning_organ = ReasoningOrgan()
        self.communication_organ = None  # Will be set by main.py
    
    def process_input(self, user_input: str):
        """
        Simple mediator: route user input through organs and coordinate responses
        """
        # 1. Store user input in memory
        self.memory_organ.store("session", user_input)
        
        # 2. Get context for reasoning
        context = self._get_context_for_reasoning()
        
        # 3. Get reasoning result
        reasoning_result = self.reasoning_organ.update_requirements(**context)
        
        # 4. Route result to appropriate handler
        return self._handle_reasoning_result(reasoning_result)
    
    def _get_context_for_reasoning(self):
        """Get all necessary context for reasoning organ"""
        return {
            "session_memory": self.memory_organ.retrieve("session"),
            "initial_memory": self.memory_organ.retrieve("initial"),
            "current_requirements": self.memory_organ.retrieve("requirements")
        }
    
    def _handle_reasoning_result(self, reasoning_result):
        """Route reasoning result to appropriate response"""
        if not reasoning_result["success"]:
            return self._handle_error(reasoning_result)
        
        if reasoning_result.get("conversation_request"):
            return self._handle_conversation_request(reasoning_result)
        
        if reasoning_result.get("new_project"):
            return self._handle_new_project(reasoning_result)
        
        return self._handle_requirements_update(reasoning_result)
    
    def _handle_conversation_request(self, reasoning_result):
        """Handle user request for more questions"""
        context = self._get_context_for_reasoning()
        new_questions = self.reasoning_organ.generate_new_questions(
            context["current_requirements"], 
            context["session_memory"], 
            context["initial_memory"]
        )
        
        if self.communication_organ and new_questions:
            questions_text = "\n".join([f"{i}. {q}" for i, q in enumerate(new_questions, 1)])
            response = f"Here are some additional questions about your project:\n{questions_text}"
            self.communication_organ.display_message(response, self.memory_organ)
        
        return {"status": "processed", "message": "Generated new questions"}
    
    def _handle_new_project(self, reasoning_result):
        """Handle new project detection"""
        if not self.communication_organ:
            return {"status": "processed", "message": "New project detected"}
        
        # Ask user about project switch
        current_reqs = self.memory_organ.retrieve("requirements")
        current_project = current_reqs.get("raw_requirements", "") if current_reqs else ""
        
        if current_project.strip():
            project_desc = current_project[:50] + "..." if len(current_project) > 50 else current_project
            question = f"I detected you're talking about a different project. Do you want to start a new project or continue with the current one ({project_desc})? (new/continue)"
        else:
            question = "I detected you're talking about a different project. Do you want to start a new project or continue with the current one? (new/continue)"
        
        user_response = self.communication_organ.ask_user_question(question)
        
        # Store conversation
        self.memory_organ.store("session", {"speaker": "agent", "message": question})
        self.memory_organ.store("session", {"speaker": "user", "message": user_response})
        
        if user_response.lower().startswith('new'):
            self.memory_organ.store("requirements", {})
            self.communication_organ.display_message("Starting fresh with a new project! Please tell me about your requirements.")
            return {"status": "processed", "message": "New project started"}
        else:
            self.communication_organ.display_message("Continuing with current project.")
            return {"status": "processed", "message": "Continuing current project"}
    
    def _handle_requirements_update(self, reasoning_result):
        """Handle normal requirements update"""
        # Store updated requirements
        self.memory_organ.store("requirements", reasoning_result["data"])
        
        # Show pending questions if any
        self._show_pending_questions(reasoning_result["data"])
        
        # Display explanation
        if self.communication_organ and "explanation" in reasoning_result:
            self.communication_organ.display_message(reasoning_result["explanation"], self.memory_organ)
        
        return {"status": "processed", "message": "Requirements updated"}
    
    def _show_pending_questions(self, requirements_data):
        """Show pending questions to user"""
        if not self.communication_organ:
            return
        
        pending_questions = requirements_data.get("functional_analysis", {}).get("pending_questions", [])
        if pending_questions:
            self.communication_organ.display_message("I have some questions for you:")
            for i, question in enumerate(pending_questions, 1):
                self.communication_organ.display_message(f"{i}. {question}")
    
    def _handle_error(self, reasoning_result):
        """Handle reasoning errors"""
        error_response = f"Error: {reasoning_result['message']}"
        if self.communication_organ:
            self.communication_organ.display_message(error_response, self.memory_organ)
        
        return {"status": "error", "message": reasoning_result["message"]}
    
    def set_communication_organ(self, communication_organ):
        """Set the communication organ for displaying messages"""
        self.communication_organ = communication_organ