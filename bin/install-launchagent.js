#!/usr/bin/env node

/**
 * MageAgent LaunchAgent Installer
 * Installs both server and menu bar app LaunchAgents for auto-start on login
 */

import { existsSync, mkdirSync, writeFileSync, copyFileSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';
import { execSync } from 'child_process';

const HOME = homedir();
const LAUNCH_AGENTS_DIR = join(HOME, 'Library', 'LaunchAgents');
const CLAUDE_DIR = join(HOME, '.claude');
const SCRIPTS_DIR = join(CLAUDE_DIR, 'scripts');
const DEBUG_DIR = join(CLAUDE_DIR, 'debug');

// Ensure directories exist
[LAUNCH_AGENTS_DIR, SCRIPTS_DIR, DEBUG_DIR].forEach(dir => {
    if (!existsSync(dir)) {
        mkdirSync(dir, { recursive: true });
        console.log(`Created directory: ${dir}`);
    }
});

// Server LaunchAgent plist
const serverPlist = `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.adverant.mageagent</string>

    <key>ProgramArguments</key>
    <array>
        <string>${SCRIPTS_DIR}/mageagent-server.sh</string>
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
        <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>HOME</key>
        <string>${HOME}</string>
    </dict>
</dict>
</plist>
`;

// Menu Bar App LaunchAgent plist
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
</plist>
`;

// Install server LaunchAgent
const serverPlistPath = join(LAUNCH_AGENTS_DIR, 'ai.adverant.mageagent.plist');
writeFileSync(serverPlistPath, serverPlist);
console.log(`✓ Installed server LaunchAgent: ${serverPlistPath}`);

// Install menu bar LaunchAgent (only if app exists)
const menubarAppPath = '/Applications/MageAgentMenuBar.app';
const menubarPlistPath = join(LAUNCH_AGENTS_DIR, 'ai.adverant.mageagent.menubar.plist');

if (existsSync(menubarAppPath)) {
    writeFileSync(menubarPlistPath, menubarPlist);
    console.log(`✓ Installed menu bar LaunchAgent: ${menubarPlistPath}`);
} else {
    console.log(`⚠ Menu bar app not found at ${menubarAppPath}`);
    console.log('  Run "npm run install:menubar" first');
}

// Load the LaunchAgents
console.log('\nLoading LaunchAgents...');

try {
    // Unload first to avoid errors
    execSync(`launchctl unload "${serverPlistPath}" 2>/dev/null || true`, { stdio: 'ignore' });
    execSync(`launchctl load "${serverPlistPath}"`, { stdio: 'inherit' });
    console.log('✓ Server LaunchAgent loaded');
} catch (e) {
    console.error('⚠ Failed to load server LaunchAgent:', e.message);
}

if (existsSync(menubarAppPath)) {
    try {
        execSync(`launchctl unload "${menubarPlistPath}" 2>/dev/null || true`, { stdio: 'ignore' });
        execSync(`launchctl load "${menubarPlistPath}"`, { stdio: 'inherit' });
        console.log('✓ Menu bar LaunchAgent loaded');
    } catch (e) {
        console.error('⚠ Failed to load menu bar LaunchAgent:', e.message);
    }
}

console.log('\n✅ LaunchAgent installation complete!');
console.log('\nMageAgent will now start automatically on login.');
console.log('\nTo manage LaunchAgents:');
console.log('  launchctl list | grep mageagent    # Check status');
console.log('  npm run uninstall:launchagent      # Disable auto-start');
