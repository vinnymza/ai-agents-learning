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

class StaffEngineerAgent:
    """AI Agent that questions Product Owner specs and defines technical architecture"""
    
    def __init__(self, json_path):
        self.agent_name = "staff_engineer"
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
    
    def wait_for_po_analysis(self):
        """Wait for the Product Owner to complete their analysis"""
        def analysis_ready():
            data = self.comm.read_json()
            product_owner_status = data["agents"]["product_owner"]["status"]
            return (product_owner_status == "completed" and 
                    "product_owner_analysis" in data)
        
        # Wait until analysis is ready
        print("Staff Engineer AI: Waiting for Product Owner analysis...")
        if not self.comm.wait_with_backoff(analysis_ready):
            raise TimeoutError("Timeout waiting for Product Owner analysis")
        
        # Check if there are any messages for this agent
        messages = self.comm.get_messages()
        if messages:
            print("Staff Engineer AI: Received messages:")
            for key, msg in messages.items():
                print(f"- From {msg['from']}: {msg['content']}")
    
    def question_and_architect(self, task, po_analysis, stack="NestJS + NextJS + PostgreSQL"):
        """Question PO specifications and define technical architecture"""
        # Update status to working
        self.comm.update_status("working", "Questioning specifications and defining architecture")
        
        # Check for messages from other agents
        messages = self.comm.get_messages()
        context_from_agents = ""
        
        if messages:
            context_from_agents = "Messages from other agents:\n"
            for msg_key, msg_data in messages.items():
                context_from_agents += f"- {msg_data['from']}: {msg_data['content']}\n"
        
        # Create prompt for Claude - focus on questioning and architecture
        system_prompt = """You are a Staff Engineer AI agent. Your job is to:
1. Question the Product Owner's specifications from a technical perspective
2. Identify missing technical requirements and edge cases
3. Define system architecture and technology choices
4. Estimate complexity and technical risks
5. Challenge assumptions with engineering expertise

You work with other AI agents. Be direct and technical.
Focus on architecture, scalability, and implementation details."""
        
        # Extract data from PO analysis
        questions = po_analysis.get('questions', [])
        assumptions = po_analysis.get('assumptions', [])
        specifications = po_analysis.get('specifications', [])
        business_context = po_analysis.get('business_context', '')
        
        questions_text = "\n".join([f"- {q}" for q in questions])
        assumptions_text = "\n".join([f"- {a}" for a in assumptions])
        specs_text = "\n".join([f"- {s}" for s in specifications])
        
        user_prompt = f"""Task: {task}
Stack: {stack}

{context_from_agents}

Product Owner Analysis:
Questions: 
{questions_text}

Assumptions:
{assumptions_text}

Specifications:
{specs_text}

Business Context: {business_context}

As a Staff Engineer AI, you need to:

1. TECHNICAL_QUESTIONS: Ask 5-7 technical questions about the PO's specifications
2. ARCHITECTURE: Define the system architecture (components, data flow, APIs)
3. TECHNOLOGY_DECISIONS: Justify technology choices and alternatives
4. COMPLEXITY_ANALYSIS: Identify technical complexity and risks
5. IMPLEMENTATION_PHASES: Break down into technical implementation phases
6. SCALABILITY_CONCERNS: Address performance and scaling considerations

Format as JSON:
{{
  "technical_questions": ["Technical question 1?", "Technical question 2?"],
  "architecture": {{
    "components": ["Component 1", "Component 2"],
    "data_flow": "Description of data flow",
    "apis": ["API 1", "API 2"]
  }},
  "technology_decisions": ["Decision 1: Justification", "Decision 2: Justification"],
  "complexity_analysis": {{
    "high_risk": ["Risk 1", "Risk 2"],
    "estimated_effort": "X weeks/months",
    "technical_debt": ["Debt 1", "Debt 2"]
  }},
  "implementation_phases": ["Phase 1: Description", "Phase 2: Description"],
  "scalability_concerns": ["Concern 1", "Concern 2"]
}}
"""
        
        # Make request to Claude
        message = self.client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2500,
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
                "technical_questions": ["What is the expected data volume?", "How many concurrent connections?"],
                "architecture": {
                    "components": ["Backend API", "Frontend App", "Database"],
                    "data_flow": "Standard client-server architecture",
                    "apis": ["REST API endpoints"]
                },
                "technology_decisions": [f"Using {stack} as specified"],
                "complexity_analysis": {
                    "high_risk": ["Integration complexity"],
                    "estimated_effort": "2-4 weeks",
                    "technical_debt": ["Potential performance bottlenecks"]
                },
                "implementation_phases": ["Phase 1: Backend setup", "Phase 2: Frontend implementation"],
                "scalability_concerns": ["Database performance under load"]
            }
    
    def generate_fallback_solution(self, task):
        """Generate a fallback solution if API call fails"""
        if "dashboard" in task.lower() and "analytics" in task.lower():
            return {
                "implementation_plan": [
                    "Develop NestJS API endpoints for analytics data",
                    "Create Chart.js components in NextJS",
                    "Implement time filters and data segmentation",
                    "Configure caching to improve performance of heavy queries"
                ],
                "estimated_time": "5 days",
                "dependencies": ["nestjs/swagger", "chart.js", "react-chartjs-2", "next-auth"]
            }
        elif "notificaciones" in task.lower() or "notifications" in task.lower():
            return {
                "implementation_plan": [
                    "Implement WebSockets service with Socket.io",
                    "Create notifications microservice in NestJS",
                    "Develop notification center component in NextJS",
                    "Integrate Firebase Cloud Messaging for push notifications"
                ],
                "estimated_time": "4 days",
                "dependencies": ["socket.io", "nestjs/websockets", "@nestjs/microservices", "firebase-admin"]
            }
        elif "chat" in task.lower() or "mensajes" in task.lower() or "messages" in task.lower():
            return {
                "implementation_plan": [
                    "Implement bidirectional real-time connections with Socket.io",
                    "Develop chat microservice in NestJS",
                    "Create UI components for chat rooms and private messages",
                    "Implement message persistence system in PostgreSQL",
                    "Integrate storage service for attachments"
                ],
                "estimated_time": "6 days",
                "dependencies": ["socket.io", "nestjs/websockets", "@nestjs/platform-socket.io", "aws-sdk", "rxjs"]
            }
        else:
            # Generic solution for other tasks
            return {
                "implementation_plan": [
                    f"Analyze technical requirements for {task}",
                    f"Develop necessary components in NextJS",
                    f"Implement backend services in NestJS",
                    f"Write unit and integration tests"
                ],
                "estimated_time": "5 days",
                "dependencies": ["nestjs/core", "next", "jest", "supertest"]
            }
    
    def run(self):
        """Main agent execution loop"""
        print("Staff Engineer AI Agent: Starting")
        
        # Update status to initializing
        self.comm.update_status("initializing")
        
        try:
            # Wait for the Product Owner to complete analysis
            self.wait_for_po_analysis()
            
            # Read the shared JSON data
            data = self.comm.read_json()
            task = data.get('task', 'Implementar funcionalidad')
            po_analysis = data.get('product_owner_analysis', {})
            
            print("Staff Engineer AI: Received Product Owner analysis:")
            print(f"Questions: {len(po_analysis.get('questions', []))} questions identified")
            print(f"Specifications: {len(po_analysis.get('specifications', []))} specs provided")
            print(f"Assumptions: {len(po_analysis.get('assumptions', []))} assumptions made")
            
            try:
                # Question PO specs and define architecture
                print(f"\nStaff Engineer AI: Questioning specifications and defining architecture for: {task}")
                technical_analysis = self.question_and_architect(task, po_analysis)
                api_used = True
            except Exception as e:
                print(f"\nStaff Engineer AI: Error during technical analysis: {e}")
                print("Using fallback technical analysis...")
                technical_analysis = {
                    "technical_questions": ["What is the expected data volume?", "How many concurrent users?"],
                    "architecture": {
                        "components": ["Backend API", "Frontend App", "Database"],
                        "data_flow": "Standard client-server architecture",
                        "apis": ["REST API endpoints"]
                    },
                    "technology_decisions": ["Using NestJS + NextJS + PostgreSQL as specified"],
                    "complexity_analysis": {
                        "high_risk": ["Integration complexity"],
                        "estimated_effort": "2-4 weeks",
                        "technical_debt": ["Potential performance bottlenecks"]
                    },
                    "implementation_phases": ["Phase 1: Backend setup", "Phase 2: Frontend implementation"],
                    "scalability_concerns": ["Database performance under load"]
                }
                api_used = False
            
            # Update shared data with the technical analysis
            data = self.comm.read_json()  # Read again to get any changes
            data['staff_engineer_analysis'] = technical_analysis
            data['staff_engineer_reasoning'] = {
                "approach": "AI-driven architecture analysis" if api_used else "Fallback technical analysis",
                "agent_type": "Staff Engineer AI Agent",
                "focus": [
                    "Questioned Product Owner specifications from technical perspective",
                    "Defined system architecture and component breakdown",
                    "Identified technical risks and complexity factors",
                    "Prepared detailed implementation phases"
                ]
            }
            
            # Write the updated JSON
            self.comm.write_json(data)
            
            # Send technical questions back to Product Owner and notify Engineering Manager
            tech_questions_text = "\n".join([f"- {q}" for q in technical_analysis['technical_questions']])
            self.comm.send_message_to_agent(
                "product_owner",
                "technical_questions",
                f"I've reviewed your specifications. I need clarification on these technical aspects:\n{tech_questions_text}"
            )
            
            self.comm.send_message_to_agent(
                "engineering_manager",
                "architecture_ready",
                f"I've defined the technical architecture for '{task}' with {len(technical_analysis['implementation_phases'])} implementation phases. Ready for coordination."
            )
            
            # Update status to completed
            self.comm.update_status("completed", "Technical architecture and analysis completed")
            
            # Print what was done
            print(f"\nStaff Engineer AI: Completed technical analysis for: {task}")
            print(f"\nTechnical questions raised:")
            for question in technical_analysis['technical_questions']:
                print(f"  ? {question}")
            
            print(f"\nArchitecture components:")
            for component in technical_analysis['architecture']['components']:
                print(f"  ⚙️ {component}")
            
            print(f"\nImplementation phases:")
            for i, phase in enumerate(technical_analysis['implementation_phases'], 1):
                print(f"  {i}. {phase}")
            
            print(f"\nComplexity estimate: {technical_analysis['complexity_analysis']['estimated_effort']}")
            
            # Check other agents' status
            other_statuses = self.comm.check_other_agents_status()
            print(f"Other agents status: {other_statuses}")
            
            # Signal completion
            print("Staff Engineer AI Agent: Technical analysis completed, awaiting Engineering Manager coordination")
            return technical_analysis
            
        except Exception as e:
            print(f"Staff Engineer AI Agent Error: {e}")
            self.comm.update_status("error", str(e))
            raise

def main():
    # Get JSON path from command line arguments or use default
    if len(sys.argv) > 1:
        json_path = sys.argv[1]
    else:
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'shared', 'communication.json')
    
    # Create and run the Staff Engineer agent
    agent = StaffEngineerAgent(json_path)
    agent.run()

if __name__ == "__main__":
    main()