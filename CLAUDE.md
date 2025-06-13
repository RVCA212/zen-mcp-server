# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Testing
```bash
# Run unit tests (no API key required)
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run simulation tests (requires API keys)
python communication_simulator_test.py

# Run specific simulation tests
python communication_simulator_test.py --tests basic_conversation content_validation

# List available simulation tests
python communication_simulator_test.py --list-tests
```

### Docker Development
```bash
# Complete setup (builds containers, configures APIs)
./setup-docker.sh

# Start services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down

# Rebuild after changes
docker compose build --no-cache
```

### Code Quality
```bash
# Format code (configured in pyproject.toml)
black . --line-length 120
isort . --profile black

# Lint code
ruff check . --fix
```

## Architecture Overview

### Core Server Architecture
This is an MCP (Model Context Protocol) server that orchestrates multiple AI providers through a unified interface:

- **MCP Server (`server.py`)**: Main entry point, handles protocol communication and tool routing
- **Provider System (`providers/`)**: Abstracted interface for different AI providers (Google, OpenAI, OpenRouter)
- **Tool Framework (`tools/`)**: Modular tools for different AI tasks (chat, code review, debugging, analysis)
- **Conversation Memory (`utils/conversation_memory.py`)**: Redis-based threading for multi-turn conversations

### Key Design Patterns

**Provider Abstraction**: All AI providers implement `ModelProvider` interface, enabling seamless switching between Google Gemini, OpenAI O3, and OpenRouter models.

**Tool Pattern**: Each tool inherits from `BaseTool` and implements:
- Request validation (Pydantic models)
- Prompt preparation with file content handling
- Response formatting and conversation threading
- Model-agnostic execution

**Auto Mode**: When `DEFAULT_MODEL=auto`, Claude automatically selects the optimal model for each task based on capabilities defined in `config.py`.

**Conversation Threading**: Uses Redis to maintain conversation context across multiple exchanges, supporting up to 5 turns per thread with 1-hour expiry.

### File Processing Architecture

**Deduplication Logic**: Tools automatically filter out files already embedded in conversation history to optimize token usage while maintaining access through conversation context.

**Token Management**: Dynamic token allocation based on model capabilities:
- Small context models (<300K): 60% content, 40% response
- Large context models (>300K): 80% content, 20% response

**MCP Bypass**: Large prompts (>50K chars) are automatically handled as files to bypass MCP's 25K token limit.

### Configuration System

**Environment-based Config**: 
- `config.py` centralizes all configuration with environment variable overrides
- Provider priority: Native APIs (Gemini, OpenAI) take precedence over OpenRouter
- Thinking modes control computational budget for Gemini models

**Model Capabilities**: Each provider defines model capabilities including context windows, temperature constraints, and feature support through `ModelCapabilities` dataclass.

## Tool Architecture

### Tool Types
- **chat**: General development discussions and brainstorming
- **thinkdeep**: Extended reasoning with Gemini's thinking modes
- **codereview**: Professional code review with severity levels  
- **precommit**: Git change validation before commits
- **debug**: Root cause analysis and debugging assistance
- **analyze**: File and architecture analysis

### Common Tool Patterns

**File Handling**: All tools use `_prepare_file_content_for_prompt()` which:
1. Filters files already in conversation history
2. Reads content within token budgets
3. Generates notes about skipped files

**Request Flow**:
1. Request validation via Pydantic models
2. File path security validation (absolute paths required)
3. Prompt preparation with conversation history injection
4. Model provider selection and execution
5. Response formatting and conversation threading

**Temperature Validation**: Tools automatically validate and correct temperature values based on model constraints defined in provider capabilities.

## Provider System Details

### Provider Registry
`ModelProviderRegistry` maintains mapping between models and providers:
- Auto-detection of available providers based on API keys
- Model name resolution (e.g., "flash" → "gemini-2.0-flash")
- Provider capability lookup for token limits and features

### Model Capabilities
Each provider defines:
- Context window sizes
- Temperature constraints (fixed, range, or discrete values)
- Extended thinking support (Gemini only)
- Default configurations

### OpenRouter Integration
Special handling for OpenRouter provider:
- Dynamic model registry from `conf/openrouter_models.json`
- Alias resolution for user-friendly names
- Fallback provider when native APIs unavailable

## Testing Strategy

### Unit Tests (`tests/`)
Mock-based tests covering:
- Tool execution logic
- Provider abstractions
- Configuration validation
- Conversation threading

### Simulation Tests (`simulator_tests/`)
End-to-end tests requiring actual API keys:
- Real MCP protocol communication
- Docker container integration
- Redis conversation persistence
- Cross-tool conversation flows

### Key Test Files
- `test_server.py`: Core server functionality
- `test_providers.py`: Provider abstraction testing
- `test_conversation_memory.py`: Redis threading validation
- `communication_simulator_test.py`: Full end-to-end simulation

## Development Guidelines

### Adding New Tools
1. Create tool class inheriting from `BaseTool`
2. Implement required abstract methods
3. Define Pydantic request model
4. Add system prompt in `prompts/tool_prompts.py`
5. Register in `server.py` TOOLS dictionary

### Adding New Providers
1. Implement `ModelProvider` interface
2. Define model capabilities with constraints
3. Register in provider registry
4. Add configuration validation
5. Update documentation

### File Security
- All file paths must be absolute
- Path validation prevents traversal attacks
- Docker environment path translation for workspace mapping

### Conversation Threading
- Create threads with `create_thread()`
- Add turns with `add_turn()`
- Reconstruct context with `build_conversation_history()`
- Use continuation_id for cross-tool conversations