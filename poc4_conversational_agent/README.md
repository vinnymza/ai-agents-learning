# PoC4: Conversational Agent Pipeline

A production-ready pipeline-based conversational agent with advanced token management, project organization, and intelligent conversation compaction.

## Mission

Create a comprehensive conversational agent that demonstrates conversation complexity through discrete processing steps while providing enterprise-grade features like token tracking, cost analysis, and intelligent context management.

## Architecture

The system uses a **pipeline architecture** where each function processes data and pipes it to the next step:

```
User Input → Input Processing → Context Building → Intent Analysis → Response Generation → Output Formatting → User Output
```

### Pipeline Steps

1. **Input Processing** (`input_processor.py`)
   - Clean and structure user input
   - Extract basic metadata (word count, timestamps, etc.)

2. **Context Building** (`context_builder.py`)
   - Gather conversation history
   - Build relevant context from previous messages
   - Track session information

3. **Intent Analysis** (`intent_analyzer.py`)
   - Classify user intent (question, request, greeting, etc.)
   - Extract entities and calculate confidence
   - Determine if historical context is needed

4. **Response Generation** (`response_generator.py`)
   - Generate response using Claude API
   - Incorporate context and intent analysis
   - Provide reasoning for response choices

5. **Output Formatting** (`output_formatter.py`)
   - Format response for user display
   - Add metadata and processing information
   - Update conversation history

## Key Features

### 🗂️ Project Management
- **Multi-Project Support**: Separate conversation projects with isolated histories
- **Project Commands**: Create, select, and manage multiple conversation contexts
- **Project-Specific Data**: Each project maintains its own conversation state and token usage

### 🔢 Advanced Token Management
- **Real-Time Token Tracking**: Exact input/output token counting from Anthropic API
- **Cost Analysis**: Precise cost tracking per message, project, and overall
- **Multi-Model Support**: Claude 3.5 Haiku, Claude 4 Sonnet, and Claude 4 Opus
- **Usage Statistics**: Detailed analytics for token consumption patterns

### 🧠 Intelligent Context Management
- **Context Window Monitoring**: Real-time percentage of context usage with color-coded warnings
- **Smart Compaction**: Automated conversation compaction when approaching token limits
- **Configurable Thresholds**: Customizable limits for compaction triggers and message retention
- **Context Optimization**: Maintains conversation quality while managing token efficiency

### 🔧 Pipeline Features
- **Direct Input Interface**: Streamlined chat interface with hidden slash commands
- **Manual Editing**: Edit conversation state between pipeline steps
- **Step-by-Step Execution**: Inspect and modify data at each processing stage
- **Claude Integration**: Uses latest Claude models with configurable parameters

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
# Copy .env from parent directory or create with:
ANTHROPIC_API_KEY=your_api_key_here
```

## Usage

### Quick Start

```bash
python main.py
```

The system uses a direct chat interface. Type `/help` to see available commands.

### Command Reference

#### Project Management
```bash
/projects              # List all conversation projects
/project <name>        # Select or create a project
/project-new <name>    # Create a new project (fails if exists)
/project-current       # Show current project info
```

#### Conversation & Analysis
```bash
/tokens               # Show detailed token usage statistics
/compact              # Analyze and compact conversation
/step                 # Run step-by-step pipeline
/view                 # View conversation state
/edit                 # Edit conversation state
/reset                # Reset current project
```

#### System
```bash
/help                 # Show all commands
/exit                 # Exit program
```

### Token Management

The system provides comprehensive token tracking:

- **Real-time monitoring**: See token usage and costs after each message
- **Context percentage**: Visual indication of context window usage
- **Automatic warnings**: Alerts when approaching context limits
- **Smart compaction**: Intelligent conversation optimization

### Project Workflow

1. **Create/Select Project**: `curl /project my-project`
2. **Start Conversation**: Type your message directly
3. **Monitor Usage**: Check token consumption with `/tokens`
4. **Optimize Context**: Use `/compact` when recommended

### Example Session

```
🤖 PoC4: Conversational Agent Pipeline
Type /help for commands

