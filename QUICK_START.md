# Quick Start

**Get MageAgent running in 5 minutes.** By the end, you'll have 4 AI models working together on your Mac.

---

## What You'll Get

After this quick start:

- **MageAgent server** running on `localhost:3457`
- **Menu bar app** for one-click control
- **Claude Code integration** with `/mage` commands
- **4 orchestrated models** ready to use

---

## Prerequisites

| Requirement | Check |
|-------------|-------|
| Apple Silicon Mac | M1, M2, M3, or M4 |
| RAM | 64GB minimum (128GB recommended) |
| Storage | 120GB free |
| Python | 3.9+ (`python3 --version`) |
| macOS | 13.0+ (Ventura or later) |

---

## Option 1: One-Command Install (Recommended)

```bash
git clone https://github.com/adverant/nexus-local-mageagent.git
cd nexus-local-mageagent
./scripts/install.sh
```

The installer will:
1. Install Python dependencies
2. Build the menu bar app
3. Set up Claude Code hooks
4. Configure auto-start
5. Optionally download models (~109GB)
6. Start the server

**That's it.** Skip to [Verify Installation](#verify-installation).

---

## Option 2: npm Install

```bash
npm install -g @adverant/mageagent
npm run setup
```

---

## Option 3: Manual Install

If you prefer to understand each step:

### Step 1: Install Dependencies

```bash
pip3 install mlx mlx-lm fastapi uvicorn pydantic huggingface_hub
```

### Step 2: Clone and Set Up

```bash
git clone https://github.com/adverant/nexus-local-mageagent.git
cd nexus-local-mageagent

# Create directories
mkdir -p ~/.claude/mageagent ~/.claude/scripts ~/.claude/debug

# Copy server
cp mageagent/server.py ~/.claude/mageagent/
cp scripts/mageagent-server.sh ~/.claude/scripts/
chmod +x ~/.claude/scripts/mageagent-server.sh
```

### Step 3: Download Models

```bash
python3 << 'EOF'
from huggingface_hub import snapshot_download

# Tool calling specialist (9GB)
snapshot_download('mlx-community/Hermes-3-Llama-3.1-8B-8bit',
                  local_dir='~/.cache/mlx-models/Hermes-3-Llama-3.1-8B-8bit')

# Primary reasoning (77GB) - takes time
snapshot_download('mlx-community/Qwen2.5-72B-Instruct-8bit',
                  local_dir='~/.cache/mlx-models/Qwen2.5-72B-Instruct-8bit')

# Coding specialist (18GB)
snapshot_download('mlx-community/Qwen2.5-Coder-32B-Instruct-4bit',
                  local_dir='~/.cache/mlx-models/Qwen2.5-Coder-32B-Instruct-4bit')

# Fast validator (5GB)
snapshot_download('mlx-community/Qwen2.5-Coder-7B-Instruct-4bit',
                  local_dir='~/.cache/mlx-models/Qwen2.5-Coder-7B-Instruct-4bit')
EOF
```

### Step 4: Start Server

```bash
~/.claude/scripts/mageagent-server.sh start
```

---

## Verify Installation

### Check Server Health

```bash
curl http://localhost:3457/health
```

Expected output:
```json
{
  "status": "healthy",
  "loaded_models": ["validator"],
  "available_models": ["tools", "primary", "validator", "competitor"]
}
```

### Test a Pattern

```bash
curl -X POST http://localhost:3457/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mageagent:tools",
    "messages": [{"role": "user", "content": "What is 2+2?"}],
    "max_tokens": 100
  }'
```

You should get a response within seconds.

---

## First Use

### From Terminal

```bash
# Use the hybrid pattern (best overall)
curl -X POST http://localhost:3457/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mageagent:hybrid",
    "messages": [{"role": "user", "content": "Explain how React hooks work"}],
    "max_tokens": 1024
  }'
```

### From Claude Code

```bash
/mage hybrid          # Switch to hybrid pattern
/mage execute         # Switch to execute pattern (real tools)
/mageagent status     # Check server status
```

Or use natural language:
- "use mage for this"
- "use best local model"
- "mage this code"

### From Menu Bar

Click the MageAgent icon in your menu bar:
- **Start/Stop** the server
- **Load models** individually or all at once
- **Switch patterns** with one click
- **Run tests** to verify everything works

---

## Patterns Reference

| Pattern | What It Does | Best For |
|---------|--------------|----------|
| `mageagent:hybrid` | 72B + Hermes tools | **General use (default)** |
| `mageagent:execute` | ReAct loop with real tools | File/web/command tasks |
| `mageagent:validated` | Generate + validate + revise | Code that must work |
| `mageagent:compete` | 72B vs 32B + judge | Critical decisions |
| `mageagent:tools` | Hermes-3 only | Fast tool extraction |
| `mageagent:auto` | Smart routing | Let MageAgent decide |

---

## Troubleshooting

### Server won't start

```bash
# Check if port is in use
lsof -i :3457

# View logs
tail -50 ~/.claude/debug/mageagent.log
```

### "Model not found" error

```bash
# Verify models are downloaded
ls ~/.cache/mlx-models/

# Should show:
# Hermes-3-Llama-3.1-8B-8bit/
# Qwen2.5-72B-Instruct-8bit/
# Qwen2.5-Coder-32B-Instruct-4bit/
# Qwen2.5-Coder-7B-Instruct-4bit/
```

### Out of memory

- Close memory-heavy apps (browsers, Docker)
- Use lighter patterns: `tools` (9GB) or `auto` (5GB)
- Consider: 128GB Mac runs all patterns simultaneously

---

## Next Steps

You're running MageAgent. Now:

1. **Try the `execute` pattern** - Ask it to read a file or run a command
2. **Set up auto-start** - See [docs/AUTOSTART.md](docs/AUTOSTART.md)
3. **Configure VSCode** - See [docs/VSCODE_SETUP.md](docs/VSCODE_SETUP.md)
4. **Deep dive on patterns** - See [docs/PATTERNS.md](docs/PATTERNS.md)

---

## Getting Help

- **Logs**: `tail -f ~/.claude/debug/mageagent.log`
- **Troubleshooting**: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- **Issues**: [GitHub Issues](https://github.com/adverant/nexus-local-mageagent/issues)

---

<p align="center">
  <strong>You now have 4 AI models working together on your Mac.</strong><br>
  <em>No API costs. No data leaving your machine. Ever.</em>
</p>
