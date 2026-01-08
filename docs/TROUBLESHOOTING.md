# Troubleshooting Guide

This guide covers common issues and their solutions when running MageAgent.

## Quick Diagnostics

Run these commands to diagnose issues:

```bash
# Check if server is running
mageagent status

# View recent logs
tail -50 ~/.claude/debug/mageagent.log

# Check error log
tail -50 ~/.claude/debug/mageagent.error.log

# Check port usage
lsof -i :3457

# Check memory
top -l 1 -o mem | head -10

# Check models exist
ls -la ~/.cache/mlx-models/
```

## Common Issues

### 1. Server Won't Start

**Symptom**: `mageagent start` fails or exits immediately

**Possible Causes & Solutions**:

#### Port already in use
```bash
# Find what's using port 3457
lsof -i :3457

# Kill the process
kill -9 <PID>

# Or kill by port
kill -9 $(lsof -t -i:3457)

# Restart
mageagent start
```

#### Python dependencies missing
```bash
# Reinstall dependencies
pip3 install --upgrade mlx mlx-lm fastapi uvicorn pydantic huggingface_hub
```

#### Server file not found
```bash
# Reinstall MageAgent
mageagent install
```

#### Permission issues
```bash
# Fix permissions
chmod +x ~/.claude/scripts/mageagent-server.sh
chmod 644 ~/.claude/mageagent/server.py
```

---

### 2. Model Not Found Errors

**Symptom**: `FileNotFoundError: Model not found at /path/to/model`

**Solution**:

```bash
# Check what models exist
ls -la ~/.cache/mlx-models/

# Download missing models
mageagent models

# Or download individually
python3 -c "
from huggingface_hub import snapshot_download
snapshot_download('mlx-community/Hermes-3-Llama-3.1-8B-8bit',
                  local_dir='$HOME/.cache/mlx-models/Hermes-3-Llama-3.1-8B-8bit')
"
```

Required models:
- `Hermes-3-Llama-3.1-8B-8bit` (9GB) - Tool calling
- `Qwen2.5-Coder-7B-Instruct-4bit` (5GB) - Validation
- `Qwen2.5-Coder-32B-Instruct-4bit` (18GB) - Coding
- `Qwen2.5-72B-Instruct-8bit` (77GB) - Primary reasoning

---

### 3. Out of Memory Errors

**Symptom**: Process killed, "Killed: 9", or memory allocation errors

**Solutions**:

1. **Close other applications**
   ```bash
   # Check memory pressure
   memory_pressure

   # See top memory consumers
   top -l 1 -o mem | head -20
   ```

2. **Use smaller patterns**
   - `mageagent:tools` - Only 9GB (Hermes-3)
   - `mageagent:validator` - Only 5GB (Qwen-7B)
   - `mageagent:competitor` - Only 18GB (Qwen-32B)
   - Avoid `mageagent:compete` which loads multiple large models

3. **Restart server to clear model cache**
   ```bash
   mageagent restart
   ```

4. **Check your system memory**
   - 64GB: Can run tools, validator, competitor
   - 128GB: Can run all patterns including hybrid and compete
   - 96GB: May struggle with compete pattern

---

### 4. Slow Responses

**Symptom**: Responses take 60+ seconds

**Causes & Solutions**:

1. **First request loads models** (normal)
   - 72B model takes 5-10 seconds to load
   - Subsequent requests are faster

2. **Use faster patterns**
   ```bash
   # Fast patterns
   mageagent:tools      # 3-5s
   mageagent:validator  # 2-3s

   # Slower patterns (use for important tasks)
   mageagent:hybrid     # 30-60s
   mageagent:validated  # 40-80s
   mageagent:compete    # 60-120s
   ```

3. **Check system load**
   ```bash
   # See if system is under load
   top -l 1

   # Check thermal throttling
   pmset -g thermlog
   ```

---

### 5. Tool Calls Not Extracted

**Symptom**: Response doesn't contain `<tool_calls>` section

**Solutions**:

