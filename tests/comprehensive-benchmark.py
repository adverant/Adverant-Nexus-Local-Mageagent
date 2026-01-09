#!/usr/bin/env python3
"""
MageAgent Comprehensive Benchmark
Tests ALL patterns including Anthropic models (Opus 4.5, Sonnet 4.5)
Covers: Tool Use, Deep Thinking, Filesystem Access, Web Search, Complex Reasoning

Run with: python3 tests/comprehensive-benchmark.py
"""

import requests
import json
import time
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

# ============================================================================
# CONFIGURATION
# ============================================================================

MAGEAGENT_URL = "http://localhost:3457/v1/chat/completions"
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"

# All models to benchmark
MODELS = {
    # MageAgent Local Patterns
    "mageagent:validator": {"type": "mageagent", "description": "Fast 7B - Quick validation"},
    "mageagent:primary": {"type": "mageagent", "description": "72B Q8 - Deep reasoning"},
    "mageagent:tools": {"type": "mageagent", "description": "Hermes-3 8B - Tool calling"},
    "mageagent:hybrid": {"type": "mageagent", "description": "72B + Hermes - Best combo"},
    "mageagent:validated": {"type": "mageagent", "description": "Generate + Validate loop"},
    "mageagent:compete": {"type": "mageagent", "description": "Multi-model with judge"},
    "mageagent:execute": {"type": "mageagent", "description": "ReAct with real tool execution"},

    # Anthropic Cloud Models
    "claude-opus-4-5-20251101": {"type": "anthropic", "description": "Claude Opus 4.5 - Highest quality"},
    "claude-sonnet-4-5-20250929": {"type": "anthropic", "description": "Claude Sonnet 4.5 - Balanced"},
}

# ============================================================================
# TEST CASES - 25+ Complex Real-World Scenarios
# ============================================================================

