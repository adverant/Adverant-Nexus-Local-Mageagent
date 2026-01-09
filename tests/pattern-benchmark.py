#!/usr/bin/env python3
"""
MageAgent Pattern Benchmark - Complex Real-World Test Cases
Tests all orchestration patterns with 20+ complex coding tasks
"""

import requests
import json
import time
import sys
from datetime import datetime

BASE_URL = "http://localhost:3457/v1/chat/completions"

# All patterns to test
PATTERNS = [
    "mageagent:validator",    # Fast 7B - baseline
    "mageagent:primary",      # 72B reasoning
    "mageagent:tools",        # Hermes-3 tool calling
    "mageagent:hybrid",       # 72B + Hermes-3
    "mageagent:validated",    # Generate + validate
    "mageagent:compete",      # Multi-model judge
    "mageagent:execute",      # ReAct with tool execution
]

# 20+ Complex Real-World Test Cases
TEST_CASES = [
    # === Algorithm & Data Structure Challenges ===
    {
        "id": 1,
        "category": "Algorithm",
        "name": "LRU Cache Implementation",
        "prompt": "Implement an LRU (Least Recently Used) cache in Python with O(1) get and put operations. Include proper type hints, docstrings, and handle edge cases. The cache should support a configurable capacity.",
        "complexity": "high",
        "expected_elements": ["OrderedDict", "dict", "capacity", "get", "put", "move_to_end"]
    },
    {
        "id": 2,
        "category": "Algorithm",
        "name": "Trie with Autocomplete",
        "prompt": "Implement a Trie (prefix tree) in TypeScript with insert, search, startsWith, and autocomplete methods. The autocomplete should return the top 5 most frequent completions. Include proper typing.",
        "complexity": "high",
        "expected_elements": ["class", "insert", "search", "startsWith", "autocomplete", "TrieNode"]
    },
    {
        "id": 3,
        "category": "Algorithm",
        "name": "Graph Shortest Path",
        "prompt": "Implement Dijkstra's algorithm in Rust to find the shortest path in a weighted graph. Handle disconnected nodes gracefully and return both the distance and the path. Use proper Rust idioms.",
        "complexity": "very_high",
        "expected_elements": ["BinaryHeap", "HashMap", "fn dijkstra", "Vec", "Option", "priority"]
    },

    # === System Design & Architecture ===
    {
        "id": 4,
        "category": "System Design",
        "name": "Rate Limiter",
        "prompt": "Design and implement a distributed rate limiter in Go using the sliding window algorithm. It should support multiple rate limit rules (per user, per IP, per endpoint) and be thread-safe. Include Redis integration.",
        "complexity": "very_high",
        "expected_elements": ["sync.Mutex", "time.Duration", "Redis", "slidingWindow", "Allow", "struct"]
    },
    {
        "id": 5,
        "category": "System Design",
        "name": "Event Sourcing CQRS",
        "prompt": "Implement a basic event sourcing system with CQRS pattern in TypeScript. Include event store, aggregate root, command handlers, and query handlers. Use proper domain-driven design patterns.",
        "complexity": "very_high",
        "expected_elements": ["EventStore", "AggregateRoot", "CommandHandler", "QueryHandler", "Event", "apply"]
    },
    {
        "id": 6,
        "category": "System Design",
        "name": "Circuit Breaker",
        "prompt": "Implement a circuit breaker pattern in Python with states (closed, open, half-open), configurable thresholds, and automatic recovery. Include async support and proper logging.",
        "complexity": "high",
        "expected_elements": ["CircuitBreaker", "CLOSED", "OPEN", "HALF_OPEN", "async", "threshold", "timeout"]
    },

    # === Database & Query Optimization ===
    {
        "id": 7,
        "category": "Database",
        "name": "Query Builder",
        "prompt": "Create a type-safe SQL query builder in TypeScript that supports SELECT, JOIN, WHERE, ORDER BY, GROUP BY, and subqueries. Use method chaining and prevent SQL injection. Include proper generic types.",
        "complexity": "very_high",
        "expected_elements": ["QueryBuilder", "select", "where", "join", "orderBy", "build", "generic"]
    },
    {
        "id": 8,
        "category": "Database",
        "name": "Connection Pool",
        "prompt": "Implement a database connection pool in Java with configurable min/max connections, connection validation, idle timeout, and connection leak detection. Use proper concurrency primitives.",
        "complexity": "very_high",
        "expected_elements": ["ConnectionPool", "BlockingQueue", "synchronized", "validate", "acquire", "release"]
    },

    # === API & Web Development ===
    {
        "id": 9,
        "category": "API",
        "name": "GraphQL Resolver",
        "prompt": "Write a GraphQL resolver in TypeScript for a social media app with users, posts, comments, and likes. Include DataLoader for N+1 query prevention, pagination, and authentication middleware.",
        "complexity": "very_high",
        "expected_elements": ["DataLoader", "resolver", "Query", "Mutation", "context", "pagination", "cursor"]
    },
    {
        "id": 10,
        "category": "API",
        "name": "REST API Validation",
        "prompt": "Create a comprehensive request validation middleware for Express.js using Zod. Support body, query, params validation with custom error messages, nested objects, and conditional validation.",
        "complexity": "high",
        "expected_elements": ["z.object", "middleware", "validate", "safeParse", "ZodError", "custom"]
    },
    {
        "id": 11,
        "category": "API",
        "name": "WebSocket Manager",
        "prompt": "Implement a WebSocket connection manager in Python (using websockets library) that handles rooms, broadcasts, private messages, connection state, heartbeats, and automatic reconnection.",
        "complexity": "very_high",
        "expected_elements": ["websockets", "async", "rooms", "broadcast", "heartbeat", "reconnect", "ConnectionManager"]
    },

    # === Security & Authentication ===
    {
        "id": 12,
        "category": "Security",
        "name": "JWT Auth System",
        "prompt": "Implement a complete JWT authentication system in Node.js with access tokens, refresh tokens, token rotation, revocation list, and secure cookie handling. Include rate limiting on auth endpoints.",
        "complexity": "very_high",
        "expected_elements": ["jwt.sign", "jwt.verify", "refreshToken", "accessToken", "httpOnly", "revoke", "rotate"]
    },
    {
        "id": 13,
        "category": "Security",
        "name": "RBAC System",
        "prompt": "Design a Role-Based Access Control (RBAC) system in Python with roles, permissions, hierarchical inheritance, and resource-based permissions. Include decorators for endpoint protection.",
        "complexity": "very_high",
        "expected_elements": ["Role", "Permission", "has_permission", "decorator", "inherit", "resource"]
    },

    # === Testing & Quality ===
    {
        "id": 14,
        "category": "Testing",
        "name": "Property-Based Tests",
        "prompt": "Write property-based tests in Python using Hypothesis for a complex data validation library. Include custom strategies, stateful testing, and shrinking examples.",
        "complexity": "high",
        "expected_elements": ["hypothesis", "given", "strategies", "stateful", "assume", "example"]
    },
    {
        "id": 15,
        "category": "Testing",
        "name": "E2E Test Framework",
        "prompt": "Create a custom E2E testing framework in TypeScript that wraps Playwright with page object model, automatic screenshots on failure, parallel execution, and custom assertions.",
        "complexity": "very_high",
        "expected_elements": ["Page", "Locator", "screenshot", "parallel", "beforeEach", "expect"]
    },

    # === DevOps & Infrastructure ===
    {
        "id": 16,
        "category": "DevOps",
        "name": "Kubernetes Operator",
        "prompt": "Write a Kubernetes custom resource definition (CRD) and operator in Go for managing a database cluster. Include reconciliation loop, status updates, and proper error handling.",
        "complexity": "very_high",
        "expected_elements": ["Reconcile", "CRD", "controller-runtime", "Status", "Spec", "client.Client"]
    },
    {
        "id": 17,
        "category": "DevOps",
        "name": "CI/CD Pipeline",
        "prompt": "Create a complete GitHub Actions workflow for a monorepo with conditional builds, caching, parallel jobs, matrix testing, artifact management, and deployment to multiple environments.",
        "complexity": "high",
        "expected_elements": ["workflow", "jobs", "matrix", "cache", "artifacts", "environment", "needs"]
    },

    # === Machine Learning & Data ===
    {
        "id": 18,
        "category": "ML",
        "name": "Feature Engineering Pipeline",
        "prompt": "Implement a feature engineering pipeline in Python using scikit-learn with custom transformers, handling missing values, encoding categoricals, scaling numerics, and feature selection.",
        "complexity": "very_high",
        "expected_elements": ["Pipeline", "ColumnTransformer", "BaseEstimator", "TransformerMixin", "fit_transform"]
    },
    {
        "id": 19,
        "category": "ML",
        "name": "Model Serving API",
        "prompt": "Create a production-ready ML model serving API in Python with FastAPI. Include model versioning, A/B testing, input validation, batch predictions, caching, and monitoring metrics.",
        "complexity": "very_high",
        "expected_elements": ["FastAPI", "pydantic", "prometheus", "cache", "batch", "version", "predict"]
    },

    # === Concurrency & Performance ===
    {
        "id": 20,
        "category": "Concurrency",
        "name": "Worker Pool",
        "prompt": "Implement a worker pool in Rust with configurable number of workers, task queue, graceful shutdown, panic recovery, and task prioritization. Use proper async/await patterns.",
        "complexity": "very_high",
        "expected_elements": ["tokio", "mpsc", "spawn", "JoinHandle", "shutdown", "priority"]
    },
    {
        "id": 21,
        "category": "Concurrency",
        "name": "Lock-Free Queue",
        "prompt": "Implement a lock-free MPMC (multi-producer multi-consumer) queue in C++ using atomic operations. Include proper memory ordering and ABA problem prevention.",
        "complexity": "very_high",
        "expected_elements": ["atomic", "memory_order", "compare_exchange", "ABA", "hazard_pointer"]
    },

    # === Domain-Specific Challenges ===
    {
        "id": 22,
        "category": "Domain",
        "name": "Financial Calculator",
        "prompt": "Implement a comprehensive financial calculator in Python with compound interest, amortization schedules, NPV, IRR, bond pricing, and option pricing (Black-Scholes). Include proper decimal handling.",
        "complexity": "very_high",
        "expected_elements": ["Decimal", "compound_interest", "amortization", "npv", "irr", "black_scholes"]
    },
    {
        "id": 23,
        "category": "Domain",
        "name": "Regex Engine",
        "prompt": "Implement a basic regex engine in Python that supports literal characters, ., *, +, ?, character classes [], grouping (), and alternation |. Use Thompson's NFA construction.",
        "complexity": "very_high",
        "expected_elements": ["NFA", "State", "epsilon", "match", "compile", "thompson"]
    },
    {
        "id": 24,
        "category": "Domain",
        "name": "Markdown Parser",
        "prompt": "Create a Markdown to HTML parser in TypeScript supporting headers, bold, italic, code blocks, links, images, lists, blockquotes, and tables. Use proper AST construction.",
        "complexity": "very_high",
        "expected_elements": ["AST", "parse", "tokenize", "Node", "render", "inline", "block"]
    },

    # === Error Handling & Resilience ===
    {
        "id": 25,
        "category": "Resilience",
        "name": "Retry with Backoff",
        "prompt": "Implement a robust retry mechanism in Python with exponential backoff, jitter, circuit breaker integration, different retry strategies per exception type, and observability hooks.",
        "complexity": "high",
        "expected_elements": ["retry", "exponential_backoff", "jitter", "max_retries", "on_retry", "strategy"]
    },
]