1. **Verify Hermes-3 Q8 is downloaded**
   ```bash
   ls -la ~/.cache/mlx-models/Hermes-3-Llama-3.1-8B-8bit/
   ```

2. **Use hybrid pattern** (always attempts extraction)
   ```bash
   curl -X POST http://localhost:3457/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{"model": "mageagent:hybrid", "messages": [{"role": "user", "content": "Read the file at /tmp/test.txt"}]}'
   ```

3. **Check prompt contains tool keywords**
   - "read file", "write file", "execute", "run", "search", "find", "edit"
   - "tool", "function call", "glob", "grep", "bash"

---

### 6. API Connection Refused

**Symptom**: `curl: (7) Failed to connect to localhost port 3457`

**Solutions**:

1. **Check if server is running**
   ```bash
   mageagent status
   ```

2. **Start the server**
   ```bash
   mageagent start
   ```

3. **Check firewall** (rarely an issue for localhost)
   ```bash
   # Temporarily disable firewall for testing
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off
   # Remember to re-enable!
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on
   ```

---

### 7. JSON Parse Errors

**Symptom**: `json.decoder.JSONDecodeError` in logs

**Cause**: Model output not properly formatted

**Solutions**:

1. **Lower temperature**
   ```bash
   curl -X POST http://localhost:3457/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{
       "model": "mageagent:tools",
       "messages": [...],
       "temperature": 0.3
     }'
   ```

2. **Restart server** (may have corrupted state)
   ```bash
   mageagent restart
   ```

---

### 8. Import Errors

**Symptom**: `ModuleNotFoundError: No module named 'mlx'`

**Solution**:
```bash
# Make sure you're using the right Python
which python3
# Should be: /usr/bin/python3 or /opt/homebrew/bin/python3

# Reinstall packages
pip3 install --upgrade mlx mlx-lm fastapi uvicorn pydantic

# If using pyenv or conda, make sure the right env is active
```

---

### 9. LaunchAgent Issues

**Symptom**: Server doesn't auto-start on boot

**Solutions**:

1. **Check plist syntax**
   ```bash
   plutil -lint ~/Library/LaunchAgents/com.adverant.mageagent.plist
   ```

2. **Reload LaunchAgent**
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.adverant.mageagent.plist
   launchctl load ~/Library/LaunchAgents/com.adverant.mageagent.plist
   ```

3. **Check system logs**
   ```bash
   log show --predicate 'subsystem == "com.apple.launchd"' --last 5m | grep mageagent
   ```

---

### 10. Claude Code Router Issues

**Symptom**: `/model mageagent,mageagent:hybrid` doesn't work

**Solutions**:

1. **Check router config**
   ```bash
   cat ~/.claude-code-router/config.json
   ```

   Should include:
   ```json
   {
     "providers": [
       {
         "name": "mageagent",
         "api_base_url": "http://localhost:3457/v1/chat/completions",
         "api_key": "local",
         "models": ["mageagent:hybrid", ...]
       }
     ]
   }
   ```

2. **Restart Claude Code Router**
   ```bash
   ccr restart
   ```

3. **Verify MageAgent is responding**
   ```bash
   curl http://localhost:3457/health
   ```

---

## Getting More Help

### Collect Debug Information

Before reporting an issue, collect this info:

```bash
# System info
uname -a
sysctl -n machdep.cpu.brand_string
sysctl -n hw.memsize | awk '{print $0/1024/1024/1024 " GB"}'

# MageAgent version
cat ~/.claude/mageagent/server.py | grep "version"

# Python version
python3 --version

# Installed packages
pip3 list | grep -E "(mlx|fastapi|uvicorn|pydantic)"

# Server status
mageagent status

# Recent logs
tail -100 ~/.claude/debug/mageagent.log
tail -100 ~/.claude/debug/mageagent.error.log
```

### Report Issues

Open an issue at: https://github.com/adverant/nexus-local-mageagent/issues

Include:
1. System information (from above)
2. Steps to reproduce
3. Expected vs actual behavior
4. Relevant log output

---

*Made with care by [Adverant](https://github.com/adverant)*