TEST_CASES = [
    # ========== FILESYSTEM ACCESS TESTS ==========
    {
        "id": 1,
        "category": "Filesystem",
        "name": "Read Project Structure",
        "prompt": "Read the file /Users/don/Adverant/nexus-local-mageagent/package.json and tell me what the project name and version are.",
        "requires": ["filesystem"],
        "validation": lambda r: "mageagent" in r.lower() and ("2.0" in r or "version" in r.lower())
    },
    {
        "id": 2,
        "category": "Filesystem",
        "name": "Count Python Files",
        "prompt": "How many Python files are in /Users/don/Adverant/nexus-local-mageagent/mageagent/ directory? List them.",
        "requires": ["filesystem"],
        "validation": lambda r: ".py" in r and ("server.py" in r or "tool_executor" in r)
    },
    {
        "id": 3,
        "category": "Filesystem",
        "name": "Analyze Code File",
        "prompt": "Read /Users/don/Adverant/nexus-local-mageagent/mageagent/server.py and tell me what FastAPI endpoints are defined. List the route paths.",
        "requires": ["filesystem"],
        "validation": lambda r: "/health" in r or "/v1/chat" in r or "endpoint" in r.lower()
    },
    {
        "id": 4,
        "category": "Filesystem",
        "name": "Find Pattern in Files",
        "prompt": "Search for files containing 'MLX' in /Users/don/Adverant/nexus-local-mageagent/ and list where it appears.",
        "requires": ["filesystem"],
        "validation": lambda r: "mlx" in r.lower() and ("server" in r.lower() or "readme" in r.lower())
    },
    {
        "id": 5,
        "category": "Filesystem",
        "name": "Directory Comparison",
        "prompt": "Compare the contents of /Users/don/Adverant/nexus-local-mageagent/scripts/ and /Users/don/Adverant/nexus-local-mageagent/bin/ directories. What files are in each?",
        "requires": ["filesystem"],
        "validation": lambda r: ("script" in r.lower() or ".sh" in r) and (".js" in r or "bin" in r.lower())
    },

    # ========== TOOL USE / FUNCTION CALLING TESTS ==========
    {
        "id": 6,
        "category": "Tool Use",
        "name": "Multi-Step File Analysis",
        "prompt": "First, read the README.md in /Users/don/Adverant/nexus-local-mageagent/, then find all mentions of 'pattern' or 'model' and summarize the different orchestration patterns available.",
        "requires": ["filesystem", "tool_calling"],
        "validation": lambda r: "hybrid" in r.lower() or "validated" in r.lower() or "compete" in r.lower()
    },
    {
        "id": 7,
        "category": "Tool Use",
        "name": "Bash Command Execution",
        "prompt": "Run 'uname -a' and tell me what operating system and architecture this machine is running.",
        "requires": ["bash"],
        "validation": lambda r: "darwin" in r.lower() or "arm64" in r.lower() or "macos" in r.lower()
    },
    {
        "id": 8,
        "category": "Tool Use",
        "name": "Git Status Check",
        "prompt": "Check the git status of /Users/don/Adverant/nexus-local-mageagent/ and tell me if there are any uncommitted changes.",
        "requires": ["bash", "git"],
        "validation": lambda r: "modified" in r.lower() or "clean" in r.lower() or "changes" in r.lower() or "commit" in r.lower()
    },
    {
        "id": 9,
        "category": "Tool Use",
        "name": "Process Discovery",
        "prompt": "Find all running Python processes on this system using ps or similar commands. How many are there?",
        "requires": ["bash"],
        "validation": lambda r: "python" in r.lower() and any(c.isdigit() for c in r)
    },
    {
        "id": 10,
        "category": "Tool Use",
        "name": "Environment Analysis",
        "prompt": "What is the current PATH environment variable? List the first 5 directories.",
        "requires": ["bash"],
        "validation": lambda r: "/usr" in r or "/bin" in r or "homebrew" in r.lower() or "path" in r.lower()
    },

    # ========== DEEP THINKING / REASONING TESTS ==========
    {
        "id": 11,
        "category": "Reasoning",
        "name": "Algorithm Design",
        "prompt": "Design a distributed consensus algorithm for a 5-node cluster that can tolerate 2 node failures. Explain the phases, message types, and prove why it's correct.",
        "requires": ["reasoning"],
        "validation": lambda r: ("leader" in r.lower() or "vote" in r.lower() or "quorum" in r.lower()) and len(r) > 500
    },
    {
        "id": 12,
        "category": "Reasoning",
        "name": "System Architecture",
        "prompt": "Design a real-time collaborative document editing system like Google Docs. Address: conflict resolution, operational transforms vs CRDTs, scalability, and offline support. Provide detailed technical decisions.",
        "requires": ["reasoning"],
        "validation": lambda r: ("crdt" in r.lower() or "operational transform" in r.lower() or "conflict" in r.lower()) and len(r) > 800
    },
    {
        "id": 13,
        "category": "Reasoning",
        "name": "Performance Analysis",
        "prompt": "Given a PostgreSQL database with 100M rows and slow queries taking 30+ seconds, walk me through a systematic debugging process. What tools would you use? What are the likely causes? How would you fix them?",
        "requires": ["reasoning"],
        "validation": lambda r: ("index" in r.lower() or "explain" in r.lower() or "vacuum" in r.lower()) and len(r) > 600
    },
    {
        "id": 14,
        "category": "Reasoning",
        "name": "Security Threat Model",
        "prompt": "Perform a threat modeling exercise for a mobile banking application. Identify at least 10 potential threats using STRIDE methodology, their likelihood, impact, and mitigations.",
        "requires": ["reasoning"],
        "validation": lambda r: ("stride" in r.lower() or "spoofing" in r.lower() or "tampering" in r.lower()) and len(r) > 700
    },
    {
        "id": 15,
        "category": "Reasoning",
        "name": "Mathematical Proof",
        "prompt": "Prove that the sum of the first n odd numbers equals n². Provide a formal proof by induction and also an intuitive geometric explanation.",
        "requires": ["reasoning"],
        "validation": lambda r: ("induction" in r.lower() or "base case" in r.lower()) and ("n²" in r or "n^2" in r or "n*n" in r)
    },

    # ========== CODE GENERATION TESTS ==========
    {
        "id": 16,
        "category": "Code",
        "name": "Full Stack Component",
        "prompt": "Create a complete React + TypeScript component for a data table with sorting, filtering, pagination, and row selection. Include proper types, hooks, and CSS-in-JS styling.",
        "requires": ["code_gen"],
        "validation": lambda r: "useState" in r and "interface" in r and ("table" in r.lower() or "column" in r.lower())
    },
    {
        "id": 17,
        "category": "Code",
        "name": "API Implementation",
        "prompt": "Implement a RESTful API in Python FastAPI for a TODO app with CRUD operations, authentication, rate limiting, and proper error handling. Include Pydantic models and async database operations.",
        "requires": ["code_gen"],
        "validation": lambda r: "FastAPI" in r and ("async def" in r or "Depends" in r) and "pydantic" in r.lower()
    },
    {
        "id": 18,
        "category": "Code",
        "name": "Rust System Tool",
        "prompt": "Write a Rust CLI tool that monitors file system changes in a directory and triggers a callback. Use proper error handling with Result types, async with tokio, and provide colored output.",
        "requires": ["code_gen"],
        "validation": lambda r: "tokio" in r.lower() and ("Result" in r or "async fn" in r) and "notify" in r.lower()
    },
    {
        "id": 19,
        "category": "Code",
        "name": "Kubernetes Manifest",
        "prompt": "Create a complete Kubernetes deployment for a microservice with: Deployment, Service, ConfigMap, Secret, HPA, PDB, NetworkPolicy, and Ingress. Include resource limits and health checks.",
        "requires": ["code_gen"],
        "validation": lambda r: "apiVersion" in r and "Deployment" in r and ("livenessProbe" in r or "readinessProbe" in r)
    },
    {
        "id": 20,
        "category": "Code",
        "name": "Database Migration",
        "prompt": "Write a database migration system in Go that supports up/down migrations, version tracking, transaction safety, and dry-run mode. Include proper CLI interface.",
        "requires": ["code_gen"],
        "validation": lambda r: "func " in r and ("migrate" in r.lower() or "version" in r.lower()) and "sql" in r.lower()
    },

    # ========== WEB SEARCH / KNOWLEDGE TESTS ==========
    {
        "id": 21,
        "category": "Knowledge",
        "name": "Current Technology",
        "prompt": "What is the current stable version of Python and what are the key features introduced in the latest release?",
        "requires": ["knowledge"],
        "validation": lambda r: "python" in r.lower() and ("3.1" in r or "3.2" in r or "feature" in r.lower())
    },
    {
        "id": 22,
        "category": "Knowledge",
        "name": "Framework Comparison",
        "prompt": "Compare React, Vue, and Svelte for building a large-scale enterprise application. Consider bundle size, learning curve, ecosystem, and performance. Give a recommendation with justification.",
        "requires": ["knowledge"],
        "validation": lambda r: "react" in r.lower() and "vue" in r.lower() and len(r) > 500
    },
    {
        "id": 23,
        "category": "Knowledge",
        "name": "Best Practices",
        "prompt": "What are the current best practices for securing a REST API in 2025? Include authentication, authorization, rate limiting, input validation, and monitoring.",
        "requires": ["knowledge"],
        "validation": lambda r: ("jwt" in r.lower() or "oauth" in r.lower() or "authentication" in r.lower()) and len(r) > 400
    },

    # ========== COMPLEX MULTI-STEP TASKS ==========
    {
        "id": 24,
        "category": "Complex",
        "name": "Codebase Analysis",
        "prompt": "Analyze the /Users/don/Adverant/nexus-local-mageagent/ codebase and provide: 1) A high-level architecture overview, 2) The main entry points, 3) Key dependencies, 4) Suggestions for improvement.",
        "requires": ["filesystem", "reasoning"],
        "validation": lambda r: ("server" in r.lower() or "architecture" in r.lower()) and len(r) > 600
    },
    {
        "id": 25,
        "category": "Complex",
        "name": "Bug Investigation",
        "prompt": "The MageAgent server occasionally returns slow responses. Read the server.py file, identify potential performance bottlenecks, and suggest specific code changes to improve performance.",
        "requires": ["filesystem", "reasoning", "code_gen"],
        "validation": lambda r: ("async" in r.lower() or "cache" in r.lower() or "performance" in r.lower()) and len(r) > 500
    },
]

