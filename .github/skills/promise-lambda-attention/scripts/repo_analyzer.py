#!/usr/bin/env python
# repo_analyzer.py

import os
import yaml
import argparse

"""
Analyzes a repository using the Promise-Lambda Attention paradigm.
Treats file extensions as Protocols (K) and file content as Executions (V).
The promise is defined in a `.promise` file at the repository root.
"""

# --- Promise Parsing ---

def load_promise(repo_path: str) -> dict | None:
    """Loads and parses the .promise file from the repository root."""
    promise_path = os.path.join(repo_path, ".promise")
    if not os.path.exists(promise_path):
        return None
    with open(promise_path, "r") as f:
        return yaml.safe_load(f)

# --- Promise Lambda Implementations ---

def check_docstrings(content: str) -> bool:
    """Checks if all function definitions have docstrings."""
    import re
    # Find all function definitions
    func_defs = re.findall(r'def\s+\w+\s*\([^)]*\)\s*:', content)
    if not func_defs:
        return True  # No functions, so the promise is trivially satisfied
    
    # Check for docstrings after each function definition
    for func_def in func_defs:
        # Find the position of the function definition
        start = content.find(func_def)
        # Look for a docstring immediately after the colon
        after_def = content[start + len(func_def):].lstrip()
        if not (after_def.startswith('"""') or after_def.startswith("'''")):
            return False
    return True

def check_no_secrets(content: str) -> bool:
    """Checks for common patterns of hardcoded secrets."""
    import re
    secret_patterns = [
        r'password\s*=\s*["\'][^"\']+["\']',
        r'api_key\s*=\s*["\'][^"\']+["\']',
        r'secret\s*=\s*["\'][^"\']+["\']',
        r'token\s*=\s*["\'][^"\']+["\']',
    ]
    for pattern in secret_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return False
    return True

PROMISE_LAMBDAS = {
    "all functions must have docstrings": check_docstrings,
    "no hardcoded secrets": check_no_secrets,
}

# --- Repository Traversal ---

def traverse_manifold(repo_path: str):
    """Traverses the repository, yielding (path, protocol, content) tuples."""
    for root, dirs, files in os.walk(repo_path):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file.startswith('.'):
                continue
            file_path = os.path.join(root, file)
            _, ext = os.path.splitext(file)
            protocol = ext if ext else "no_extension"
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                yield file_path, protocol, content
            except Exception:
                continue

# --- Main Analysis Function ---

def analyze_repo(repo_path: str):
    """Analyzes a repository using the Promise-Lambda Attention paradigm."""
    print(f"\n━━━ Promise-Lambda Repository Analysis ━━━")
    print(f"Repository: {repo_path}")

    promise_config = load_promise(repo_path)
    if not promise_config:
        print("\n⚠️  No .promise file found at repository root.")
        print("   Create a .promise file to define assertions.")
        return

    assertions = promise_config.get("assertions", [])
    if not assertions:
        print("\n⚠️  No assertions found in .promise file.")
        return

    print(f"\n▶ Loaded {len(assertions)} assertion(s) from .promise file.")

    violations = []
    for file_path, protocol, content in traverse_manifold(repo_path):
        for assertion in assertions:
            rule = assertion.get("rule")
            assertion_type = assertion.get("type")
            
            # Only apply code quality rules to Python files
            if assertion_type == "code_quality" and protocol != ".py":
                continue
            
            promise_lambda = PROMISE_LAMBDAS.get(rule)
            if promise_lambda and not promise_lambda(content):
                violations.append({
                    "file": file_path,
                    "rule": rule,
                    "type": assertion_type
                })

    # --- Report ---
    print(f"\n━━━ Analysis Results ━━━")
    if not violations:
        print("\n✅ All files satisfy the promise!")
    else:
        print(f"\n❌ Found {len(violations)} violation(s):")
        for v in violations:
            rel_path = os.path.relpath(v['file'], repo_path)
            print(f"  - [{v['type']}] {rel_path}: Violates '{v['rule']}'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze a repository using Promise-Lambda Attention.")
    parser.add_argument("repo_path", help="Path to the repository to analyze.")
    args = parser.parse_args()
    
    if not os.path.isdir(args.repo_path):
        print(f"Error: '{args.repo_path}' is not a valid directory.")
    else:
        analyze_repo(args.repo_path)
