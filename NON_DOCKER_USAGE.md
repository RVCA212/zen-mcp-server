# Running Claude Code with Zen MCP Server (Without Docker)

This guide explains how to run Claude Code SDK with the Zen MCP server without using Docker, allowing you to leverage multiple AI models through Claude Code's non-interactive mode.

## Prerequisites

1. **Claude Code CLI**
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

2. **Python 3.10+**
   ```bash
   python3 --version  # Should be 3.10 or higher
   ```

3. **Redis** (optional but recommended for conversation threading)
   ```bash
   # Ubuntu/Debian
   sudo apt-get install redis-server
   
   # macOS
   brew install redis
   
   # Or run without Redis (limited functionality)
   ```

4. **API Keys** (set as environment variables)
   ```bash
   # Required for Claude Code
   export ANTHROPIC_API_KEY="your-anthropic-api-key"
   
   # At least one of these for Zen MCP tools
   export GEMINI_API_KEY="your-gemini-api-key"
   export OPENAI_API_KEY="your-openai-api-key"
   export OPENROUTER_API_KEY="your-openrouter-api-key"
   
   # Optional: Set your workspace root (defaults to home directory)
   export WORKSPACE_ROOT="/path/to/your/projects"
   ```

## Quick Start

### Option 1: Using the Bash Script

```bash
# Make the script executable (first time only)
chmod +x run_claude_with_zen.sh

# Run Claude Code with a zen tool
./run_claude_with_zen.sh "Use zen chat to help me understand this Python code" /path/to/project

# Examples of using different tools
./run_claude_with_zen.sh "Use zen analyze to analyze the architecture of src/"
./run_claude_with_zen.sh "Use zen codereview to review the changes in my last commit"
./run_claude_with_zen.sh "Use zen debug to help me figure out why my tests are failing"
./run_claude_with_zen.sh "Use zen thinkdeep to design a caching strategy for my API"
```

### Option 2: Using the Python Script

```bash
# Run with Python directly
python3 run_claude_with_zen.py "Use zen chat to explain this code" /path/to/project

# Or make it executable
chmod +x run_claude_with_zen.py
./run_claude_with_zen.py "Use zen analyze on main.py"
```

### Option 3: Manual Setup

1. **Install Python dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Start Redis (if available)**
   ```bash
   redis-server --port 6379
   ```

3. **Create MCP configuration file** (`zen-mcp-config.json`)
   ```json
   {
     "mcpServers": {
       "zen": {
         "command": "python3",
         "args": ["/path/to/zen-mcp-server/server.py"],
         "env": {
           "GEMINI_API_KEY": "your-gemini-key",
           "OPENAI_API_KEY": "your-openai-key",
           "OPENROUTER_API_KEY": "your-openrouter-key",
           "WORKSPACE_ROOT": "/path/to/workspace",
           "REDIS_HOST": "localhost",
           "REDIS_PORT": "6379"
         }
       }
     }
   }
   ```

4. **Run Claude Code with MCP**
   ```bash
   claude -p "Your prompt here" \
     --mcp-config zen-mcp-config.json \
     --allowedTools "mcp__zen__chat,mcp__zen__thinkdeep,mcp__zen__codereview,mcp__zen__precommit,mcp__zen__debug,mcp__zen__analyze"
   ```

## Available Zen Tools

When using Claude Code with Zen MCP, you can access these tools:

- **`mcp__zen__chat`** - Collaborative AI chat for development discussions
- **`mcp__zen__thinkdeep`** - Extended reasoning for complex problems
- **`mcp__zen__codereview`** - Professional code review with severity levels
- **`mcp__zen__precommit`** - Pre-commit validation and checks
- **`mcp__zen__debug`** - Expert debugging assistance
- **`mcp__zen__analyze`** - Smart file and architecture analysis

## Usage Examples

### Basic Chat
```bash
./run_claude_with_zen.sh "Use zen chat to help me understand how this authentication system works"
```

### Code Review
```bash
./run_claude_with_zen.sh "Use zen codereview to review all Python files in src/ and suggest improvements"
```

### Debugging
```bash
./run_claude_with_zen.sh "Use zen debug to help me fix the memory leak in my application"
```

