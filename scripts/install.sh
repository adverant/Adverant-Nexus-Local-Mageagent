#!/bin/bash

# Nexus Local MageAgent - Complete Installation Script
# Installs and configures MageAgent multi-model orchestration for MLX
# Includes: Server, Menu Bar App, Claude Code Hooks, Slash Commands, VSCode Integration

set -e  # Exit on error

echo "==============================================================="
echo "  Nexus Local MageAgent - Complete Installation"
echo "  Multi-Model AI Orchestration for Apple Silicon"
echo "  Version 2.0.0"
echo "==============================================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Parse arguments
SKIP_MODELS=false
SKIP_MENUBAR=false
SKIP_AUTOSTART=false
SKIP_CLAUDE_CODE=false
SKIP_VSCODE=false

for arg in "$@"; do
    case $arg in
        --skip-models) SKIP_MODELS=true ;;
        --skip-menubar) SKIP_MENUBAR=true ;;
        --skip-autostart) SKIP_AUTOSTART=true ;;
        --skip-claude-code) SKIP_CLAUDE_CODE=true ;;
        --skip-vscode) SKIP_VSCODE=true ;;
        --minimal) SKIP_MODELS=true; SKIP_AUTOSTART=true ;;
        --server-only) SKIP_MENUBAR=true; SKIP_AUTOSTART=true; SKIP_CLAUDE_CODE=true; SKIP_VSCODE=true ;;
        --help)
            echo "Usage: ./scripts/install.sh [options]"
            echo ""
            echo "Options:"
            echo "  --skip-models       Skip MLX model download (~109GB)"
            echo "  --skip-menubar      Skip menu bar app installation"
            echo "  --skip-autostart    Skip LaunchAgent configuration"
            echo "  --skip-claude-code  Skip Claude Code hooks/commands"
            echo "  --skip-vscode       Skip VSCode integration"
            echo "  --minimal           Skip models and autostart"
            echo "  --server-only       Install server components only"
            echo "  --help              Show this help"
            exit 0
            ;;
    esac
done

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}Error: This script requires macOS with Apple Silicon${NC}"
    exit 1
fi

# Check for Apple Silicon
if [[ $(uname -m) != "arm64" ]]; then
    echo -e "${RED}Error: Apple Silicon (M1/M2/M3/M4) required${NC}"
    exit 1
fi

# Check memory
TOTAL_MEM=$(sysctl -n hw.memsize)
TOTAL_GB=$((TOTAL_MEM / 1024 / 1024 / 1024))
if [ $TOTAL_GB -lt 64 ]; then
    echo -e "${YELLOW}Warning: 128GB+ unified memory recommended for full MageAgent${NC}"
    echo -e "  Your system has ${TOTAL_GB}GB. Some patterns may not work.${NC}"
    echo ""
fi

echo "Checking Prerequisites..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo "  Install from: https://www.python.org/ or brew install python"
    exit 1
fi
echo -e "${GREEN}✓${NC} Python $(python3 --version | cut -d' ' -f2)"

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}Error: pip3 is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} pip3 installed"

# Check Node.js (optional but recommended)
if command -v node &> /dev/null; then
    echo -e "${GREEN}✓${NC} Node.js $(node --version)"
else
    echo -e "${YELLOW}!${NC} Node.js not found (optional, needed for npm commands)"
fi

# Check Xcode Command Line Tools (needed for Swift compilation)
if xcode-select -p &> /dev/null; then
    echo -e "${GREEN}✓${NC} Xcode Command Line Tools"
else
    echo -e "${YELLOW}!${NC} Xcode Command Line Tools not found"
    echo "  Install with: xcode-select --install"
fi

echo ""
echo "==============================================================="
echo -e "  ${CYAN}Step 1/7:${NC} Installing Python Dependencies"
echo "==============================================================="
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Install MLX and dependencies
pip3 install --quiet mlx mlx-lm
echo -e "${GREEN}✓${NC} MLX framework installed"

pip3 install --quiet fastapi uvicorn pydantic
echo -e "${GREEN}✓${NC} FastAPI server dependencies installed"

