## Summary

I've created three solutions for running Claude Code with the zen mcp server without Docker:

### 1. **Bash Script** (`run_claude_with_zen.sh`)
Simple bash script that:
- Checks dependencies and API keys
- Installs Python requirements
- Starts Redis if available
- Creates temporary MCP config
- Runs Claude Code with the zen tools

Usage:
```bash
./run_claude_with_zen.sh "Use zen chat to help me understand this code" /path/to/project
```

### 2. **Python Script** (`run_claude_with_zen.py`)
More robust Python script with:
- Better process management
- Automatic cleanup
- Signal handling
- Detailed error messages

Usage:
```bash
python3 run_claude_with_zen.py "Use zen analyze on the architecture" /path/to/project
```

### 3. **Manual Setup Guide** (`NON_DOCKER_USAGE.md`)
Comprehensive documentation covering:
- Prerequisites and setup
- Multiple usage methods
- Advanced examples
- Troubleshooting

### Key Points:

1. **Required Environment Variables**:
   - `ANTHROPIC_API_KEY` - For Claude Code
   - At least one of: `GEMINI_API_KEY`, `OPENAI_API_KEY`, `OPENROUTER_API_KEY` - For zen tools

2. **MCP Configuration Format**:
   ```json
   {
     "mcpServers": {
       "zen": {
         "command": "python3",
         "args": ["/path/to/server.py"],
         "env": { /* API keys */ }
       }
     }
   }
   ```

3. **Tool Names for `--allowedTools`**:
   - `mcp__zen__chat`
   - `mcp__zen__thinkdeep`
   - `mcp__zen__codereview`
   - `mcp__zen__precommit`
   - `mcp__zen__debug`
   - `mcp__zen__analyze`
