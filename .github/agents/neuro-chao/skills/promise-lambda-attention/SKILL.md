---
name: promise-lambda-attention
description: Implements the Promise-Lambda Attention paradigm, a constraint-satisfaction mechanism where a promise (λ) filters a manifold of protocol-execution pairs (KV) to find valid solutions. Use for conceptual modeling, repository analysis, and constraint-based reasoning.
---

# Promise-Lambda Attention

This skill provides the tools and concepts to work with **Promise-Lambda Attention**, a paradigm that inverts the traditional attention mechanism. Instead of querying for information, a **promise (λ)** asserts a set of constraints, and the system finds all **protocol-execution (KV)** pairs that satisfy it.

## Core Concept: λ(KV)^-1

The fundamental idea is to find solutions that satisfy a promise within a given space of possibilities.

| Component | Standard Attention | Promise-Lambda Attention |
| :--- | :--- | :--- |
| **Q (Query)** | "What am I looking for?" | **λ.promise**: "What *must* be true." |
| **K (Key)** | "What information is available?" | **Protocol**: An interpretive framework or grammar. |
| **V (Value)** | "What information do I get?" | **Execution**: A concrete instantiation or action. |
| **Mechanism** | `softmax(QK^T)V` | `λ(KV)^-1` |

The mechanism finds all `(KV)` pairs whose inverse (generative history) satisfies the promise `λ`.

For a deeper dive into the mathematical and conceptual foundations, refer to the reference document:

```bash
cat /home/ubuntu/skills/promise-lambda-attention/references/paradigm.md
```

## Workflows

This skill supports two primary workflows: conceptual simulation and repository analysis.

### 1. Conceptual Simulation

To understand the core mechanics, use the `promise_attention_simulator.py` script. It demonstrates how a promise filters a predefined KV space.

**Usage:**

```bash
python /home/ubuntu/skills/promise-lambda-attention/scripts/promise_attention_simulator.py
```

The script runs a simulation with a sample KV space and two different promises, showing how the solution set changes based on the asserted constraints.

### 2. Repository Analysis

Apply the paradigm to a code repository to enforce quality and security constraints. This workflow uses the `repo_analyzer.py` script and a `.promise` configuration file.

**Step 1: Define the Promise**

Create a `.promise` file at the root of the repository you want to analyze. This file defines the assertions to be checked. A template is provided to get you started.

```bash
# Copy the template to your repository root
cp /home/ubuntu/skills/promise-lambda-attention/templates/.promise.template /path/to/your/repo/.promise
```

Edit the `.promise` file to define your specific constraints.

**Step 2: Run the Analyzer**

Execute the `repo_analyzer.py` script, pointing it to your repository.

```bash
python /home/ubuntu/skills/promise-lambda-attention/scripts/repo_analyzer.py /path/to/your/repo
```

The script will read the `.promise` file, traverse the repository, and report any files that violate the asserted promises.

For more details on how this integration works, see the repository integration guide:

```bash
cat /home/ubuntu/skills/promise-lambda-attention/references/repo-integration.md
```

## Bundled Resources

| Path                                                                  | Description                                                                 |
| --------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| `scripts/promise_attention_simulator.py`                              | A Python script to simulate the core Promise-Lambda Attention mechanism.    |
| `scripts/repo_analyzer.py`                                            | A Python script to analyze a repository based on a `.promise` file.         |
| `templates/.promise.template`                                         | A template for the `.promise` configuration file used by the repo analyzer. |
| `references/paradigm.md`                                              | A detailed explanation of the mathematical and conceptual foundations.      |
| `references/repo-integration.md`                                      | A guide on how to apply the paradigm to a repository structure.             |
