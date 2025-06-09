#!/usr/bin/env python3
import json
import os
import sys
import time
import anthropic
from dotenv import load_dotenv
from pathlib import Path

# Add parent directory to path to import shared utilities
sys.path.append(str(Path(__file__).parent.parent))
from shared.agent_utils import AgentCommunication

class ProductOwnerAgent:
    """Agent that takes a task and generates requirements"""
    
    def __init__(self, json_path):
        self.agent_name = "product_owner"
        self.comm = AgentCommunication(json_path, self.agent_name)
        self.load_dotenv()
    
    def load_dotenv(self):
        """Load environment variables from .env file"""
        load_dotenv()
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("No se encontró ANTHROPIC_API_KEY en el archivo .env")
        
        # Initialize Anthropic client
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def interrogate_client_and_analyze(self, task, collaboration_mode=True):
        """Interrogate client to clarify requirements and generate specifications"""
        # Update status to working
        self.comm.update_status("working", "Interrogating client and analyzing requirements")
        
        # Check if other agents have sent any messages or constraints
        messages = self.comm.get_messages()
        agent_feedback = ""
        
        if messages and collaboration_mode:
            agent_feedback = "Feedback from other agents:\n"
            for msg_key, msg_data in messages.items():
                agent_feedback += f"- {msg_data['from']}: {msg_data['content']}\n"
        
        # Create prompt for Claude - focus on interrogation and analysis
        system_prompt = """You are a Product Owner AI agent. Your job is to:
1. Ask intelligent clarifying questions about the task
2. Analyze business context and user needs
3. Generate executable specifications (not user stories)
4. Question assumptions and identify missing information

You work with other AI agents, so be specific and technical.
Don't write user stories - write specifications that developers can implement."""
        
        user_prompt = f"""Client Task: {task}
Stack: NestJS + NextJS + PostgreSQL

{agent_feedback}

As a Product Owner AI agent, you need to:

1. QUESTIONS: List 5-7 intelligent questions you would ask the client to clarify this task
2. ASSUMPTIONS: What assumptions are you making about this feature?
3. SPECIFICATIONS: Generate 4-6 executable specifications (not user stories)
4. BUSINESS_CONTEXT: What business value does this provide?

Format your response as JSON:
{{
  "questions": ["Question 1?", "Question 2?"],
  "assumptions": ["Assumption 1", "Assumption 2"],
  "specifications": ["Spec 1", "Spec 2"],
  "business_context": "Business value explanation"
}}
"""

        # Make request to Claude
        message = self.client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1500,
            temperature=0.3,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        
        # Extract and parse the response
        response = message.content[0].text.strip()
        
        # Clean up JSON response
        if response.startswith("```json"):
            response = response[7:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()
        
        try:
            parsed_response = json.loads(response)
            return parsed_response
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "questions": ["What is the expected number of concurrent users?", "What are the main user roles?"],
                "assumptions": ["Standard web application", "Basic CRUD operations needed"],
                "specifications": [f"Implement {task} with basic functionality"],
                "business_context": f"This feature will improve user productivity for {task}"
            }
    
    def generate_fallback_requirements(self, task):
        """Generate fallback requirements if API call fails"""
        if "dashboard" in task.lower() and "analytics" in task.lower():
            return [
                "El dashboard debe mostrar métricas clave de conversión en tiempo real",
                "Los datos deben poder filtrarse por rango de fechas y segmentos de usuarios",
                "Debe incluir gráficos de tendencias para los últimos 30 días",
                "Los administradores deben poder exportar reportes en formato CSV y PDF"
            ]
        elif "notificaciones" in task.lower() or "notifications" in task.lower():
            return [
                "Los usuarios deben recibir notificaciones en tiempo real sin refrescar la página",
                "Las notificaciones deben ser persistentes y marcables como leídas",
                "Los usuarios deben poder configurar qué notificaciones desean recibir",
                "El sistema debe soportar notificaciones push para usuarios móviles"
            ]
        elif "login" in task.lower() and "google" in task.lower() or "autenticación" in task.lower() or "authentication" in task.lower():
            return [
                "El login con Google debe integrarse en la página principal",
                "Debe seguir el diseño de UI existente",
                "Necesitamos tracking de conversiones para cada login exitoso",
                "El proceso debe ser rápido y no requerir validaciones adicionales"
            ]
        else:
            # Generic requirements for any other task
            return [
                f"El sistema de {task} debe ser intuitivo y fácil de usar",
                f"La implementación debe seguir los estándares de UI/UX existentes",
                f"Debe ser compatible con dispositivos móviles y desktop",
                f"El rendimiento no debe verse afectado por la nueva funcionalidad"
            ]
    
    def run(self):
        """Main agent execution loop"""
        print("Product Owner AI Agent: Starting")
        
        # Read the shared JSON data
        data = self.comm.read_json()
        task = data.get('task', 'Implementar funcionalidad')
        
        # Update status to initialize
        self.comm.update_status("initializing")
        
        try:
            # Interrogate client and analyze requirements
            print(f"Product Owner AI: Interrogating client about: {task}")
            analysis = self.interrogate_client_and_analyze(task)
            api_used = True
        except Exception as e:
            print(f"Error during client interrogation: {e}")
            print("Using fallback analysis...")
            analysis = {
                "questions": ["What is the expected number of users?", "What are the main features needed?"],
                "assumptions": ["Standard web application", "Basic functionality required"],
                "specifications": [f"Implement {task} with standard features"],
                "business_context": f"This will improve workflow for {task}"
            }
            api_used = False
        
        # Update the shared data with the analysis
        data = self.comm.read_json()  # Read again to get any changes
        data['product_owner_analysis'] = analysis
        
        # Add reasoning about the analysis approach
        data['product_owner_reasoning'] = {
            "approach": "AI-driven client interrogation" if api_used else "Fallback analysis",
            "agent_type": "Product Owner AI Agent",
            "focus": [
                "Asked clarifying questions to understand requirements",
                "Identified assumptions and business context",
                "Generated executable specifications for development",
                "Prepared foundation for technical architecture discussion"
            ]
        }
        
        # Update the JSON file
        self.comm.write_json(data)
        
        # Send questions to Staff Engineer for technical validation
        questions_text = "\n".join([f"- {q}" for q in analysis['questions']])
        self.comm.send_message_to_agent(
            "staff_engineer", 
            "client_interrogation",
            f"I've interrogated the client about '{task}'. Key questions that need technical input:\n{questions_text}\n\nPlease review my specifications and add technical depth."
        )
        
        # Update status to completed
        self.comm.update_status("completed", "Client interrogation and analysis completed")
        
        # Print what was done
        print(f"Product Owner AI: Completed analysis for: {task}")
        print(f"\nQuestions for client:")
        for question in analysis['questions']:
            print(f"  ? {question}")
        
        print(f"\nKey assumptions:")
        for assumption in analysis['assumptions']:
            print(f"  → {assumption}")
        
        print(f"\nExecutable specifications:")
        for spec in analysis['specifications']:
            print(f"  ✓ {spec}")
        
        print(f"\nBusiness context: {analysis['business_context']}")
        
        # Check if other agents have started their work
        other_statuses = self.comm.check_other_agents_status()
        print(f"Other agents status: {other_statuses}")
        
        # Signal completion
        print("Product Owner AI Agent: Analysis completed, awaiting Staff Engineer technical review")
        return analysis

def main():
    # Get JSON path from command line arguments or use default
    if len(sys.argv) > 1:
        json_path = sys.argv[1]
    else:
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'shared', 'communication.json')
    
    # Create and run the Product Owner agent
    agent = ProductOwnerAgent(json_path)
    agent.run()

if __name__ == "__main__":
    main()