def run_test(pattern: str, test_case: dict, timeout: int = 300) -> dict:
    """Run a single test case against a pattern"""
    start_time = time.time()

    try:
        response = requests.post(
            BASE_URL,
            headers={"Content-Type": "application/json"},
            json={
                "model": pattern,
                "messages": [{"role": "user", "content": test_case["prompt"]}],
                "max_tokens": 4096,
                "temperature": 0.7
            },
            timeout=timeout
        )

        elapsed = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})

            # Check for expected elements
            elements_found = sum(1 for e in test_case["expected_elements"] if e.lower() in content.lower())
            element_score = elements_found / len(test_case["expected_elements"]) * 100

            return {
                "status": "success",
                "elapsed_seconds": round(elapsed, 2),
                "content_length": len(content),
                "tokens": usage.get("total_tokens", 0),
                "element_score": round(element_score, 1),
                "elements_found": elements_found,
                "elements_total": len(test_case["expected_elements"]),
                "content_preview": content[:500] + "..." if len(content) > 500 else content
            }
        else:
            return {
                "status": "error",
                "error": f"HTTP {response.status_code}: {response.text[:200]}",
                "elapsed_seconds": round(elapsed, 2)
            }

    except requests.exceptions.Timeout:
        return {
            "status": "timeout",
            "elapsed_seconds": timeout,
            "error": f"Request timed out after {timeout}s"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "elapsed_seconds": round(time.time() - start_time, 2)
        }