pip3 install --quiet huggingface_hub
echo -e "${GREEN}✓${NC} Hugging Face Hub installed"

# Install from requirements.txt if exists
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    pip3 install --quiet -r "$SCRIPT_DIR/requirements.txt"
    echo -e "${GREEN}✓${NC} Additional dependencies installed"
fi

echo ""
echo "==============================================================="
echo -e "  ${CYAN}Step 2/7:${NC} Setting Up Directory Structure"
echo "==============================================================="
echo ""

# Create all required directories
mkdir -p ~/.claude/mageagent
mkdir -p ~/.claude/scripts
mkdir -p ~/.claude/debug
mkdir -p ~/.claude/hooks
mkdir -p ~/.claude/commands
mkdir -p ~/.claude/mageagent-menubar/icons
mkdir -p ~/.cache/mlx-models
mkdir -p ~/Library/LaunchAgents

echo -e "${GREEN}✓${NC} Directory structure created"

echo ""
echo "==============================================================="
echo -e "  ${CYAN}Step 3/7:${NC} Installing Server Components"
echo "==============================================================="
echo ""

# Copy server files
cp "$SCRIPT_DIR/mageagent/server.py" ~/.claude/mageagent/
echo -e "${GREEN}✓${NC} MageAgent server installed"

cp "$SCRIPT_DIR/scripts/mageagent-server.sh" ~/.claude/scripts/
chmod +x ~/.claude/scripts/mageagent-server.sh
echo -e "${GREEN}✓${NC} Server management script installed"

# Create symlink for global access
if [ -w /usr/local/bin ]; then
    ln -sf ~/.claude/scripts/mageagent-server.sh /usr/local/bin/mageagent 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Global 'mageagent' command available"
elif [ -d ~/bin ]; then
    ln -sf ~/.claude/scripts/mageagent-server.sh ~/bin/mageagent 2>/dev/null || true
    echo -e "${GREEN}✓${NC} User 'mageagent' command available in ~/bin"
fi

echo ""
echo "==============================================================="
echo -e "  ${CYAN}Step 4/7:${NC} Installing Menu Bar App"
echo "==============================================================="
echo ""

if [ "$SKIP_MENUBAR" = true ]; then
    echo -e "${YELLOW}⚠${NC} Skipping menu bar app (--skip-menubar)"
else
    if [ -d "$SCRIPT_DIR/menubar-app" ]; then
        cd "$SCRIPT_DIR/menubar-app"
        if [ -f "build.sh" ]; then
            echo "Building MageAgentMenuBar.app..."
            bash build.sh
            echo -e "${GREEN}✓${NC} Menu bar app installed to /Applications"
        fi
        cd "$SCRIPT_DIR"
    else
        echo -e "${YELLOW}⚠${NC} Menu bar app source not found"
    fi
fi

echo ""
echo "==============================================================="
echo -e "  ${CYAN}Step 5/7:${NC} Claude Code Integration"
echo "==============================================================="
echo ""

if [ "$SKIP_CLAUDE_CODE" = true ]; then
    echo -e "${YELLOW}⚠${NC} Skipping Claude Code integration (--skip-claude-code)"
else
    # Install hooks
    echo "Installing Claude Code hooks..."

    # Pre-tool hook for MageAgent routing
    cat > ~/.claude/hooks/mageagent-pretool.sh << 'HOOKEOF'
#!/bin/bash
# MageAgent Pre-Tool Hook
# Automatically routes to MageAgent for certain tool calls

TOOL_NAME="$1"
TOOL_INPUT="$2"

# Log tool calls if debug enabled
if [ "$MAGEAGENT_DEBUG" = "1" ]; then
    echo "[$(date)] Tool: $TOOL_NAME" >> ~/.claude/debug/hook.log
fi

# Allow all tools by default
exit 0
HOOKEOF
    chmod +x ~/.claude/hooks/mageagent-pretool.sh
    echo -e "${GREEN}✓${NC} Pre-tool hook installed"

    # Post-response hook for logging
    cat > ~/.claude/hooks/mageagent-postresponse.sh << 'HOOKEOF'
#!/bin/bash
# MageAgent Post-Response Hook
# Logs responses for debugging

