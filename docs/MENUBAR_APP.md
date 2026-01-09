# MageAgent Menu Bar App

A native macOS menu bar application for managing the MageAgent multi-model AI orchestration server.

## Features

- **Server Control**: Start, stop, and restart the MageAgent server
- **Model Management**: Load individual models or all models into GPU memory
- **Pattern Selection**: Choose orchestration patterns with automatic model loading
- **Live Status**: Real-time server status and model availability
- **Test Runner**: Comprehensive test suite with streaming visual feedback
- **Quick Access**: Open API docs, view logs, and access settings

## Screenshots

### Main Menu
The menu bar icon provides quick access to all server controls:

```
┌─────────────────────────────────────────┐
│ Status: Running (v1.0.0)                │
├─────────────────────────────────────────┤
│ Start Server          ⌘S               │
│ Stop Server                             │
│ Restart Server        ⌘R               │
│ Warmup Models         ⌘W               │
├─────────────────────────────────────────┤
│ Load Models           ▸                 │
│ Patterns              ▸                 │
├─────────────────────────────────────────┤
│ Open API Docs         ⌘D               │
│ View Logs             ⌘L               │
│ Run Test              ⌘T               │
├─────────────────────────────────────────┤
│ Settings...           ⌘,               │
├─────────────────────────────────────────┤
│ Quit MageAgent Menu   ⌘Q               │
└─────────────────────────────────────────┘
```

### Load Models Submenu
Click individual models to load them into memory:

```
┌─────────────────────────────────────────────────┐
│ Click to load into memory:                      │
├─────────────────────────────────────────────────┤
│ ✓ Qwen-72B Q8 (77GB) - Reasoning               │
│ ✓ Hermes-3 8B Q8 (9GB) - Tool Calling          │
│   Qwen-Coder 7B (5GB) - Fast Validation        │
│   Qwen-Coder 32B (18GB) - Coding               │
├─────────────────────────────────────────────────┤
│ Load All Models                        ⌘W      │
└─────────────────────────────────────────────────┘
```

### Patterns Submenu
Each pattern shows its required models:

```
┌───────────────────────────────────────────────────┐
│ auto                                    ▸         │
│ execute                                 ▸         │
│ hybrid                                  ▸         │
│ validated                               ▸         │
│ compete                                 ▸         │
└───────────────────────────────────────────────────┘
         │
         ▼
┌───────────────────────────────────────────────────┐
│ Reasoning + tools - Qwen-72B for thinking,       │
│ Hermes for tool extraction                        │
├───────────────────────────────────────────────────┤
│ Required Models:                                  │
│   • Qwen-72B Q8 (77GB) - Reasoning               │
│   • Hermes-3 8B Q8 (9GB) - Tool Calling          │
├───────────────────────────────────────────────────┤
│ ✓ Use hybrid Pattern                             │
└───────────────────────────────────────────────────┘
```

### Test Results Window
Streaming test output with color-coded results:

```
┌─────────────────────────────────────────────────────┐
│ MageAgent Test Results                          ─□X│
├─────────────────────────────────────────────────────┤
│ MageAgent Test Suite                                │
│ ==================================================  │
│                                                     │
│ [1/6] Testing: Server Health Check... PASS          │
│     Status: healthy                                 │
│ [2/6] Testing: Models Endpoint... PASS              │
│     12 models available                             │
│ [3/6] Testing: Validator Model (7B)... PASS         │
│     "Test passed" (0.8s)                            │
│ [4/6] Testing: Tools Model (Hermes-3)... PASS       │
│     "test passed" (1.2s)                            │
│ [5/6] Testing: Primary Model (72B)... PASS          │
│     "Test passed." (8.4s)                           │
│ [6/6] Testing: Competitor Model (32B)... PASS       │
│     "test passed" (3.1s)                            │
│                                                     │
│ ==================================================  │
│ All tests passed!                                   │
├─────────────────────────────────────────────────────┤
│ Results: 6/6 passed                      [ Close ]  │
└─────────────────────────────────────────────────────┘
```

