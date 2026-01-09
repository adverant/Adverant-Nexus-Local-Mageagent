#!/usr/bin/env node

/**
 * MageAgent CLI
 * Multi-Model AI Orchestration for Apple Silicon
 */

import { spawn, execSync } from 'child_process';
import { existsSync, mkdirSync, copyFileSync, chmodSync } from 'fs';
import { homedir } from 'os';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const packageRoot = join(__dirname, '..');

const CLAUDE_DIR = join(homedir(), '.claude');
const MAGEAGENT_DIR = join(CLAUDE_DIR, 'mageagent');
const SCRIPTS_DIR = join(CLAUDE_DIR, 'scripts');
const DEBUG_DIR = join(CLAUDE_DIR, 'debug');
const MODELS_DIR = join(homedir(), '.cache', 'mlx-models');
const SERVER_SCRIPT = join(SCRIPTS_DIR, 'mageagent-server.sh');

const COLORS = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

function log(message, color = 'reset') {
  console.log(`${COLORS[color]}${message}${COLORS.reset}`);
}

function checkAppleSilicon() {
  try {
    const arch = execSync('uname -m').toString().trim();
    if (arch !== 'arm64') {
      log('Error: MageAgent requires Apple Silicon (M1/M2/M3/M4)', 'red');
      process.exit(1);
    }
  } catch (e) {
    log('Error: Could not detect system architecture', 'red');
    process.exit(1);
  }
}

function checkPython() {
  try {
    execSync('python3 --version', { stdio: 'pipe' });
    return true;
  } catch (e) {
    log('Error: Python 3 is required but not installed', 'red');
    log('Install from: https://www.python.org/', 'yellow');
    return false;
  }
}

function ensureDirectories() {
  [CLAUDE_DIR, MAGEAGENT_DIR, SCRIPTS_DIR, DEBUG_DIR, MODELS_DIR].forEach(dir => {
    if (!existsSync(dir)) {
      mkdirSync(dir, { recursive: true });
      log(`Created: ${dir}`, 'green');
    }
  });
}

function copyServerFiles() {
  const serverSrc = join(packageRoot, 'mageagent', 'server.py');
  const serverDst = join(MAGEAGENT_DIR, 'server.py');

  const scriptSrc = join(packageRoot, 'scripts', 'mageagent-server.sh');
  const scriptDst = SERVER_SCRIPT;

  if (existsSync(serverSrc)) {
    copyFileSync(serverSrc, serverDst);
    log(`Installed: ${serverDst}`, 'green');
  }

  if (existsSync(scriptSrc)) {
    copyFileSync(scriptSrc, scriptDst);
    chmodSync(scriptDst, '755');
    log(`Installed: ${scriptDst}`, 'green');
  }
}

function installPythonDeps() {
  log('\nInstalling Python dependencies...', 'cyan');
  try {
    execSync('pip3 install --quiet mlx mlx-lm fastapi uvicorn pydantic huggingface_hub', {
      stdio: 'inherit'
    });
    log('Python dependencies installed', 'green');
    return true;
  } catch (e) {
    log('Failed to install Python dependencies', 'red');
    return false;
  }
}

function runServerCommand(command) {
  if (!existsSync(SERVER_SCRIPT)) {
    log('Error: MageAgent not installed. Run: mageagent install', 'red');
    process.exit(1);
  }

  const child = spawn(SERVER_SCRIPT, [command], {
    stdio: 'inherit',
    shell: true
  });

  child.on('close', (code) => {
    process.exit(code);
  });
}

function downloadModels() {
  log('\nDownloading MLX models (~110GB total)...', 'cyan');
  log('This will take 30-60 minutes depending on your connection.\n', 'yellow');

  const models = [
    { name: 'Hermes-3-Llama-3.1-8B-8bit', size: '9GB', role: 'Tool calling' },
    { name: 'Qwen2.5-Coder-7B-Instruct-4bit', size: '5GB', role: 'Validation' },
    { name: 'Qwen2.5-Coder-32B-Instruct-4bit', size: '18GB', role: 'Code generation' },
    { name: 'Qwen2.5-72B-Instruct-8bit', size: '77GB', role: 'Primary reasoning' },
  ];

  for (const model of models) {
    const modelPath = join(MODELS_DIR, model.name);
    if (existsSync(modelPath)) {
      log(`Skipping ${model.name} (already exists)`, 'yellow');
      continue;
    }

    log(`Downloading ${model.name} (${model.size}) - ${model.role}...`, 'blue');

    try {
      execSync(`python3 -c "
from huggingface_hub import snapshot_download
snapshot_download('mlx-community/${model.name}', local_dir='${modelPath}')
"`, { stdio: 'inherit' });
      log(`Downloaded: ${model.name}`, 'green');
    } catch (e) {
      log(`Failed to download ${model.name}`, 'red');
    }
  }
}

function showHelp() {
  console.log(`
${COLORS.cyan}MageAgent - Multi-Model AI Orchestration for Apple Silicon${COLORS.reset}

${COLORS.yellow}Usage:${COLORS.reset}
  mageagent <command>

${COLORS.yellow}Commands:${COLORS.reset}
  setup       Complete setup (install + start + launch menu bar)
  install     Install MageAgent server and dependencies
  start       Start the MageAgent server
  stop        Stop the MageAgent server
  restart     Restart the MageAgent server
  status      Check server status
  logs        View server logs
  models      Download required MLX models
  test        Test the API endpoint
  help        Show this help message

${COLORS.yellow}Quick Start:${COLORS.reset}
  npm install -g mageagent-local && mageagent setup

${COLORS.yellow}Examples:${COLORS.reset}
  mageagent setup      # Complete first-time setup (recommended)
  mageagent start      # Start server on port 3457
  mageagent status     # Check if running

${COLORS.yellow}After installation:${COLORS.reset}
  curl http://localhost:3457/health

${COLORS.yellow}More info:${COLORS.reset}
  https://github.com/adverant/nexus-local-mageagent
`);
}

