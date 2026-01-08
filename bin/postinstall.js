#!/usr/bin/env node

/**
 * MageAgent Post-Install Script
 * Shows helpful information after npm install
 */

const COLORS = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  cyan: '\x1b[36m',
};

console.log(`
${COLORS.cyan}═══════════════════════════════════════════════════════════════${COLORS.reset}
${COLORS.green}  MageAgent installed successfully!${COLORS.reset}
${COLORS.cyan}═══════════════════════════════════════════════════════════════${COLORS.reset}

${COLORS.yellow}Quick Start:${COLORS.reset}

  1. Complete installation:
     ${COLORS.green}mageagent install${COLORS.reset}

  2. Download MLX models (~110GB):
     ${COLORS.green}mageagent models${COLORS.reset}

  3. Start the server:
     ${COLORS.green}mageagent start${COLORS.reset}

  4. Test it:
     ${COLORS.green}mageagent test${COLORS.reset}

${COLORS.yellow}Requirements:${COLORS.reset}
  - Apple Silicon Mac (M1/M2/M3/M4)
  - 64GB+ unified memory (128GB recommended)
  - Python 3.9+

${COLORS.yellow}Documentation:${COLORS.reset}
  https://github.com/adverant/nexus-local-mageagent

${COLORS.cyan}═══════════════════════════════════════════════════════════════${COLORS.reset}
`);
