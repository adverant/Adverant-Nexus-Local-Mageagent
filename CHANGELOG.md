# Changelog

All notable changes to MageAgent will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
| 2.0.0 | 2026-01-09 | Menu bar app, real tool execution, Claude Code integration |
| 1.0.0 | 2026-01-08 | Initial release with multi-model orchestration |