RESPONSE="$1"

if [ "$MAGEAGENT_DEBUG" = "1" ]; then
    echo "[$(date)] Response length: ${#RESPONSE}" >> ~/.claude/debug/hook.log
fi

exit 0
HOOKEOF
    chmod +x ~/.claude/hooks/mageagent-postresponse.sh
    echo -e "${GREEN}✓${NC} Post-response hook installed"

    # Install slash commands
    echo "Installing Claude Code slash commands..."

    # /mageagent command
    cat > ~/.claude/commands/mageagent.md << 'CMDEOF'
# /mageagent - MageAgent Server Control

Control the MageAgent multi-model orchestration server.

## Usage

```
/mageagent [command]
```

## Commands

- `status` - Check server status
- `start` - Start the server
- `stop` - Stop the server
- `restart` - Restart the server
- `test` - Run quick test
- `logs` - View recent logs

## Examples

```
/mageagent status
/mageagent restart
/mageagent test
```

## Implementation

When the user runs this command, execute:

```bash
~/.claude/scripts/mageagent-server.sh [command]
```

If no command specified, show status.
CMDEOF
    echo -e "${GREEN}✓${NC} /mageagent command installed"

    # /mage command (quick pattern selector)
    cat > ~/.claude/commands/mage.md << 'CMDEOF'
# /mage - Quick MageAgent Pattern Selection

Quickly switch to a MageAgent pattern.

## Usage

```
/mage [pattern]
```

## Patterns

- `auto` - Intelligent task routing (default)
- `hybrid` - 72B reasoning + Hermes-3 tools
- `validated` - Generate + validate + revise
- `compete` - Multi-model with judge
- `execute` - ReAct loop with real tool execution
- `tools` - Fast Hermes-3 tool calling
- `primary` - Direct 72B access
- `fast` - Fast 7B validator

## Examples

```
/mage hybrid
/mage execute
/mage compete
```

## Implementation

When user runs `/mage [pattern]`, switch the model:

```
/model mageagent,mageagent:[pattern]
```

If no pattern specified, use `auto`.
CMDEOF
    echo -e "${GREEN}✓${NC} /mage command installed"

    # /warmup command
    cat > ~/.claude/commands/warmup.md << 'CMDEOF'
# /warmup - Preload MageAgent Models

Preload MLX models into GPU/unified memory for faster inference.

## Usage

```
/warmup [model|all]
```

## Models

- `primary` - Qwen-72B Q8 (77GB)
- `tools` - Hermes-3 8B Q8 (9GB)
- `validator` - Qwen-Coder 7B (5GB)
- `competitor` - Qwen-Coder 32B (18GB)
- `all` - Load all models

## Examples

```
/warmup primary
/warmup all
```

## Implementation

Send a minimal request to each model to load it:

```bash
curl -X POST http://localhost:3457/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "mageagent:[model]", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 1}'
```
CMDEOF
    echo -e "${GREEN}✓${NC} /warmup command installed"

    # Update CLAUDE.md with MageAgent instructions
    if [ -f ~/.claude/CLAUDE.md ]; then
        if ! grep -q "MageAgent" ~/.claude/CLAUDE.md; then
            cat >> ~/.claude/CLAUDE.md << 'CLAUDEMD'

## MageAgent Multi-Model Orchestration

MageAgent provides intelligent multi-model AI orchestration running locally on Apple Silicon.

### Quick Commands

- `/mage hybrid` - Switch to hybrid pattern (recommended)
- `/mage execute` - Switch to execute pattern (real tool execution)
- `/mageagent status` - Check server status
- `/warmup all` - Preload all models

### Server Management

```bash
mageagent start    # Start server
mageagent stop     # Stop server
mageagent status   # Check status
mageagent test     # Run tests
```

### API Endpoint

- URL: http://localhost:3457
- Docs: http://localhost:3457/docs

### Available Patterns

| Pattern | Models | Use Case |
|---------|--------|----------|
| `auto` | Varies | Intelligent routing |
| `hybrid` | 72B + 8B | Complex reasoning + tools |
| `execute` | 72B + 8B | Real file/web access |
| `validated` | 72B + 7B | Code validation |
| `compete` | 72B + 32B + 7B | Critical code |

