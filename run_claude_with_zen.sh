#!/bin/bash
# Run Claude Code with Zen MCP Server (without Docker)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Claude Code with Zen MCP Server ===${NC}"
echo

# Check for required environment variables
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${RED}ERROR: ANTHROPIC_API_KEY environment variable not set${NC}"
    echo "Please set: export ANTHROPIC_API_KEY=your-key-here"
    exit 1
fi

# Check for at least one AI provider API key
if [ -z "$GEMINI_API_KEY" ] && [ -z "$OPENAI_API_KEY" ] && [ -z "$OPENROUTER_API_KEY" ]; then
    echo -e "${YELLOW}WARNING: No AI provider API keys found for Zen MCP${NC}"
    echo "Set at least one of: GEMINI_API_KEY, OPENAI_API_KEY, or OPENROUTER_API_KEY"
    echo "The MCP server will start but won't be able to use AI tools"
    echo
fi

# Set workspace root
export WORKSPACE_ROOT="${WORKSPACE_ROOT:-$HOME}"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if Claude Code is installed
if ! command -v claude &> /dev/null; then
    echo -e "${RED}ERROR: Claude Code CLI not found${NC}"
    echo "Install with: npm install -g @anthropic-ai/claude-code"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 not found${NC}"
    exit 1
fi

# Install Python dependencies if needed
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip3 install -r "$SCRIPT_DIR/requirements.txt" --quiet
fi

# Check/start Redis
if command -v redis-cli &> /dev/null; then
    if ! redis-cli ping &> /dev/null; then
        echo "Starting Redis server..."
        redis-server --daemonize yes --port 6379
        sleep 2
    else
        echo "Redis is already running"
    fi
else
    echo -e "${YELLOW}WARNING: Redis not found. Some features may not work properly${NC}"
fi

# Create temporary MCP config
MCP_CONFIG=$(mktemp /tmp/zen-mcp-config.XXXXXX.json)
cat > "$MCP_CONFIG" <<EOF
{
  "mcpServers": {
    "zen": {
      "command": "python3",
      "args": ["$SCRIPT_DIR/server.py"],
      "env": {
        "GEMINI_API_KEY": "${GEMINI_API_KEY:-}",
        "OPENAI_API_KEY": "${OPENAI_API_KEY:-}",
        "OPENROUTER_API_KEY": "${OPENROUTER_API_KEY:-}",
        "WORKSPACE_ROOT": "$WORKSPACE_ROOT",
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379"
      }
    }
  }
}
EOF

# Cleanup function
cleanup() {
    rm -f "$MCP_CONFIG"
}
trap cleanup EXIT

# Parse arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 <prompt> [working_directory]"
    echo
    echo "Examples:"
    echo "  $0 \"Review this code with zen chat tool\""
    echo "  $0 \"Analyze main.py with zen analyze tool\" /path/to/project"
    exit 1
fi

PROMPT="$1"
WORKING_DIR="${2:-$(pwd)}"

# Run Claude Code with MCP
echo -e "\n${GREEN}Running Claude Code...${NC}"
echo "Working directory: $WORKING_DIR"
echo "Prompt: $PROMPT"
echo -e "\n$( printf '=%.0s' {1..50} )\n"

cd "$WORKING_DIR"
claude -p "$PROMPT" \
    --mcp-config "$MCP_CONFIG" \
    --allowedTools "mcp__zen__chat,mcp__zen__thinkdeep,mcp__zen__codereview,mcp__zen__precommit,mcp__zen__debug,mcp__zen__analyze"