## Installation

### Quick Install (Recommended)

```bash
# From the nexus-local-mageagent repository
npm run install:menubar
```

### Manual Install

```bash
# 1. Build the app
cd menubar-app
./build.sh

# 2. The app is automatically installed to /Applications

# 3. (Optional) Enable auto-start on login
cp ~/Library/LaunchAgents/ai.adverant.mageagent.menubar.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/ai.adverant.mageagent.menubar.plist
```

## Requirements

- macOS 13.0 (Ventura) or later
- Apple Silicon (M1/M2/M3/M4) - required for MLX models
- MageAgent server dependencies installed

## Configuration

The menu bar app uses these configuration paths:

| Item | Path |
|------|------|
| Server Script | `~/.claude/scripts/mageagent-server.sh` |
| Server URL | `http://localhost:3457` |
| Server Log | `~/.claude/debug/mageagent.log` |
| App Debug Log | `~/.claude/debug/mageagent-menubar-debug.log` |
| Menu Bar Icon | `~/.claude/mageagent-menubar/icons/icon_18x18@2x.png` |

## Available Patterns

| Pattern | Models Required | Use Case |
|---------|-----------------|----------|
| **auto** | Validator (7B) | Intelligent task routing |
| **execute** | Primary (72B) + Tools (8B) | Real file/web/command access |
| **hybrid** | Primary (72B) + Tools (8B) | Complex reasoning + tool extraction |
| **validated** | Primary (72B) + Validator (7B) | Code that needs validation |
| **compete** | Primary (72B) + Competitor (32B) + Validator (7B) | Critical/security code |

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Start Server | ⌘S |
| Restart Server | ⌘R |
| Warmup Models | ⌘W |
| Open API Docs | ⌘D |
| View Logs | ⌘L |
| Run Tests | ⌘T |
| Settings | ⌘, |
| Quit | ⌘Q |

## Troubleshooting

### Menu bar icon not appearing
1. Check if the app is running: `pgrep MageAgentMenuBar`
2. Restart the app: `pkill MageAgentMenuBar && open /Applications/MageAgentMenuBar.app`

### Server won't start
1. Check if port is in use: `lsof -i:3457`
2. Check server logs: Click "View Logs" in menu
3. Check debug log: `tail -50 ~/.claude/debug/mageagent-menubar-debug.log`

### Models not loading
1. Ensure server is running (green status)
2. Check available memory: `top -l 1 | grep PhysMem`
3. Models require significant RAM: 72B=77GB, 32B=18GB, 8B=9GB, 7B=5GB

### Notifications not showing
The app uses system notifications with fallback to floating toast panels. If neither work:
1. Check System Settings > Notifications > MageAgentMenuBar
2. Grant notification permissions if prompted

## Development

### Building from Source

```bash
cd menubar-app

# Compile Swift code
swiftc -o build/MageAgentMenuBar.app/Contents/MacOS/MageAgentMenuBar \
    -framework Cocoa \
    -framework UserNotifications \
    -target arm64-apple-macos13.0 \
    MageAgentMenuBar/main.swift \
    MageAgentMenuBar/AppDelegate.swift

# Or use the build script
./build.sh
```

### Project Structure

```
menubar-app/
├── MageAgentMenuBar/
│   ├── main.swift              # App entry point
│   ├── AppDelegate.swift       # Main app logic
│   └── Info.plist              # App metadata
├── build/
│   └── MageAgentMenuBar.app/   # Built application
├── build.sh                    # Build script
└── Package.swift               # Swift package definition
```

### Key Classes

- **AppDelegate**: Main application delegate handling all UI and server interactions
- **ModelInfo**: Struct defining available models (id, display name, memory size)
- **PatternInfo**: Struct defining patterns (id, name, required models, description)

## License

MIT License - see main repository LICENSE file.