def run_benchmark(patterns: list = None, test_ids: list = None, timeout: int = 300):
    """Run the full benchmark suite"""
    patterns = patterns or PATTERNS
    tests = TEST_CASES if not test_ids else [t for t in TEST_CASES if t["id"] in test_ids]

    results = {
        "timestamp": datetime.now().isoformat(),
        "patterns": patterns,
        "total_tests": len(tests),
        "results": {}
    }

    print(f"\n{'='*80}")
    print(f"MageAgent Pattern Benchmark")
    print(f"Patterns: {len(patterns)} | Tests: {len(tests)} | Timeout: {timeout}s")
    print(f"{'='*80}\n")

    for pattern in patterns:
        print(f"\n--- Testing Pattern: {pattern} ---\n")
        results["results"][pattern] = {"tests": [], "summary": {}}
        pattern_start = time.time()

        for test in tests:
            print(f"  [{test['id']:2d}] {test['category']:12s} | {test['name'][:30]:30s} | ", end="", flush=True)

            result = run_test(pattern, test, timeout)
            result["test_id"] = test["id"]
            result["test_name"] = test["name"]
            result["category"] = test["category"]
            result["complexity"] = test["complexity"]

            results["results"][pattern]["tests"].append(result)

            if result["status"] == "success":
                print(f"✓ {result['elapsed_seconds']:6.1f}s | Score: {result['element_score']:5.1f}%")
            else:
                print(f"✗ {result['status']}: {result.get('error', '')[:50]}")

        # Calculate summary for pattern
        successful = [t for t in results["results"][pattern]["tests"] if t["status"] == "success"]
        results["results"][pattern]["summary"] = {
            "total_tests": len(tests),
            "successful": len(successful),
            "failed": len(tests) - len(successful),
            "avg_time": round(sum(t["elapsed_seconds"] for t in successful) / len(successful), 2) if successful else 0,
            "avg_score": round(sum(t["element_score"] for t in successful) / len(successful), 1) if successful else 0,
            "total_time": round(time.time() - pattern_start, 2)
        }

        print(f"\n  Summary: {len(successful)}/{len(tests)} passed | Avg Time: {results['results'][pattern]['summary']['avg_time']}s | Avg Score: {results['results'][pattern]['summary']['avg_score']}%")

    return results

