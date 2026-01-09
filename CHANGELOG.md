# Changelog

All notable changes to MageAgent will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-01-09

### Added

- **Activity Monitor-Style System Pressure** (Menu Bar App)
  - Real-time memory usage display (used/total GB with percentage)
  - CPU usage percentage with color-coded pressure
  - GPU/Metal status showing loaded model count
  - Color-coded pressure indicators:
    - Green (Normal): < 75% memory, < 70% CPU
    - Yellow (Warning): 75-90% memory, 70-90% CPU
    - Red (Critical): > 90% memory or CPU
  - Updates every 2 seconds

- **Production-Grade Timeout Handling**
  - Per-model timeout configuration:
    - validator (7B): 60s
    - tools (8B): 120s
    - competitor (32B): 180s
    - primary (72B): 600s
  - `asyncio.wait_for()` wrapping for Python 3.9+ compatibility
  - Custom `GenerationTimeoutError` with descriptive messages
  - HTTP 504 responses for timeout conditions

- **Concurrency Control**
  - `asyncio.Lock()` per model type prevents concurrent Metal loads
  - Async model loading with double-check locking pattern
  - uvicorn configured with `timeout_keep_alive=700`

- **Model Pre-loading**
  - Server pre-loads validator and tools models at startup
  - Eliminates cold-start timeout issues

- **Honest Comparison Documentation**
  - Added transparency section comparing MageAgent to Claude
  - Quality metrics: 60-70% vs cloud 85-98%
  - Tool calling reliability: ~70% vs cloud ~95%
  - Clear guidance on when to use each

### Fixed

- All HTTP 500 timeout errors for multi-model patterns
- Server crashes from concurrent model loading
- Menu bar text colors now readable in both light and dark mode
- Import path issue for tool_executor module

### Changed

- Font colors use `NSColor.labelColor` for proper light/dark mode support
- Monospaced digits for memory/CPU values prevent layout jumping
- Updated version to 2.1.0

## [2.0.0] - 2026-01-09

### Added

- **Native Menu Bar App** (`MageAgentMenuBar.app`)
  - Server control (Start/Stop/Restart)
  - Model loading with checkmarks for loaded status
  - Pattern selection with auto-model loading
  - Streaming test runner with colored output
  - Toast notifications for server events
  - Settings panel with server info
  - Keyboard shortcuts for all actions

- **Real Tool Execution** (`mageagent:execute` pattern)
  - ReAct loop implementation
  - Actual file read/write operations
  - Bash command execution
  - Web search via DuckDuckGo
  - Glob and grep file searching

- **Claude Code Integration**
  - `/mage` slash command for pattern switching
  - `/mageagent` command for server control
  - `/warmup` command for model preloading
  - Pre-tool and post-response hooks
  - VSCode settings integration

- **Pattern-Based Model Loading**
  - Patterns now show required models
  - Auto-load missing models on pattern selection
  - Memory usage tracking

- **Comprehensive Installation**
  - One-command installation (`./scripts/install.sh`)
  - Multiple installation options (full, minimal, server-only)
  - LaunchAgent auto-start configuration
  - npm package with install scripts

- **Documentation**
  - Architecture diagrams (Mermaid)
  - Menu bar app documentation
  - VSCode setup guide
  - Troubleshooting guide

### Changed

- Updated package.json to version 2.0.0
- Installation script now includes all components
- Improved server health checks
- Better error handling in all patterns

### Fixed

- Menu bar button actions now work correctly (NSMenuItem target/action)
- Model loading status updates properly
- Server status display accuracy

## [1.0.0] - 2026-01-08

### Added

- Initial release of MageAgent
- Multi-model orchestration patterns:
  - `mageagent:auto` - Intelligent task routing
  - `mageagent:hybrid` - 72B + Hermes-3 combination
  - `mageagent:validated` - Generate + validate pattern
  - `mageagent:compete` - Multi-model with judge
  - `mageagent:tools` - Direct Hermes-3 access
  - `mageagent:primary` - Direct 72B access
- FastAPI server on port 3457
- OpenAI-compatible API
- MLX model pool management
- Server management script
- Claude Code router integration
- Basic documentation

### Technical Details

- Hermes-3 Q8 for reliable tool calling
- Qwen-72B Q8 for reasoning with tool support
- Qwen-32B Q4 for code generation
- Qwen-7B Q4 for fast validation

---

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| 2.1.0 | 2026-01-09 | System pressure UI, timeout fixes, honest comparison |
| 2.0.0 | 2026-01-09 | Menu bar app, real tool execution, Claude Code integration |
| 1.0.0 | 2026-01-08 | Initial release with multi-model orchestration |