CLAUDEMD
            echo -e "${GREEN}✓${NC} Updated CLAUDE.md with MageAgent docs"
        fi
    fi
fi

echo ""
echo "==============================================================="
echo -e "  ${CYAN}Step 6/7:${NC} VSCode Integration"
echo "==============================================================="
echo ""

if [ "$SKIP_VSCODE" = true ]; then
    echo -e "${YELLOW}⚠${NC} Skipping VSCode integration (--skip-vscode)"
else
    # Check for VSCode
    VSCODE_DIR=""
    if [ -d "$HOME/Library/Application Support/Code/User" ]; then
        VSCODE_DIR="$HOME/Library/Application Support/Code/User"
    elif [ -d "$HOME/.config/Code/User" ]; then
        VSCODE_DIR="$HOME/.config/Code/User"
    fi

    if [ -n "$VSCODE_DIR" ]; then
        # Create/update VSCode settings
        SETTINGS_FILE="$VSCODE_DIR/settings.json"

        if [ -f "$SETTINGS_FILE" ]; then
            # Backup existing settings
            cp "$SETTINGS_FILE" "$SETTINGS_FILE.backup"
            echo -e "${GREEN}✓${NC} Backed up existing VSCode settings"
        fi

        # Create Claude Code extension settings snippet
        cat > "$VSCODE_DIR/mageagent-settings.json" << 'VSCODEJSON'
{
  "claude-code.customInstructions": "MageAgent multi-model orchestration is available at http://localhost:3457. Use /mage [pattern] to switch patterns.",
  "claude-code.hooks.preTool": "~/.claude/hooks/mageagent-pretool.sh",
  "claude-code.hooks.postResponse": "~/.claude/hooks/mageagent-postresponse.sh"
}
VSCODEJSON
        echo -e "${GREEN}✓${NC} VSCode MageAgent settings created"
        echo "  Merge $VSCODE_DIR/mageagent-settings.json into your settings.json"
    else
        echo -e "${YELLOW}⚠${NC} VSCode user directory not found"
    fi
fi

echo ""
echo "==============================================================="
echo -e "  ${CYAN}Step 7/7:${NC} Auto-Start Configuration"
echo "==============================================================="
echo ""

if [ "$SKIP_AUTOSTART" = true ]; then
    echo -e "${YELLOW}⚠${NC} Skipping auto-start (--skip-autostart)"
else
    # Server LaunchAgent
    cat > ~/Library/LaunchAgents/ai.adverant.mageagent.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.adverant.mageagent</string>
    <key>ProgramArguments</key>
    <array>
        <string>$HOME/.claude/scripts/mageagent-server.sh</string>
        <string>start</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>$HOME/.claude/debug/mageagent-launchd.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/.claude/debug/mageagent-launchd.error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
        <key>HOME</key>
        <string>$HOME</string>
    </dict>
</dict>
</plist>
EOF

    # Menu bar LaunchAgent
    if [ -d "/Applications/MageAgentMenuBar.app" ]; then
        cat > ~/Library/LaunchAgents/ai.adverant.mageagent.menubar.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.adverant.mageagent.menubar</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Applications/MageAgentMenuBar.app/Contents/MacOS/MageAgentMenuBar</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>$HOME/.claude/debug/mageagent-menubar.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/.claude/debug/mageagent-menubar.error.log</string>
</dict>
</plist>
EOF
    fi

    # Load LaunchAgents
    launchctl unload ~/Library/LaunchAgents/ai.adverant.mageagent.plist 2>/dev/null || true
    launchctl load ~/Library/LaunchAgents/ai.adverant.mageagent.plist
    echo -e "${GREEN}✓${NC} Server LaunchAgent installed"

    if [ -f ~/Library/LaunchAgents/ai.adverant.mageagent.menubar.plist ]; then
        launchctl unload ~/Library/LaunchAgents/ai.adverant.mageagent.menubar.plist 2>/dev/null || true
        launchctl load ~/Library/LaunchAgents/ai.adverant.mageagent.menubar.plist
        echo -e "${GREEN}✓${NC} Menu bar LaunchAgent installed"
    fi
