#!/usr/bin/env python3
"""
Tool Executor - Actually executes tools and returns real results

This module bridges the gap between LLM tool calls and actual execution.
Instead of hallucinating file contents, it ACTUALLY reads files.
Instead of making up command output, it ACTUALLY runs commands.
"""

import subprocess
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Execute tools and return real results - no hallucination"""

    # Dangerous commands that should never be executed
    DANGEROUS_PATTERNS = [
        "rm -rf /",
        "rm -rf /*",
        "mkfs",
        "> /dev/sda",
        "dd if=/dev/zero",
        "dd if=/dev/random",
        ":(){:|:&};:",  # Fork bomb
        "chmod -R 777 /",
        "chown -R",
        "sudo rm",
        "wget | sh",
        "curl | sh",
        "wget | bash",
        "curl | bash",
    ]

    # Maximum file size to read (50KB)
    MAX_FILE_SIZE = 50000

    # Maximum command output size (10KB)
    MAX_OUTPUT_SIZE = 10000

    # Command timeout in seconds
    COMMAND_TIMEOUT = 30

    # Maximum number of glob results
    MAX_GLOB_RESULTS = 100

    # Maximum number of grep matches
    MAX_GREP_MATCHES = 50

    def __init__(self, working_dir: Optional[str] = None):
        """Initialize with optional working directory"""
        self.working_dir = working_dir or os.getcwd()

    def execute(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single tool call and return the result.

        Args:
            tool_call: Dict with 'tool' (str) and 'arguments' (dict)

        Returns:
            Dict with result or error
        """
        tool = tool_call.get("tool", "").strip()
        args = tool_call.get("arguments", {})

        logger.info(f"Executing tool: {tool} with args: {args}")

        try:
            if tool == "Read":
                return self._read_file(args.get("file_path", ""))
            elif tool == "Write":
                return self._write_file(
                    args.get("file_path", ""),
                    args.get("content", "")
                )
            elif tool == "Edit":
                return self._edit_file(
                    args.get("file_path", ""),
                    args.get("old_string", ""),
                    args.get("new_string", "")
                )
            elif tool == "Bash":
                return self._run_bash(args.get("command", ""))
            elif tool == "Glob":
                return self._glob_files(
                    args.get("pattern", "*"),
                    args.get("path", self.working_dir)
                )
            elif tool == "Grep":
                return self._grep_search(
                    args.get("pattern", ""),
                    args.get("path", self.working_dir)
                )
            elif tool == "WebSearch":
                return self._web_search(args.get("query", ""))
            elif tool == "WebFetch":
                return self._web_fetch(
                    args.get("url", ""),
                    args.get("prompt", "Summarize this page")
                )
            else:
                return {"error": f"Unknown tool: {tool}", "available_tools": [
                    "Read", "Write", "Edit", "Bash", "Glob", "Grep", "WebSearch", "WebFetch"
                ]}
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {"error": str(e), "tool": tool}

    def _read_file(self, path: str) -> Dict[str, Any]:
        """Actually read a file from the filesystem"""
        if not path:
            return {"error": "No file path provided"}

        p = Path(path).expanduser().resolve()

        if not p.exists():
            return {"error": f"File not found: {path}"}

        if not p.is_file():
            return {"error": f"Not a file: {path}"}

        # Check file size
        size = p.stat().st_size
        if size > self.MAX_FILE_SIZE:
            return {
                "error": f"File too large ({size} bytes). Max: {self.MAX_FILE_SIZE} bytes",
                "suggestion": "Use Bash with head/tail to read portions"
            }

        try:
            content = p.read_text(encoding='utf-8')
            return {
                "content": content,
                "path": str(p),
                "size": len(content),
                "lines": content.count('\n') + 1
            }
        except UnicodeDecodeError:
            # Try reading as binary and report
            return {
                "error": "Binary file cannot be read as text",
                "path": str(p),
                "size": size
            }

    def _write_file(self, path: str, content: str) -> Dict[str, Any]:
        """Actually write content to a file"""
        if not path:
            return {"error": "No file path provided"}

        if not content:
            return {"error": "No content provided"}

        p = Path(path).expanduser().resolve()

        # Security: Don't write outside of home or working directory
        home = Path.home()
        if not (str(p).startswith(str(home)) or str(p).startswith(self.working_dir)):
            return {"error": f"Cannot write outside home directory or working directory"}

        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding='utf-8')
            return {
                "success": True,
                "path": str(p),
                "size": len(content),
                "lines": content.count('\n') + 1
            }
        except PermissionError:
            return {"error": f"Permission denied: {path}"}
        except Exception as e:
            return {"error": f"Write failed: {e}"}

    def _edit_file(self, path: str, old_string: str, new_string: str) -> Dict[str, Any]:
        """Actually edit a file by replacing text"""
        if not path:
            return {"error": "No file path provided"}

        if not old_string:
            return {"error": "No old_string provided"}

        p = Path(path).expanduser().resolve()

        if not p.exists():
            return {"error": f"File not found: {path}"}

        try:
            content = p.read_text(encoding='utf-8')

            if old_string not in content:
                return {
                    "error": "old_string not found in file",
                    "suggestion": "Check exact whitespace and characters"
                }

            # Count occurrences
            count = content.count(old_string)
            if count > 1:
                return {
                    "error": f"old_string found {count} times. Must be unique.",
                    "suggestion": "Provide more context to make it unique"
                }

            new_content = content.replace(old_string, new_string, 1)
            p.write_text(new_content, encoding='utf-8')

            return {
                "success": True,
                "path": str(p),
                "replaced": True
            }
        except Exception as e:
            return {"error": f"Edit failed: {e}"}

    def _run_bash(self, command: str) -> Dict[str, Any]:
        """Actually run a bash command"""
        if not command:
            return {"error": "No command provided"}

        # Security: Block dangerous commands
        command_lower = command.lower()
        for pattern in self.DANGEROUS_PATTERNS:
            if pattern.lower() in command_lower:
                return {
                    "error": f"Command blocked for safety: contains '{pattern}'",
                    "blocked": True
                }

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.COMMAND_TIMEOUT,
                cwd=self.working_dir,
                env={**os.environ, "HOME": str(Path.home())}
            )

            stdout = result.stdout[:self.MAX_OUTPUT_SIZE]
            stderr = result.stderr[:2000]

            truncated = len(result.stdout) > self.MAX_OUTPUT_SIZE

            return {
                "stdout": stdout,
                "stderr": stderr if stderr else None,
                "returncode": result.returncode,
                "success": result.returncode == 0,
                "truncated": truncated
            }
        except subprocess.TimeoutExpired:
            return {
                "error": f"Command timed out after {self.COMMAND_TIMEOUT} seconds",
                "timeout": True
            }
        except Exception as e:
            return {"error": f"Command failed: {e}"}

    def _glob_files(self, pattern: str, path: str) -> Dict[str, Any]:
        """Actually find files matching a pattern"""
        if not pattern:
            return {"error": "No pattern provided"}

        p = Path(path).expanduser().resolve()

        if not p.exists():
            return {"error": f"Path not found: {path}"}

        try:
            matches = list(p.glob(pattern))[:self.MAX_GLOB_RESULTS]

            files = []
            dirs = []
            for m in matches:
                if m.is_file():
                    files.append(str(m))
                elif m.is_dir():
                    dirs.append(str(m))

            return {
                "files": files,
                "directories": dirs,
                "total": len(files) + len(dirs),
                "truncated": len(list(p.glob(pattern))) > self.MAX_GLOB_RESULTS
            }
        except Exception as e:
            return {"error": f"Glob failed: {e}"}

    def _grep_search(self, pattern: str, path: str) -> Dict[str, Any]:
        """Actually search file contents"""
        if not pattern:
            return {"error": "No pattern provided"}

        p = Path(path).expanduser().resolve()

        if not p.exists():
            return {"error": f"Path not found: {path}"}

        try:
            # Use grep for efficiency
            result = subprocess.run(
                ["grep", "-r", "-n", "-l", "--include=*", pattern, str(p)],
                capture_output=True,
                text=True,
                timeout=self.COMMAND_TIMEOUT
            )

            matches = [m for m in result.stdout.strip().split("\n") if m][:self.MAX_GREP_MATCHES]

            return {
                "matches": matches,
                "count": len(matches),
                "pattern": pattern,
                "path": str(p)
            }
        except subprocess.TimeoutExpired:
            return {"error": "Search timed out", "timeout": True}
        except Exception as e:
            return {"error": f"Search failed: {e}"}

    def _web_search(self, query: str) -> Dict[str, Any]:
        """Actually search the web using DuckDuckGo (no API key needed)"""
        if not query:
            return {"error": "No query provided"}

        try:
            from duckduckgo_search import DDGS

            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))

            return {
                "results": [
                    {
                        "title": r.get("title", ""),
                        "url": r.get("href", ""),
                        "snippet": r.get("body", "")
                    }
                    for r in results
                ],
                "query": query,
                "count": len(results)
            }
        except ImportError:
            return {
                "error": "duckduckgo_search not installed",
                "fix": "pip install duckduckgo_search"
            }
        except Exception as e:
            return {"error": f"Web search failed: {e}"}

    def _web_fetch(self, url: str, prompt: str) -> Dict[str, Any]:
        """Actually fetch and process a web page"""
        if not url:
            return {"error": "No URL provided"}

        try:
            import requests
            from bs4 import BeautifulSoup

            response = requests.get(url, timeout=10, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
            })
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            text = soup.get_text(separator='\n', strip=True)

            # Truncate if too long
            if len(text) > self.MAX_FILE_SIZE:
                text = text[:self.MAX_FILE_SIZE] + "\n... [truncated]"

            return {
                "content": text,
                "url": url,
                "title": soup.title.string if soup.title else None,
                "length": len(text)
            }
        except ImportError:
            return {
                "error": "requests or beautifulsoup4 not installed",
                "fix": "pip install requests beautifulsoup4"
            }
        except Exception as e:
            return {"error": f"Web fetch failed: {e}"}