# ============================================================================
# API CLIENTS
# ============================================================================

def call_mageagent(model: str, prompt: str, timeout: int = 300) -> dict:
    """Call MageAgent local API"""
    try:
        response = requests.post(
            MAGEAGENT_URL,
            headers={"Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 4096,
                "temperature": 0.7
            },
            timeout=timeout
        )
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "success",
                "content": data["choices"][0]["message"]["content"],
                "usage": data.get("usage", {})
            }
        else:
            return {"status": "error", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def call_anthropic(model: str, prompt: str, timeout: int = 300) -> dict:
    """Call Anthropic API directly"""
    if not ANTHROPIC_API_KEY:
        return {"status": "error", "error": "ANTHROPIC_API_KEY not set"}

    try:
        response = requests.post(
            ANTHROPIC_URL,
            headers={
                "Content-Type": "application/json",
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": model,
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=timeout
        )
        if response.status_code == 200:
            data = response.json()
            content = data["content"][0]["text"] if data.get("content") else ""
            return {
                "status": "success",
                "content": content,
                "usage": data.get("usage", {})
            }
        else:
            return {"status": "error", "error": f"HTTP {response.status_code}: {response.text[:200]}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def call_model(model_name: str, prompt: str, timeout: int = 300) -> dict:
    """Route to appropriate API based on model type"""
    model_info = MODELS.get(model_name, {})
    model_type = model_info.get("type", "mageagent")

    start_time = time.time()

    if model_type == "anthropic":
        result = call_anthropic(model_name, prompt, timeout)
    else:
        result = call_mageagent(model_name, prompt, timeout)

    result["elapsed_seconds"] = round(time.time() - start_time, 2)
    return result

# ============================================================================
# BENCHMARK RUNNER
# ============================================================================

def run_single_test(model: str, test: dict, timeout: int = 300) -> dict:
    """Run a single test case"""
    result = call_model(model, test["prompt"], timeout)

    if result["status"] == "success":
        content = result["content"]
        # Run validation if provided
        try:
            passed = test.get("validation", lambda x: True)(content)
        except:
            passed = False

        result["validation_passed"] = passed
        result["content_length"] = len(content)
        result["content_preview"] = content[:800] + "..." if len(content) > 800 else content
    else:
        result["validation_passed"] = False

    return result

def run_benchmark(models: list = None, test_ids: list = None, timeout: int = 300):
    """Run full benchmark"""
    models = models or list(MODELS.keys())
    tests = TEST_CASES if not test_ids else [t for t in TEST_CASES if t["id"] in test_ids]

    print(f"\n{'='*100}")
    print(f"MageAgent Comprehensive Benchmark")
    print(f"Models: {len(models)} | Tests: {len(tests)} | Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*100}\n")

    all_results = {}

    for model in models:
        model_info = MODELS.get(model, {})
        print(f"\n{'─'*100}")
        print(f"MODEL: {model}")
        print(f"Type: {model_info.get('type', 'unknown')} | {model_info.get('description', '')}")
        print(f"{'─'*100}\n")

        model_results = []

        for test in tests:
            print(f"  [{test['id']:2d}] {test['category']:12s} | {test['name'][:35]:35s} | ", end="", flush=True)

            result = run_single_test(model, test, timeout)
            result["test_id"] = test["id"]
            result["test_name"] = test["name"]
            result["category"] = test["category"]

            model_results.append(result)

            if result["status"] == "success":
                status = "✓ PASS" if result["validation_passed"] else "○ DONE"
                print(f"{status} | {result['elapsed_seconds']:6.1f}s | {result.get('content_length', 0):5d} chars")
            else:
                print(f"✗ FAIL | {result.get('error', 'Unknown error')[:50]}")

        # Calculate summary
        successful = [r for r in model_results if r["status"] == "success"]
        validated = [r for r in model_results if r.get("validation_passed")]

        summary = {
            "total": len(tests),
            "successful": len(successful),
            "validated": len(validated),
            "failed": len(tests) - len(successful),
            "avg_time": round(sum(r["elapsed_seconds"] for r in successful) / len(successful), 2) if successful else 0,
            "avg_length": round(sum(r.get("content_length", 0) for r in successful) / len(successful), 0) if successful else 0
        }

        all_results[model] = {
            "info": model_info,
            "summary": summary,
            "tests": model_results
        }

        print(f"\n  Summary: {summary['successful']}/{summary['total']} successful | {summary['validated']} validated | Avg: {summary['avg_time']}s")

    return all_results

def print_comparison_table(results: dict):
    """Print side-by-side comparison"""
    print(f"\n{'='*100}")
    print("COMPARISON SUMMARY")
    print(f"{'='*100}\n")

    # Header
    print(f"{'Model':<35} {'Type':<12} {'Success':>10} {'Valid':>10} {'Avg Time':>12} {'Avg Len':>10}")
    print("─" * 95)

    for model, data in results.items():
        s = data["summary"]
        model_type = data["info"].get("type", "?")
        print(f"{model:<35} {model_type:<12} {s['successful']:>3}/{s['total']:<6} {s['validated']:>3}/{s['total']:<6} {s['avg_time']:>10.1f}s {int(s['avg_length']):>10}")

    print()

def print_detailed_results(results: dict):
    """Print detailed test-by-test results"""
    print(f"\n{'='*100}")
    print("DETAILED RESULTS BY TEST")
    print(f"{'='*100}\n")

    # Group by test
    test_comparison = {}
    for model, data in results.items():
        for test in data["tests"]:
            tid = test["test_id"]
            if tid not in test_comparison:
                test_comparison[tid] = {"name": test["test_name"], "category": test["category"], "results": {}}
            test_comparison[tid]["results"][model] = test

    for tid, test_data in sorted(test_comparison.items()):
        print(f"\n[{tid}] {test_data['category']} - {test_data['name']}")
        print("─" * 80)

        for model, result in test_data["results"].items():
            status = "✓" if result.get("validation_passed") else ("○" if result["status"] == "success" else "✗")
            time_str = f"{result.get('elapsed_seconds', 0):.1f}s"
            print(f"  {status} {model:<35} {time_str:>8} | {result.get('content_length', 0):>5} chars")

            # Show preview for interesting comparisons
            if result["status"] == "success" and result.get("content_preview"):
                preview = result["content_preview"][:200].replace("\n", " ")
                print(f"      Preview: {preview}...")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="MageAgent Comprehensive Benchmark")
    parser.add_argument("--models", nargs="+", help="Specific models to test")
    parser.add_argument("--tests", nargs="+", type=int, help="Specific test IDs")
    parser.add_argument("--timeout", type=int, default=300, help="Timeout per test (seconds)")
    parser.add_argument("--local-only", action="store_true", help="Only test local MageAgent models")
    parser.add_argument("--cloud-only", action="store_true", help="Only test cloud Anthropic models")
    parser.add_argument("--category", type=str, help="Test specific category only")
    parser.add_argument("--output", type=str, help="Save results to JSON file")
    parser.add_argument("--quick", action="store_true", help="Quick test with subset of tests")

    args = parser.parse_args()

    # Filter models
    if args.models:
        models_to_test = args.models
    elif args.local_only:
        models_to_test = [m for m, info in MODELS.items() if info["type"] == "mageagent"]
    elif args.cloud_only:
        models_to_test = [m for m, info in MODELS.items() if info["type"] == "anthropic"]
    else:
        models_to_test = list(MODELS.keys())

    # Filter tests
    if args.tests:
        test_ids = args.tests
    elif args.category:
        test_ids = [t["id"] for t in TEST_CASES if t["category"].lower() == args.category.lower()]
    elif args.quick:
        # Quick test: one from each category
        seen_cats = set()
        test_ids = []
        for t in TEST_CASES:
            if t["category"] not in seen_cats:
                test_ids.append(t["id"])
                seen_cats.add(t["category"])
    else:
        test_ids = None

    # Run benchmark
    results = run_benchmark(models=models_to_test, test_ids=test_ids, timeout=args.timeout)

    # Print results
    print_comparison_table(results)
    print_detailed_results(results)

    # Save if requested
    if args.output:
        # Convert results to JSON-serializable format
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "results": {}
        }
        for model, data in results.items():
            output_data["results"][model] = {
                "info": data["info"],
                "summary": data["summary"],
                "tests": [
                    {k: v for k, v in t.items() if k != "validation"}
                    for t in data["tests"]
                ]
            }
        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2, default=str)
        print(f"\nResults saved to: {args.output}")
