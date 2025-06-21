PoC4: Conversational Agent Pipeline

MISSION: Create a simple conversational agent to understand the complexity of conversations using a pipeline approach.

APPROACH:
- Series of functions that pipe into each other
- Each function uses LLMs internally
- JSON file as source of truth for data editing between steps
- CLI interface to start the pipeline
- User can edit data between function calls

PIPELINE FUNCTIONS:
1. Input Processing - Parse and understand user input
2. Context Building - Build conversation context from history
3. Intent Recognition - Identify what the user wants
4. Response Generation - Generate appropriate response
5. Output Formatting - Format the final response

TECHNICAL CONSTRAINTS:
- Keep it straightforward technically
- Focus on proving value and that the system works
- Use JSON files for data persistence between steps
- Allow manual editing between pipeline steps
- Simple CLI interface