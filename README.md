# Nexus Local MageAgent

> **Multi-Model AI Orchestration for Apple Silicon - Opus 4.5-level performance with local models**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Apple Silicon](https://img.shields.io/badge/Apple_Silicon-M1/M2/M3/M4-success.svg)](https://www.apple.com/mac/)
[![MLX](https://img.shields.io/badge/MLX-Native-blue.svg)](https://github.com/ml-explore/mlx)
[![Version](https://img.shields.io/badge/Version-2.0.0-blue.svg)](https://github.com/adverant/nexus-local-mageagent/releases)

## Mission

**Achieve Claude Opus 4.5-level performance using local models on Apple Silicon.**

MageAgent combines multiple specialized models through intelligent orchestration to match or exceed cloud AI quality while keeping everything private and free.

## What's New in v2.0

- **Native Menu Bar App** - Control MageAgent from your Mac menu bar
- **Real Tool Execution** - ReAct loop for actual file/web/command access
- **Streaming Test Runner** - Visual test feedback with colored results
- **Pattern-Based Model Loading** - Auto-load required models per pattern
- **Claude Code Integration** - Hooks, slash commands, VSCode support
- **One-Command Installation** - Complete setup with `./scripts/install.sh`

## Quick Start

```bash
# Clone and install
git clone https://github.com/adverant/nexus-local-mageagent.git
cd nexus-local-mageagent
./scripts/install.sh

# Or with npm
npm install -g @adverant/mageagent
npm run setup
```

That's it! MageAgent will:
1. Install Python dependencies (MLX, FastAPI)
2. Build and install the menu bar app
3. Set up Claude Code hooks and commands
4. Configure auto-start on login
5. Download MLX models (~109GB, optional)
6. Start the server

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        MageAgent System                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────────┐     ┌────────────────────┐                      │
│  │   Menu Bar App     │     │   Claude Code CLI  │                      │
│  │ MageAgentMenuBar   │     │  /mage commands    │                      │
│  └─────────┬──────────┘     └─────────┬──────────┘                      │
│            │                          │                                  │
│            └──────────┬───────────────┘                                  │
│                       ▼                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │              MageAgent Server (localhost:3457)                   │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │                                                                  │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │    │
│  │  │  auto    │ │ execute  │ │  hybrid  │ │validated │ │compete │ │    │
│  │  │ routing  │ │ ReAct    │ │ 72B+8B   │ │ 72B+7B   │ │72B+32B │ │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘ │    │
│  │                                                                  │    │
│  │  ┌─────────────────────────────────────────────────────────────┐│    │
│  │  │                    Tool Executor                            ││    │
│  │  │  Read Files │ Write Files │ Bash │ Glob │ Grep │ WebSearch ││    │
│  │  └─────────────────────────────────────────────────────────────┘│    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                       │                                                  │
│                       ▼                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                     MLX Model Pool                               │    │
│  │                                                                  │    │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────────┐  │    │
│  │  │ Qwen-72B   │ │ Qwen-32B   │ │ Qwen-7B    │ │  Hermes-3    │  │    │
│  │  │ Q8 (77GB)  │ │ Q4 (18GB)  │ │ Q4 (5GB)   │ │  Q8 (9GB)    │  │    │
│  │  │ Reasoning  │ │ Coding     │ │ Validation │ │ Tool Calling │  │    │
│  │  └────────────┘ └────────────┘ └────────────┘ └──────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Menu Bar App

The native macOS menu bar app provides easy control of MageAgent:

- **Server Control**: Start/Stop/Restart with one click
- **Model Loading**: Load individual models or all at once
- **Pattern Selection**: Choose patterns with auto-model loading
- **Live Status**: See server status and loaded models
- **Test Runner**: Streaming test results with visual feedback
- **Quick Access**: Open API docs, view logs, access settings

See [docs/MENUBAR_APP.md](docs/MENUBAR_APP.md) for full documentation.

## Orchestration Patterns

| Pattern | Models | Quality Boost | Use Case |
|---------|--------|---------------|----------|
| `auto` | Dynamic | Variable | Intelligent task routing |
| `execute` | 72B + 8B | +0% | **Real file/web/command access** |
| `hybrid` | 72B + 8B | +5% | Complex reasoning + tools |
| `validated` | 72B + 7B | +5-10% | Code with error checking |
| `compete` | 72B + 32B + 7B | +10-15% | Critical/security code |

### Execute Pattern (NEW in v2.0)

The `execute` pattern provides **real tool execution** - not simulated:

```
User: "Read ~/.zshrc and tell me what plugins are configured"

MageAgent Execute Flow:
1. Qwen-72B: "I need to read the file"
2. Hermes-3: Extracts tool call → {"tool": "Read", "path": "~/.zshrc"}
3. Tool Executor: Actually reads the file
4. Qwen-72B: "Based on the contents, you have oh-my-zsh with plugins: git, docker, kubectl..."
```

## Claude Code Integration

### Slash Commands

```bash
/mage hybrid      # Switch to hybrid pattern
/mage execute     # Switch to execute pattern (real tools)
/mage compete     # Switch to compete pattern
/mageagent status # Check server status
/warmup all       # Preload all models
```

### Natural Language

```
"use mage hybrid"
"use best local for this"
"mage this code"
"use local ai for security review"
```

### VSCode Integration

MageAgent integrates with the Claude Code VSCode extension:
- Automatic model routing
- Hook integration for tool calls
- Custom instructions for patterns

## Installation Options

### Full Installation (Recommended)

```bash
./scripts/install.sh
```

### Minimal Installation (Skip models)

```bash
./scripts/install.sh --skip-models
```

### Server Only

```bash
./scripts/install.sh --server-only
```

### npm Installation

```bash
npm install -g @adverant/mageagent
npm run install:all
```

## API Usage

### Health Check

```bash
curl http://localhost:3457/health
```

### Chat Completion

```bash
curl -X POST http://localhost:3457/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mageagent:execute",
    "messages": [{"role": "user", "content": "Read /etc/hosts and summarize"}]
  }'
```

### Available Models

```bash
curl http://localhost:3457/v1/models
```

## Requirements

- **macOS**: 13.0 (Ventura) or later
- **Chip**: Apple Silicon (M1/M2/M3/M4)
- **RAM**: 64GB minimum, 128GB+ recommended
- **Storage**: ~120GB for models + app
- **Python**: 3.9+

### Memory Requirements by Pattern

| Pattern | Minimum RAM | Models Loaded |
|---------|-------------|---------------|
| `auto` | 8GB | 7B only (routes others) |
| `execute` | 90GB | 72B + 8B |
| `hybrid` | 90GB | 72B + 8B |
| `validated` | 85GB | 72B + 7B |
| `compete` | 105GB | 72B + 32B + 7B |

## Performance

On M4 Max (128GB Unified Memory):

| Metric | Value |
|--------|-------|
| Hermes-3 Q8 | ~50 tok/s |
| Qwen-7B Q4 | ~105 tok/s |
| Qwen-32B Q4 | ~25 tok/s |
| Qwen-72B Q8 | ~8 tok/s |
| Execute pattern | 30-60s typical |
| Compete pattern | 60-120s typical |

## Quality Comparison

| Task Type | Single Model | MageAgent Pattern | Improvement |
|-----------|--------------|-------------------|-------------|
| Complex reasoning | Baseline | hybrid | +5% |
| Code generation | Baseline | validated | +5-10% |
| Security code | Baseline | compete | +10-15% |
| Tool execution | Unreliable | execute | Guaranteed |

## Documentation

- [Quick Start Guide](QUICK_START.md)
- [Menu Bar App](docs/MENUBAR_APP.md)
- [Orchestration Patterns](docs/PATTERNS.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Auto-Start Setup](docs/AUTOSTART.md)
- [VSCode Setup](docs/VSCODE_SETUP.md)
- [Architecture Diagrams](docs/diagrams/architecture.md)
- [Contributing](CONTRIBUTING.md)

## Roadmap

- [x] Multi-model orchestration
- [x] Native menu bar app
- [x] Real tool execution (ReAct)
- [x] Claude Code integration
- [x] Streaming test runner
- [ ] MCP tool server integration
- [ ] Web UI dashboard
- [ ] Ollama backend option
- [ ] Custom pattern builder
- [ ] Distributed model loading

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Links

- [Report Bug](https://github.com/adverant/nexus-local-mageagent/issues/new?template=bug_report.md)
- [Request Feature](https://github.com/adverant/nexus-local-mageagent/issues/new?template=feature_request.md)
- [Discussions](https://github.com/adverant/nexus-local-mageagent/discussions)

## Community

- **Discord**: [Join our server](https://discord.gg/adverant)
- **Twitter**: [@AdverantAI](https://twitter.com/AdverantAI)
- **Blog**: [adverant.ai/blog](https://adverant.ai/blog)

## License

MIT License - see [LICENSE](LICENSE)

## Acknowledgments

- [MLX](https://github.com/ml-explore/mlx) - Apple's ML framework
- [Qwen](https://github.com/QwenLM/Qwen2.5) - Base models from Alibaba
- [NousResearch](https://nousresearch.com/) - Hermes-3 model
- Together AI research on Mixture of Agents
- The Claude Code and Anthropic teams

---

<p align="center">
  <strong>Made with care by <a href="https://adverant.ai">Adverant</a></strong>
  <br>
  <em>Local AI orchestration for serious developers</em>
  <br><br>
  <a href="https://github.com/adverant/nexus-local-mageagent/stargazers">Star us on GitHub</a>
</p>
