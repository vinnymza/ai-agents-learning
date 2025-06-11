#!/usr/bin/env python3
import os
import anthropic
from dotenv import load_dotenv
from pathlib import Path
from typing import Dict, Any

class ReasoningOrgan:
    """
    Independent Reasoning Organ - Handles AI processing and analysis
    
    Responsible for:
    - Processing data through Anthropic API
    - Analyzing conversations and extracting insights
    - Updating requirements based on new inputs
    """
    
    def __init__(self):
        self.load_anthropic_client()
    
    def load_anthropic_client(self):
        """Load Anthropic API client"""
        # Load from root project directory
        root_env_path = Path(__file__).parent.parent.parent.parent.parent / '.env'
        load_dotenv(root_env_path)
        
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def update_requirements(self, session_memory: Dict, initial_memory: str, current_requirements) -> Dict:
        """
        Update requirements based on session conversation, using initial wisdom and current requirements
        """
        try:
            # Handle empty or missing current requirements
            if not current_requirements or current_requirements == {} or not current_requirements.get("raw_requirements"):
                current_requirements = {
                    "raw_requirements": "",
                    "functional_analysis": {
                        "main_problem": "",
                        "identified_users": [],
                        "main_use_cases": [],
                        "assumptions": [],
                        "risks": [],
                        "pending_questions": []
                    },
                    "identified_epics": []
                }
            
            # Create prompt for updating requirements
            system_prompt = f"""You are a reasoning organ that updates project requirements based on conversation.

                INITIAL WISDOM:
                {initial_memory}

                Your task: Analyze the conversation and determine if the latest user input contains NEW requirements information.

                IMPORTANT: 
                1. If the user says things like greetings, random words, or unrelated comments, respond with "NO_UPDATE"
                2. If the user input contains requirements for a COMPLETELY DIFFERENT PROJECT than what's currently in requirements, respond with "NEW_PROJECT"
                3. If the user input contains updates/additions to the EXISTING project requirements, update them normally
            """
            
            user_prompt = f"""
                CURRENT REQUIREMENTS:
                {current_requirements}

                CONVERSATION HISTORY:
                {session_memory}

                Based on this conversation, determine if the latest user input contains new requirements information.

                Look at the CURRENT REQUIREMENTS and compare with the latest user input:

                IMPORTANT RULES:
                1. If user says greetings/small talk like "hola", "hello", "hi", "how are you" → Always NO_UPDATE
                2. If user explicitly asks for more questions like "ask me other questions", "more questions", "different questions" → CONVERSATION_REQUEST  
                3. If user provides SPECIFIC DETAILS about the current project (like target users, features, constraints, company size) → Normal update (NOT conversation request)
                4. If current requirements are EMPTY (no raw_requirements or empty string) and user provides project requirements → Update the empty project (normal update)
                5. If current requirements have a CLEAR PROJECT (like "task management app") and user describes a COMPLETELY DIFFERENT project type (like "mobile fitness app") → NEW_PROJECT
                6. If user adds details to the SAME project type → Normal update

                If the latest user input contains NO new requirements information (like greetings, random words, unrelated comments), respond with exactly:
                NO_UPDATE

                If the latest user input describes a COMPLETELY DIFFERENT PROJECT than the current requirements, respond with exactly:
                NEW_PROJECT

                If the user explicitly asks for more questions about the current project (like "ask me other questions", "more questions", "different questions"), respond with exactly:
                CONVERSATION_REQUEST

                EXAMPLES:
                - "it is a task management application for a company of 15 users" → Normal update (specific detail about current project)
                - "it should have user authentication" → Normal update (feature detail)
                - "the budget is $50,000" → Normal update (constraint detail)
                - "please ask me other questions" → CONVERSATION_REQUEST
                - "hola" → NO_UPDATE
                - "I want to build a fitness tracking app" → NEW_PROJECT (if current is task management)

                If the latest user input DOES contain new requirements information for the EXISTING project, respond with:

                EXPLANATION:
                [Write a paragraph explaining what changed in the requirements and why]

                UPDATED_REQUIREMENTS:
                {{
                "raw_requirements": "...",
                "functional_analysis": {{
                    "main_problem": "...",
                    "identified_users": [...],
                    "main_use_cases": [...],
                    "assumptions": [...],
                    "risks": [...],
                    "pending_questions": [...]
                }},
                "identified_epics": [...]
                }}
            """
            
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=2000,
                temperature=0.3,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            response = message.content[0].text.strip()
            
            # Check if AI determined no update is needed
            if "NO_UPDATE" in response:
                return {
                    "success": True,
                    "data": current_requirements,  # Return unchanged requirements
                    "explanation": "No requirements update needed - user input was not related to project requirements.",
                    "message": "No requirements update needed"
                }
            
            # Check if AI detected a new project
            if "NEW_PROJECT" in response:
                return {
                    "success": True,
                    "data": current_requirements,  # Keep current requirements for now
                    "explanation": "NEW_PROJECT_DETECTED",
                    "message": "New project detected",
                    "new_project": True
                }
            
            # Check if user wants to have a conversation about current project
            if "CONVERSATION_REQUEST" in response:
                return {
                    "success": True,
                    "data": current_requirements,  # Keep current requirements unchanged
                    "explanation": "CONVERSATION_REQUEST",
                    "message": "User wants to discuss current project",
                    "conversation_request": True
                }
            
            # Extract explanation and JSON from response
            import json
            
            # Find explanation
            explanation_start = response.find("EXPLANATION:")
            requirements_start = response.find("UPDATED_REQUIREMENTS:")
            
            if explanation_start != -1 and requirements_start != -1:
                explanation = response[explanation_start + 12:requirements_start].strip()
                
                # Extract JSON from requirements section
                json_start = response.find('{', requirements_start)
                json_end = response.rfind('}') + 1
                
                if json_start != -1 and json_end != 0:
                    json_str = response[json_start:json_end]
                    updated_requirements = json.loads(json_str)
                else:
                    raise ValueError("No valid JSON found in requirements section")
            else:
                raise ValueError("Could not find EXPLANATION or UPDATED_REQUIREMENTS sections")
            
            return {
                "success": True,
                "data": updated_requirements,
                "explanation": explanation,
                "message": "Requirements updated successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to update requirements: {e}"
            }
    
    def generate_new_questions(self, current_requirements, session_memory, initial_memory):
        """Generate new questions for the current project"""
        try:
            system_prompt = f"""You are a reasoning organ that generates insightful questions about a project.

INITIAL WISDOM:
{initial_memory}

Generate 3-5 NEW questions that would help better understand the project requirements. 
Avoid repeating questions that are already in pending_questions.
Focus on areas that need more clarity for a Product Owner."""

            user_prompt = f"""
PROJECT REQUIREMENTS:
{current_requirements}

CONVERSATION HISTORY:
{session_memory}

Generate 3-5 new insightful questions about this project that would help a Product Owner better understand the requirements. 
Avoid repeating the existing pending questions.

Return only the questions, one per line, numbered:
1. Question here
2. Question here
etc.
"""

            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                temperature=0.7,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            response = message.content[0].text.strip()
            
            # Extract questions from numbered list
            questions = []
            for line in response.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('•') or line.startswith('-')):
                    # Remove numbering and clean up
                    question = line.split('.', 1)[-1].strip()
                    if question:
                        questions.append(question)
            
            return questions
            
        except Exception as e:
            return [f"What aspects of this project would you like to discuss further?"]