function testApi() {
  log('\nTesting MageAgent API...', 'cyan');
  try {
    const result = execSync('curl -s http://localhost:3457/health').toString();
    const health = JSON.parse(result);
    log('\nServer Status: ' + health.status, 'green');
    log('Loaded Models: ' + health.loaded_models.join(', '), 'blue');
    log('Available Models: ' + health.available_models.join(', '), 'blue');
  } catch (e) {
    log('Error: Could not connect to MageAgent server', 'red');
    log('Make sure the server is running: mageagent start', 'yellow');
    process.exit(1);
  }
}

function installLaunchAgents() {
  const launchAgentsDir = join(homedir(), 'Library', 'LaunchAgents');

  // Server LaunchAgent
  const serverPlist = `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.adverant.mageagent</string>
    <key>ProgramArguments</key>
    <array>
        <string>${SERVER_SCRIPT}</string>
        <string>start</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>${DEBUG_DIR}/mageagent-launchd.log</string>
    <key>StandardErrorPath</key>
    <string>${DEBUG_DIR}/mageagent-launchd.error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
        <key>HOME</key>
        <string>${homedir()}</string>
    </dict>
</dict>
</plist>`;

  // Menu Bar LaunchAgent
  const menubarPlist = `<?xml version="1.0" encoding="UTF-8"?>
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
    <string>${DEBUG_DIR}/mageagent-menubar.log</string>
    <key>StandardErrorPath</key>
    <string>${DEBUG_DIR}/mageagent-menubar.error.log</string>
</dict>
</plist>`;

  // Write plists
  const serverPlistPath = join(launchAgentsDir, 'ai.adverant.mageagent.plist');
  const menubarPlistPath = join(launchAgentsDir, 'ai.adverant.mageagent.menubar.plist');

  require('fs').writeFileSync(serverPlistPath, serverPlist);
  log('Installed server LaunchAgent (auto-start on boot)', 'green');

  if (existsSync('/Applications/MageAgentMenuBar.app')) {
    require('fs').writeFileSync(menubarPlistPath, menubarPlist);
    log('Installed menu bar LaunchAgent (auto-start on boot)', 'green');

    // Load LaunchAgents
    try {
      execSync(`launchctl unload "${serverPlistPath}" 2>/dev/null || true`, { stdio: 'ignore' });
      execSync(`launchctl load "${serverPlistPath}"`, { stdio: 'ignore' });
      execSync(`launchctl unload "${menubarPlistPath}" 2>/dev/null || true`, { stdio: 'ignore' });
      execSync(`launchctl load "${menubarPlistPath}"`, { stdio: 'ignore' });
    } catch (e) {
      // Ignore errors
    }
  }
}

function launchMenuBar() {
  if (existsSync('/Applications/MageAgentMenuBar.app')) {
    try {
      execSync('open /Applications/MageAgentMenuBar.app', { stdio: 'ignore' });
      log('Menu bar app launched', 'green');
    } catch (e) {
      log('Could not launch menu bar app', 'yellow');
    }
  }
}

function fullSetup() {
  log('\n=== MageAgent Complete Setup ===\n', 'cyan');
  checkAppleSilicon();
  if (!checkPython()) process.exit(1);
  ensureDirectories();
  copyServerFiles();
  installPythonDeps();
  installLaunchAgents();

  // Start server
  log('\nStarting MageAgent server...', 'cyan');
  try {
    execSync(`${SERVER_SCRIPT} start`, { stdio: 'inherit' });
  } catch (e) {
    // Ignore - might already be running
  }

  // Wait for server
  setTimeout(() => {
    // Launch menu bar app
    launchMenuBar();

    log('\n=== Setup Complete! ===\n', 'green');
    log('MageAgent server: http://localhost:3457', 'blue');
    log('Menu bar icon should appear in your menu bar.', 'blue');
    log('Both server and menu bar will auto-start on boot.\n', 'blue');
    log('Next: Download models (~110GB) via menu: Load Models > Load All', 'yellow');
  }, 2000);
}

// Main CLI
const command = process.argv[2] || 'help';

switch (command) {
  case 'setup':
    fullSetup();
    break;

  case 'install':
    log('\n=== MageAgent Installation ===\n', 'cyan');
    checkAppleSilicon();
    if (!checkPython()) process.exit(1);
    ensureDirectories();
    copyServerFiles();
    installPythonDeps();
    installLaunchAgents();
    log('\nInstallation complete!', 'green');
    log('\nNext steps:', 'yellow');
    log('  1. Download models: mageagent models', 'reset');
    log('  2. Start server:    mageagent start', 'reset');
    log('  3. Test:            mageagent test\n', 'reset');
    break;

  case 'models':
    checkAppleSilicon();
    downloadModels();
    break;

  case 'start':
    runServerCommand('start');
    break;

  case 'stop':
    runServerCommand('stop');
    break;

  case 'restart':
    runServerCommand('restart');
    break;

  case 'status':
    runServerCommand('status');
    break;

  case 'logs':
    runServerCommand('logs');
    break;

  case 'test':
    testApi();
    break;

  case 'help':
  case '--help':
  case '-h':
    showHelp();
    break;

  default:
    log(`Unknown command: ${command}`, 'red');
    showHelp();
    process.exit(1);
}
