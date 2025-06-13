#!/usr/bin/env python3
"""
Run Claude Code with Zen MCP Server (without Docker)

This script sets up and runs Claude Code SDK with the Zen MCP server in non-interactive mode.
It handles:
1. Starting the MCP server locally (no Docker)
2. Creating the MCP configuration
3. Running Claude Code with the MCP configuration
"""

import asyncio
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
import signal
import atexit

# Global process tracking
mcp_process = None
redis_process = None

def cleanup():
    """Clean up processes on exit"""
    global mcp_process, redis_process
    
    if mcp_process:
        print("Stopping MCP server...")
        mcp_process.terminate()
        try:
            mcp_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            mcp_process.kill()
    
    if redis_process:
        print("Stopping Redis...")
        redis_process.terminate()
        try:
            redis_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            redis_process.kill()

# Register cleanup
atexit.register(cleanup)

def signal_handler(signum, frame):
    """Handle interruption signals"""
    print("\nReceived interrupt signal, cleaning up...")
    cleanup()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def check_dependencies():
    """Check if required dependencies are installed"""
    required = {
        "claude": "Claude Code CLI (npm install -g @anthropic-ai/claude-code)",
        "redis-server": "Redis server (apt-get install redis-server or brew install redis)",
        "python3": "Python 3.10+"
    }
    
    missing = []
    for cmd, desc in required.items():
        try:
            subprocess.run([cmd, "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing.append(f"- {desc}")
    
    if missing:
        print("Missing dependencies:")
        print("\n".join(missing))
        sys.exit(1)

def setup_environment():
    """Set up environment variables"""
    # Check for required API keys
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        print("Please set: export ANTHROPIC_API_KEY=your-key-here")
        sys.exit(1)
    
    # Optional API keys for Zen MCP
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    
    if not any([gemini_key, openai_key, openrouter_key]):
        print("WARNING: No AI provider API keys found for Zen MCP")
        print("Set at least one of: GEMINI_API_KEY, OPENAI_API_KEY, or OPENROUTER_API_KEY")
        print("The MCP server will start but won't be able to use AI tools")
    
    # Set working directory
    workspace_root = os.getenv("WORKSPACE_ROOT", os.path.expanduser("~"))
    os.environ["WORKSPACE_ROOT"] = workspace_root
    
    return {
        "anthropic": anthropic_key,
        "gemini": gemini_key,
        "openai": openai_key,
        "openrouter": openrouter_key,
        "workspace": workspace_root
    }

def start_redis():
    """Start Redis server if not already running"""
    global redis_process
    
    # Check if Redis is already running
    try:
        subprocess.run(["redis-cli", "ping"], capture_output=True, check=True)
        print("Redis is already running")
        return
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    print("Starting Redis server...")
    try:
        redis_process = subprocess.Popen(
            ["redis-server", "--port", "6379"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        # Wait a moment for Redis to start
        import time
        time.sleep(2)
        
        # Verify Redis started
        subprocess.run(["redis-cli", "ping"], capture_output=True, check=True)
        print("Redis started successfully")
    except Exception as e:
        print(f"Failed to start Redis: {e}")
        print("Some features may not work properly without Redis")

def install_dependencies():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    zen_dir = Path(__file__).parent
    requirements_file = zen_dir / "requirements.txt"
    
    if requirements_file.exists():
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], check=True)
    else:
        print("WARNING: requirements.txt not found, skipping dependency installation")

def create_mcp_config(zen_server_path):
    """Create MCP configuration for Claude Code"""
    config = {
        "mcpServers": {
            "zen": {
                "command": sys.executable,
                "args": [str(zen_server_path / "server.py")],
                "env": {
                    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
                    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
                    "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY", ""),
                    "WORKSPACE_ROOT": os.getenv("WORKSPACE_ROOT", ""),
                    "REDIS_HOST": "localhost",
                    "REDIS_PORT": "6379"
                }
            }
        }
    }
    
    # Create temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f, indent=2)
        return f.name

def run_claude_code(prompt, mcp_config_path, working_dir=None):
    """Run Claude Code with the MCP configuration"""
    cmd = [
        "claude", "-p", prompt,
        "--mcp-config", mcp_config_path,
        "--allowedTools", "mcp__zen__chat,mcp__zen__thinkdeep,mcp__zen__codereview,mcp__zen__precommit,mcp__zen__debug,mcp__zen__analyze"
    ]
    
    if working_dir:
        cmd.extend(["--cwd", working_dir])
    
    print(f"Running Claude Code with command:")
    print(" ".join(cmd))
    print()
    
    # Run Claude Code
    result = subprocess.run(cmd, cwd=working_dir)
    return result.returncode

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python run_claude_with_zen.py <prompt> [working_directory]")
        print()
        print("Examples:")
        print('  python run_claude_with_zen.py "Review this code with zen chat tool"')
        print('  python run_claude_with_zen.py "Analyze main.py with zen analyze tool" /path/to/project')
        sys.exit(1)
    
    prompt = sys.argv[1]
    working_dir = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()
    
    print("=== Claude Code with Zen MCP Server ===")
    print()
    
    # Check dependencies
    print("Checking dependencies...")
    check_dependencies()
    
    # Set up environment
    print("Setting up environment...")
    env = setup_environment()
    
    # Install Python dependencies
    install_dependencies()
    
    # Start Redis
    start_redis()
    
    # Get zen server path
    zen_server_path = Path(__file__).parent.absolute()
    
    # Create MCP configuration
    print("Creating MCP configuration...")
    mcp_config_path = create_mcp_config(zen_server_path)
    
    try:
        # Run Claude Code
        print(f"\nRunning Claude Code in: {working_dir}")
        print(f"Prompt: {prompt}")
        print("\n" + "="*50 + "\n")
        
        exit_code = run_claude_code(prompt, mcp_config_path, working_dir)
        
        if exit_code != 0:
            print(f"\nClaude Code exited with code: {exit_code}")
            sys.exit(exit_code)
    
    finally:
        # Clean up config file
        if os.path.exists(mcp_config_path):
            os.unlink(mcp_config_path)
        
        # Cleanup will be handled by atexit

if __name__ == "__main__":
    main()