def print_comparison(results: dict):
    """Print a comparison table of all patterns"""
    print(f"\n{'='*80}")
    print("PATTERN COMPARISON SUMMARY")
    print(f"{'='*80}\n")

    headers = ["Pattern", "Success", "Avg Time", "Avg Score", "Total Time"]
    print(f"{'Pattern':<25} {'Success':>10} {'Avg Time':>12} {'Avg Score':>12} {'Total Time':>12}")
    print("-" * 75)

    for pattern, data in results["results"].items():
        s = data["summary"]
        print(f"{pattern:<25} {s['successful']:>3}/{s['total_tests']:<6} {s['avg_time']:>10.1f}s {s['avg_score']:>10.1f}% {s['total_time']:>10.1f}s")

    print()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="MageAgent Pattern Benchmark")
    parser.add_argument("--patterns", nargs="+", help="Specific patterns to test")
    parser.add_argument("--tests", nargs="+", type=int, help="Specific test IDs to run")
    parser.add_argument("--timeout", type=int, default=300, help="Timeout per test in seconds")
    parser.add_argument("--output", type=str, help="Output JSON file")

    args = parser.parse_args()

    results = run_benchmark(
        patterns=args.patterns,
        test_ids=args.tests,
        timeout=args.timeout
    )

    print_comparison(results)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {args.output}")