### Architecture Analysis
```bash
./run_claude_with_zen.sh "Use zen analyze to analyze the overall architecture and suggest improvements"
```

### Complex Multi-Tool Workflow
```bash
./run_claude_with_zen.sh "First use zen analyze to understand the codebase structure, then use zen chat to discuss refactoring options, and finally use zen codereview to validate the proposed changes"
```

## Advanced Usage

### Specify Working Directory
```bash
./run_claude_with_zen.sh "Use zen chat to explain this code" /path/to/specific/project
```

### Use with Pipes
```bash
echo "Explain this error and how to fix it" | ./run_claude_with_zen.sh "Use zen debug with the piped input"
```

### Programmatic Usage (Python)
```python
import subprocess
import json

# Create MCP config
config = {
    "mcpServers": {
        "zen": {
            "command": "python3",
            "args": ["/path/to/zen-mcp-server/server.py"],
            "env": {
                "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", ""),
                "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY", ""),
                "WORKSPACE_ROOT": os.getcwd()
            }
        }
    }
}

# Save config
with open("mcp-config.json", "w") as f:
    json.dump(config, f)

# Run Claude Code
result = subprocess.run([
    "claude", "-p", "Use zen chat to help optimize this function",
    "--mcp-config", "mcp-config.json",
    "--allowedTools", "mcp__zen__chat"
], capture_output=True, text=True)

print(result.stdout)
```

### Using with Claude Code SDK (TypeScript)
```typescript
import { query } from "@anthropic-ai/claude-code";

const mcpConfig = {
  mcpServers: {
    zen: {
      command: "python3",
      args: ["/path/to/zen-mcp-server/server.py"],
      env: {
        GEMINI_API_KEY: process.env.GEMINI_API_KEY,
        WORKSPACE_ROOT: process.cwd()
      }
    }
  }
};

// Save config to file
fs.writeFileSync("mcp-config.json", JSON.stringify(mcpConfig));

// Query with MCP
for await (const message of query({
  prompt: "Use zen analyze to review the architecture",
  options: {
    mcpConfig: "mcp-config.json",
    allowedTools: ["mcp__zen__analyze"]
  }
})) {
  console.log(message);
}
```

## Troubleshooting

### "Claude Code CLI not found"
Install Claude Code globally:
```bash
npm install -g @anthropic-ai/claude-code
```

### "No API keys found"
Ensure you've exported the required environment variables:
```bash
export ANTHROPIC_API_KEY="your-key"
export GEMINI_API_KEY="your-key"  # At least one AI provider key required
```

### "Redis connection failed"
The tools will work without Redis but won't have conversation memory. To enable Redis:
```bash
# Start Redis
redis-server --port 6379

# Or run without Redis (limited functionality)
```

### "Module not found" errors
Install Python dependencies:
```bash
cd /path/to/zen-mcp-server
pip3 install -r requirements.txt
```

## Tips

1. **Model Selection**: Use `DEFAULT_MODEL=auto` environment variable to let Claude automatically select the best model for each task.

2. **Specific Models**: Request specific models in your prompts:
   - "Use zen chat with gemini-2.0-flash for quick responses"
   - "Use zen thinkdeep with gemini-2.5-pro for complex analysis"
   - "Use zen debug with o3 for logical problems"

3. **Large Files**: The MCP server automatically handles large files by creating temporary files when content exceeds MCP's token limits.

4. **Conversation Threading**: With Redis enabled, conversations maintain context across multiple tool calls.

5. **Verbose Output**: Add `--verbose` flag to Claude Code for detailed logging:
   ```bash
   claude -p "..." --mcp-config config.json --verbose
   ```

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key for Claude Code |
| `GEMINI_API_KEY` | One required | Google AI Studio API key |
| `OPENAI_API_KEY` | One required | OpenAI API key for O3 models |
| `OPENROUTER_API_KEY` | One required | OpenRouter API key for multiple models |
| `WORKSPACE_ROOT` | No | Root directory for file operations (default: home) |
| `DEFAULT_MODEL` | No | Default model selection (auto, gemini, o3, etc.) |
| `THINKING_MODE` | No | Gemini thinking depth (minimal, standard, deep) |
| `LOG_LEVEL` | No | Logging verbosity (DEBUG, INFO, WARNING, ERROR) |