fi

echo ""
echo "==============================================================="
echo -e "  ${CYAN}Downloading MLX Models${NC}"
echo "==============================================================="
echo ""

if [ "$SKIP_MODELS" = true ]; then
    echo -e "${YELLOW}⚠${NC} Skipping model download (--skip-models)"
    echo "  Models will be downloaded on first use"
else
    echo "MageAgent requires the following models (~109GB total):"
    echo ""
    echo -e "  ${BLUE}Hermes-3-Llama-3.1-8B-8bit${NC} (9GB) - Tool calling"
    echo -e "  ${BLUE}Qwen2.5-72B-Instruct-8bit${NC} (77GB) - Primary reasoning"
    echo -e "  ${BLUE}Qwen2.5-Coder-32B-Instruct-4bit${NC} (18GB) - Code generation"
    echo -e "  ${BLUE}Qwen2.5-Coder-7B-Instruct-4bit${NC} (5GB) - Fast validation"
    echo ""

    read -p "Download models now? This will take 30-60 minutes. (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "Downloading models from Hugging Face..."
        python3 << 'PYTHON'
from huggingface_hub import snapshot_download
import os

models_dir = os.path.expanduser("~/.cache/mlx-models")

models = [
    ('mlx-community/Hermes-3-Llama-3.1-8B-8bit', 'Hermes-3 8B (9GB)'),
    ('mlx-community/Qwen2.5-Coder-7B-Instruct-4bit', 'Qwen-Coder 7B (5GB)'),
    ('mlx-community/Qwen2.5-Coder-32B-Instruct-4bit', 'Qwen-Coder 32B (18GB)'),
    ('mlx-community/Qwen2.5-72B-Instruct-8bit', 'Qwen 72B (77GB)'),
]

for i, (repo, name) in enumerate(models, 1):
    print(f"{i}/{len(models)} Downloading {name}...")
    local_name = repo.split('/')[-1]
    snapshot_download(repo, local_dir=f'{models_dir}/{local_name}')
    print(f"    ✓ {name} complete")

print("\nAll models downloaded!")
PYTHON
        echo -e "${GREEN}✓${NC} All models downloaded"
    else
        echo "Skipping model download"
    fi
fi

echo ""
echo "==============================================================="
echo -e "  ${CYAN}Starting MageAgent${NC}"
echo "==============================================================="
echo ""

~/.claude/scripts/mageagent-server.sh start 2>/dev/null || true

sleep 3

# Verify installation
if curl -s http://localhost:3457/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} MageAgent server is running!"
else
    echo -e "${YELLOW}!${NC} Server may still be starting..."
    echo "  Check with: curl http://localhost:3457/health"
fi

# Open menu bar app if installed
if [ -d "/Applications/MageAgentMenuBar.app" ] && [ "$SKIP_MENUBAR" != true ]; then
    open /Applications/MageAgentMenuBar.app
    echo -e "${GREEN}✓${NC} Menu bar app launched"
fi

echo ""
echo "==============================================================="
echo -e "  ${GREEN}Installation Complete!${NC}"
echo "==============================================================="
echo ""
echo "MageAgent is now running at: ${GREEN}http://localhost:3457${NC}"
echo ""
echo -e "${BLUE}Quick Start:${NC}"
echo "  • Menu bar: Look for the Adverant icon in your menu bar"
echo "  • Terminal: mageagent status / start / stop"
echo "  • Claude Code: /mage hybrid"
echo "  • API Docs: http://localhost:3457/docs"
echo ""
echo -e "${BLUE}Available Patterns:${NC}"
echo "  • mageagent:hybrid     - Reasoning + tools (recommended)"
echo "  • mageagent:execute    - Real tool execution"
echo "  • mageagent:validated  - Generate + validate"
echo "  • mageagent:compete    - Multi-model judge"
echo "  • mageagent:auto       - Intelligent routing"
echo ""
echo -e "${BLUE}Test the Server:${NC}"
echo "  curl http://localhost:3457/health"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo "  https://github.com/adverant/nexus-local-mageagent"
echo ""
echo "==============================================================="