def execute_tool_calls(tool_calls: list, working_dir: Optional[str] = None) -> list:
    """
    Execute a list of tool calls and return results.

    Args:
        tool_calls: List of {"tool": str, "arguments": dict}
        working_dir: Optional working directory

    Returns:
        List of {"tool": str, "arguments": dict, "result": dict}
    """
    executor = ToolExecutor(working_dir)
    results = []

    for tc in tool_calls:
        result = executor.execute(tc)
        results.append({
            "tool": tc.get("tool"),
            "arguments": tc.get("arguments"),
            "result": result
        })

    return results


# Simple test
if __name__ == "__main__":
    executor = ToolExecutor()

    # Test file read
    print("Testing Read tool...")
    result = executor.execute({
        "tool": "Read",
        "arguments": {"file_path": "~/.zshrc"}
    })
    print(f"Read result: {result.get('size', 'error')} bytes")

    # Test bash
    print("\nTesting Bash tool...")
    result = executor.execute({
        "tool": "Bash",
        "arguments": {"command": "ls -la /tmp | head -5"}
    })
    print(f"Bash result: {result.get('stdout', result.get('error'))[:200]}")

    # Test glob
    print("\nTesting Glob tool...")
    result = executor.execute({
        "tool": "Glob",
        "arguments": {"pattern": "*.py", "path": "."}
    })
    print(f"Glob result: {result.get('total', 'error')} matches")