💬 /project my-work
✅ Created and selected new project: my-work

💬 Hello, can you help me with a product roadmap?
✅ Input processed: 9 words
✅ Context built: 1 messages in history
✅ Intent analyzed: request (confidence: 0.80)
✅ Response generated: 342 characters
   Tokens: 45 in + 89 out = 134 total
   Cost: $0.000392
   Context usage: 2.1% of available window

Hello! I'd be happy to help you create a product roadmap...

💬 /tokens
📊 Token Usage Statistics
==================================================

Current Project: my-work
Total messages: 2
Total tokens: 134
  Input tokens: 45
  Output tokens: 89
Total cost: $0.000392

Context Usage:
Estimated context tokens: 420
Context usage: 2.1%
✅ Context usage is healthy
```

## Learning Outcomes

This PoC demonstrates advanced conversational AI concepts:

### 🔍 Pipeline Architecture
- **Modular Design**: Independent, testable pipeline steps
- **Data Flow Visibility**: Clear transformation at each stage
- **State Management**: Comprehensive conversation state tracking
- **Debugging Capabilities**: Inspect and modify processing at any step

### 💰 Production Concerns
- **Token Economics**: Real-time cost tracking and optimization
- **Context Management**: Intelligent handling of long conversations
- **Resource Optimization**: Automated compaction strategies
- **Performance Monitoring**: Detailed usage analytics

### 🏗️ Enterprise Features
- **Multi-Tenancy**: Project-based conversation isolation
- **Scalability Patterns**: Efficient state management for multiple projects
- **Configuration Management**: Centralized constants for easy tuning
- **Operational Visibility**: Comprehensive logging and metrics

### 🤖 AI Integration Patterns
- **Model Flexibility**: Support for multiple Claude models
- **Response Quality**: Balanced creativity and coherence parameters
- **Context Optimization**: Smart conversation history management
- **Error Handling**: Robust API integration with fallbacks

## Technical Architecture

### Core Components
- **Pipeline Processing**: Modular, inspectable conversation processing
- **Project Management**: Multi-project conversation isolation
- **Token Tracking**: Real-time usage monitoring and cost analysis
- **Context Management**: Intelligent conversation compaction
- **Configuration System**: Centralized, tunable parameters

### Key Innovations
- **Real-time Token Counting**: Direct API response parsing for exact usage
- **Smart Compaction**: Context-aware conversation optimization
- **Project Isolation**: Separate conversation contexts with shared infrastructure
- **Visual Feedback**: Color-coded warnings and usage indicators

## Production Readiness

This PoC includes enterprise-grade features:

✅ **Cost Management**: Precise token tracking and budget monitoring  
✅ **Scalability**: Project-based architecture for multiple users  
✅ **Observability**: Comprehensive logging and analytics  
✅ **Configuration**: Centralized constants for easy deployment tuning  
✅ **Error Handling**: Robust API integration with graceful degradation  
✅ **Resource Optimization**: Automated context management

## File Structure

### Core Pipeline
- `main.py` - CLI interface, command handling, and pipeline orchestration
- `input_processor.py` - Step 1: Process raw user input and metadata
- `context_builder.py` - Step 2: Build conversation context and history
- `intent_analyzer.py` - Step 3: Analyze user intent and extract entities
- `response_generator.py` - Step 4: Generate responses with token tracking
- `output_formatter.py` - Step 5: Format output and update conversation history

### Management Systems
- `project_manager.py` - Multi-project conversation management
- `token_tracker.py` - Real-time token usage tracking and cost analysis
- `constants.py` - Configuration constants and model settings

### Data Files
- `projects/*.json` - Individual project conversation states
- `token_usage.json` - Comprehensive token usage analytics
- `CLAUDE.md` - Instructions for Claude assistant
- `requirements.txt` - Python dependencies

### Configuration
The system uses a centralized configuration approach:
- **Model Settings**: Claude model selection and parameters
- **Context Management**: Token limits and compaction thresholds  
- **Display Options**: Color coding and warning levels
- **API Configuration**: Temperature, top-p, and token limits