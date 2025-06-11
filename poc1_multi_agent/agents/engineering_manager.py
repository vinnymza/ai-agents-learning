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

class EngineeringManagerAgent:
    """AI Agent that facilitates collaboration, coordinates execution, and generates Claude Code prompts"""
    
    def __init__(self, json_path):
        self.agent_name = "engineering_manager"
        self.comm = AgentCommunication(json_path, self.agent_name)
        self.load_dotenv()
    
    def load_dotenv(self):
        """Load environment variables from .env file"""
        # Load from root project directory
        root_env_path = Path(__file__).parent.parent.parent / '.env'
        load_dotenv(root_env_path)
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("No se encontró ANTHROPIC_API_KEY en el archivo .env")
        
        # Initialize Anthropic client
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def wait_for_analyses(self):
        """Wait for both Product Owner and Staff Engineer to complete their analyses"""
        def analyses_ready():
            data = self.comm.read_json()
            po_status = data["agents"]["product_owner"]["status"]
            se_status = data["agents"]["staff_engineer"]["status"]
            
            return (po_status == "completed" and se_status == "completed" and
                    "product_owner_analysis" in data and
                    "staff_engineer_analysis" in data)
        
        # Wait until analyses are ready
        print("Engineering Manager AI: Waiting for Product Owner and Staff Engineer analyses...")
        if not self.comm.wait_with_backoff(analyses_ready):
            raise TimeoutError("Timeout waiting for agent analyses")
        
        # Check if there are any messages for this agent
        messages = self.comm.get_messages()
        if messages:
            print("Engineering Manager AI: Received messages:")
            for key, msg in messages.items():
                print(f"- From {msg['from']}: {msg['content']}")
    
    def coordinate_and_generate_prompts(self, task, po_analysis, se_analysis, stack="NestJS + NextJS + PostgreSQL"):
        """Facilitate collaboration between agents and generate Claude Code prompts for implementation"""
        # Update status to working
        self.comm.update_status("working", "Coordinating agents and generating implementation prompts")
        
        # Check for messages from other agents
        messages = self.comm.get_messages()
        agent_messages = ""
        
        if messages:
            agent_messages = "Messages from other agents:\n"
            for msg_key, msg_data in messages.items():
                agent_messages += f"- {msg_data['from']}: {msg_data['content']}\n"
        
        # Extract and format data from both analyses
        po_specs = "\n".join([f"- {spec}" for spec in po_analysis.get('specifications', [])])
        po_questions = "\n".join([f"- {q}" for q in po_analysis.get('questions', [])])
        
        se_questions = "\n".join([f"- {q}" for q in se_analysis.get('technical_questions', [])])
        se_architecture = se_analysis.get('architecture', {})
        se_phases = "\n".join([f"- {phase}" for phase in se_analysis.get('implementation_phases', [])])
        estimated_effort = se_analysis.get('complexity_analysis', {}).get('estimated_effort', '2-4 weeks')
        
        # Create prompt for coordination and Claude Code prompt generation
        system_prompt = """You are an Engineering Manager AI agent. Your job is to:
1. Facilitate collaboration between Product Owner and Staff Engineer agents
2. Resolve conflicts and fill gaps between business specs and technical architecture
3. Generate specific, actionable prompts for Claude Code to implement the solution
4. Coordinate the implementation process and ensure quality

You work with other AI agents and generate prompts for automated development.
Focus on creating clear, executable prompts that Claude Code can follow."""
        
        coordination_prompt = f"""Task: {task}
Stack: {stack}

{agent_messages}

Product Owner Analysis:
Specifications:
{po_specs}

Questions from PO:
{po_questions}

Staff Engineer Analysis:
Technical Questions:
{se_questions}

Implementation Phases:
{se_phases}

Architecture: {se_architecture}
Estimated Effort: {estimated_effort}

As an Engineering Manager AI, you need to:

1. COORDINATION: Identify conflicts between PO specs and technical architecture
2. RESOLUTION: Provide solutions to bridge any gaps
3. CLAUDE_CODE_PROMPTS: Generate 3-5 specific prompts for Claude Code to implement this
4. EXECUTION_PLAN: Create a step-by-step execution plan
5. QUALITY_GATES: Define validation checkpoints
6. PRIORITY_ASSESSMENT: Evaluate project priority and resource allocation

Format as JSON:
{{
  "coordination": {{
    "conflicts_identified": ["Conflict 1", "Conflict 2"],
    "resolutions": ["Resolution 1", "Resolution 2"]
  }},
  "claude_code_prompts": [
    "Prompt 1: Create the database schema for...",
    "Prompt 2: Implement the backend API endpoints for...",
    "Prompt 3: Build the frontend components for..."
  ],
  "execution_plan": [
    "Step 1: Execute first Claude Code prompt",
    "Step 2: Execute second Claude Code prompt",
    "Step 3: Integration and testing"
  ],
  "quality_gates": [
    "Gate 1: Database schema validated",
    "Gate 2: API endpoints tested",
    "Gate 3: Frontend integration working"
  ],
  "priority_assessment": {{
    "priority_level": "high/medium/low",
    "business_impact": "Description of business impact",
    "recommended_timeline": "X weeks"
  }}
}}
"""
        
        # Get coordination analysis from Claude
        message = self.client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2500,
            temperature=0.3,
            system=system_prompt,
            messages=[{"role": "user", "content": coordination_prompt}]
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
                "coordination": {
                    "conflicts_identified": ["No major conflicts identified"],
                    "resolutions": ["Proceed with implementation as planned"]
                },
                "claude_code_prompts": [
                    f"Create database schema for {task}",
                    f"Implement backend API for {task}",
                    f"Build frontend components for {task}"
                ],
                "execution_plan": [
                    "Execute database setup",
                    "Implement backend services",
                    "Build frontend interface",
                    "Integration testing"
                ],
                "quality_gates": [
                    "Database schema validated",
                    "API endpoints tested",
                    "Frontend functionality verified"
                ],
                "priority_assessment": {
                    "priority_level": "medium",
                    "business_impact": f"Implementation of {task} will improve user workflow",
                    "recommended_timeline": estimated_effort
                }
            }
    
    def generate_fallback_synthesis(self, task, solution):
        """Generate a fallback synthesis if API call fails"""
        if "dashboard" in task.lower() and "analytics" in task.lower():
            return {
                "approved": True,
                "next_steps": [
                    f"Assign resources to complete in {solution['estimated_time']}",
                    "Coordinate with Data team to define key metrics",
                    "Prepare infrastructure for handling large data volumes",
                    "Configure CI/CD pipeline for continuous updates"
                ],
                "blockers": ["Pending confirmation of production data access"],
                "notes": "High priority - The dashboard is required for the quarterly presentation"
            }, "EXECUTIVE SUMMARY: Analytics dashboard approved with high priority for the quarterly presentation."
        elif "notificaciones" in task.lower() or "notifications" in task.lower():
            return {
                "approved": True,
                "next_steps": [
                    f"Assign resources to complete in {solution['estimated_time']}",
                    "Evaluate server performance impact with increased WebSocket connections",
                    "Coordinate with Product to prioritize notification types",
                    "Plan A/B test for optimal notification frequency"
                ],
                "blockers": ["Pending approval for FCM use in iOS"],
                "notes": "Project approved - Users have requested real-time notifications"
            }, "EXECUTIVE SUMMARY: Notification system approved - medium priority, pending iOS approval."
        elif "chat" in task.lower() or "mensajes" in task.lower() or "messages" in task.lower():
            return {
                "approved": True,
                "next_steps": [
                    f"Assign resources to complete in {solution['estimated_time']}",
                    "Evaluate scalability options for multiple simultaneous connections",
                    "Coordinate with UX team to define user interface",
                    "Establish message and attachment retention policy",
                    "Prepare load testing plan to simulate intensive use"
                ],
                "blockers": [
                    "Need to define user limits per chat room",
                    "Pending decision on file storage (S3 vs local storage)"
                ],
                "notes": "Project approved with medium priority - This is a highly requested feature"
            }, "EXECUTIVE SUMMARY: Real-time chat system approved - need to define scalability limits."
        else:
            # Generic synthesis for other tasks
            return {
                "approved": True,
                "next_steps": [
                    f"Assign resources to complete in {solution['estimated_time']}",
                    "Coordinate with QA team to define test cases",
                    "Prepare development and staging environments",
                    "Define acceptance criteria with Product Owner"
                ],
                "blockers": [],
                "notes": "Project evaluated and approved for implementation"
            }, f"EXECUTIVE SUMMARY: Implementation of '{task}' approved and planned."
    
    def run(self):
        """Main agent execution loop"""
        print("Engineering Manager AI Agent: Starting")
        
        # Update status to initializing
        self.comm.update_status("initializing")
        
        try:
            # Wait for both agents to complete their analyses
            self.wait_for_analyses()
            
            # Read the shared JSON data
            data = self.comm.read_json()
            task = data.get('task', 'Implementar funcionalidad')
            po_analysis = data.get('product_owner_analysis', {})
            se_analysis = data.get('staff_engineer_analysis', {})
            
            print("Engineering Manager AI: Coordinating agent analyses:")
            print(f"Product Owner: {len(po_analysis.get('specifications', []))} specifications")
            print(f"Staff Engineer: {len(se_analysis.get('implementation_phases', []))} implementation phases")
            
            try:
                # Coordinate agents and generate Claude Code prompts
                print(f"\nEngineering Manager AI: Coordinating and generating implementation prompts for: {task}")
                coordination = self.coordinate_and_generate_prompts(task, po_analysis, se_analysis)
                api_used = True
            except Exception as e:
                print(f"\nEngineering Manager AI: Error during coordination: {e}")
                print("Using fallback coordination...")
                coordination = {
                    "coordination": {
                        "conflicts_identified": ["No major conflicts identified"],
                        "resolutions": ["Proceed with implementation as planned"]
                    },
                    "claude_code_prompts": [
                        f"Create database schema for {task}",
                        f"Implement backend API for {task}",
                        f"Build frontend components for {task}"
                    ],
                    "execution_plan": [
                        "Execute database setup",
                        "Implement backend services", 
                        "Build frontend interface",
                        "Integration testing"
                    ],
                    "quality_gates": [
                        "Database schema validated",
                        "API endpoints tested",
                        "Frontend functionality verified"
                    ],
                    "priority_assessment": {
                        "priority_level": "medium",
                        "business_impact": f"Implementation of {task} will improve user workflow",
                        "recommended_timeline": "2-4 weeks"
                    }
                }
                api_used = False
            
            # Send coordination feedback to other agents
            conflicts = coordination['coordination']['conflicts_identified']
            resolutions = coordination['coordination']['resolutions']
            
            if len(conflicts) > 0 and conflicts[0] != "No major conflicts identified":
                # Send feedback about conflicts
                self.comm.send_message_to_agent(
                    "product_owner",
                    "coordination_feedback",
                    f"Identified conflicts: {'; '.join(conflicts[:2])}. Resolutions: {'; '.join(resolutions[:2])}"
                )
                
                self.comm.send_message_to_agent(
                    "staff_engineer",
                    "coordination_feedback",
                    f"Technical conflicts resolved: {'; '.join(resolutions[:2])}. Ready for implementation."
                )
            else:
                # No conflicts, proceed with implementation
                self.comm.send_message_to_agent(
                    "product_owner",
                    "implementation_ready",
                    f"No conflicts identified. Generated {len(coordination['claude_code_prompts'])} Claude Code prompts for implementation."
                )
                
                self.comm.send_message_to_agent(
                    "staff_engineer",
                    "implementation_ready",
                    f"Architecture validated. {len(coordination['execution_plan'])} execution steps planned."
                )
            
            # Update the shared data with coordination results
            data = self.comm.read_json()  # Read again to get any changes
            data['engineering_manager_coordination'] = coordination
            data['engineering_manager_reasoning'] = {
                "approach": "AI-driven coordination and prompt generation" if api_used else "Fallback coordination",
                "agent_type": "Engineering Manager AI Agent",
                "focus": [
                    "Facilitated collaboration between Product Owner and Staff Engineer",
                    "Resolved conflicts between business specs and technical architecture",
                    "Generated specific Claude Code prompts for implementation",
                    "Created quality gates and execution timeline"
                ]
            }
            
            # Mark workflow as ready for implementation
            data['workflow_state'] = "ready_for_implementation"
            
            # Write the updated JSON
            self.comm.write_json(data)
            
            # Update status to completed
            self.comm.update_status("completed", "Coordination completed, Claude Code prompts generated")
            
            # Print what was done
            print(f"\nEngineering Manager AI: Coordination completed for: {task}")
            print(f"\nConflicts identified: {len(coordination['coordination']['conflicts_identified'])}")
            print(f"Claude Code prompts generated: {len(coordination['claude_code_prompts'])}")
            
            print(f"\nClaude Code Prompts:")
            for i, prompt in enumerate(coordination['claude_code_prompts'], 1):
                print(f"  {i}. {prompt}")
            
            print(f"\nPriority: {coordination['priority_assessment']['priority_level']}")
            print(f"Timeline: {coordination['priority_assessment']['recommended_timeline']}")
            
            # Check other agents' status
            other_statuses = self.comm.check_other_agents_status()
            print(f"Other agents status: {other_statuses}")
            
            # Signal completion
            print("Engineering Manager AI Agent: Ready for Claude Code implementation")
            return coordination
            
        except Exception as e:
            print(f"Engineering Manager AI Agent Error: {e}")
            self.comm.update_status("error", str(e))
            raise

def main():
    # Get JSON path from command line arguments or use default
    if len(sys.argv) > 1:
        json_path = sys.argv[1]
    else:
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'shared', 'communication.json')
    
    # Create and run the Engineering Manager agent
    agent = EngineeringManagerAgent(json_path)
    agent.run()

if __name__ == "__main__":
    main()