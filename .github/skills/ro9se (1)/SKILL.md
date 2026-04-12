---
name: ro9se
description: "Analyze, evolve, and extend the ro9se polyglot OpenCog integration repository (e9-o9/ro9se). Use for: adding language bindings for cogutil/atomspace/cogserver, analyzing language AI capabilities, working with the Inferno cognitive kernel, running OpenCog analysis tools, implementing FrankenCog synthesis, and syncing changes to GitHub. Triggers on mentions of ro9se, RosettaCog, OpenCog integration, polyglot AGI, FrankenCog, or Inferno kernel."
---

# ro9se — Polyglot OpenCog Integration

The `ro9se` repository (`e9-o9/ro9se`) is a post-polyglot meta-intelligence framework that:
- Analyzes 970+ programming languages for AI/AGI capabilities across 10 cognitive domains
- Implements OpenCog core components (`cogutil`, `atomspace`, `cogserver`) in 14+ languages
- Orchestrates multi-agent cognitive reasoning via Agent-Zero
- Builds toward an Inferno kernel-based distributed AGI operating system

## Repository Structure

```
ro9se/
├── Repo/opencog/           # Multi-language component implementations
│   ├── cogutil/            # Utilities (14 languages: C++, Python, Go, Julia, Rust, Scheme, ...)
│   ├── atomspace/          # Hypergraph KB (12 languages)
│   └── cogserver/          # Network REPL (12 languages)
├── opencog/                # Python analysis framework
│   ├── lib/                # Core modules: analyzer, hypergraph, atom_types
│   ├── bin/                # CLI tools
│   ├── agents/             # Multi-agent system
│   ├── patterns/           # 10 cognitive patterns
│   ├── strategies/         # 7 reasoning strategies
│   └── inferno-kernel/     # Inferno OS cognitive kernel
├── Lang/                   # RosettaCode data: 970 languages
└── Task/                   # RosettaCode tasks: 1,228 tasks
```

## Dependency Chain

```
cogutil (no deps)
  └── atomspace
        └── atomspace-storage
              └── cogserver
```

Always implement components in this order when adding a new language.

## Core Workflows

### 1. Add Language Bindings

To add `cogutil` → `atomspace` → `cogserver` for a new language:

```bash
# Step 1: Check what's missing
python /home/ubuntu/skills/ro9se/scripts/opencog-bindgen --list-missing

# Step 2: Generate boilerplate for a specific component
python /home/ubuntu/skills/ro9se/scripts/opencog-bindgen \
  --lang <language> --component <component> \
  --output /path/to/ro9se/Repo/opencog/<component>/<Language>

# Step 3: Auto-generate all missing at once
python /home/ubuntu/skills/ro9se/scripts/opencog-bindgen --auto-complete
```

Supported languages for generation: `go`, `julia`, `rust`, `scheme`, `prolog`.

After generating, implement the logic following the reference implementations:
- **C++**: `Repo/opencog/cogutil/c++/opencog-cogutil.cpp`
- **Python**: `Repo/opencog/cogutil/Python/opencog-cogutil.py`
- **Go**: `Repo/opencog/atomspace/Go/atomspace.go` (full implementation with tests)

### 2. Run Analysis Tools

All tools run from the repository root:

```bash
opencog/bin/opencog-analyze              # Full language analysis
opencog/bin/opencog-hypergraph           # Hypergraph generation (45 subcategories)
opencog/bin/opencog-atom-types           # Formal atom type expressions
opencog/bin/opencog-reasoning            # Reasoning task analysis
opencog/bin/opencog-agent-zero <task>    # Multi-agent orchestration
opencog/bin/opencog-eval-lang <lang>     # Evaluate a specific language
opencog/bin/opencog-inferno              # Inferno kernel interaction
opencog/bin/opencog-manifest             # FrankenCog integration manifest
```

### 3. Sync to GitHub

Always use the `magoo` PAT for pushing to `e9-o9/ro9se`:

```bash
git add .
git commit -m "feat: <description>"
git push https://${magoo}@github.com/e9-o9/ro9se.git main
```

## Language Coverage Matrix

| Component  | C++ | Python | Haskell | Go | Julia | Rust | Scheme | Prolog | Racket | Perl | Raku | Clojure | D | Limbo |
|-----------|-----|--------|---------|----|----|------|--------|--------|--------|------|------|---------|---|-------|
| cogutil   | ✓   | ✓      | ✓       | ✓  | ✓  | ✓    | ✓      | -      | ✓      | ✓    | ✓    | ✓       | ✓ | ✓     |
| atomspace | ✓   | ✓      | ✓       | ✓  | -  | -    | -      | ✓      | ✓      | ✓    | ✓    | ✓       | ✓ | ✓     |
| cogserver | ✓   | ✓      | ✓       | ✓  | -  | -    | -      | -      | ✓      | ✓    | ✓    | ✓       | ✓ | ✓     |

Missing: Julia, Rust, Scheme for atomspace/cogserver; Prolog for cogutil/cogserver.

## Implementation Pattern

Each language implementation is a **single self-contained file** that demonstrates the language's idioms. The file naming convention is:
- `opencog-cogutil.<ext>`
- `opencog-atomspace.<ext>`
- `opencog-cogserver.<ext>`

Exception: Go uses a package structure with `atomspace.go` + `atomspace_test.go` + `go.mod`.

Each implementation must demonstrate:
1. **CogUtil**: Logger, Config, Concurrent data structures
2. **AtomSpace**: Atom (Node/Link), TruthValue, Handle, AtomSpace database
3. **CogServer**: Command registry, Module system, Network REPL

## FrankenCog Synthesis

The optimal language per cognitive domain (from analysis):

| Domain | Optimal Language |
|--------|------------------|
| ML / Perception | C |
| Concurrent systems | Ada |
| Knowledge representation | C++ |
| Symbolic reasoning | C# |
| Planning / Problem solving | 11l |
| Meta-learning / Self-reflection | FreeBASIC |

Read `references/ro9se_ReadMe.md` for the full FrankenCog manifest details.

## Inferno Kernel Integration

The `opencog/inferno-kernel/` directory contains the implementation of cognition as a kernel service. The 9P protocol is used to expose the AtomSpace as a filesystem:

```
/atomspace/
  /atoms/nodes/<type>/<name>
  /atoms/links/<type>/<id>
  /queries/pattern   # write pattern, read results
  /ctl               # control interface
```

For Inferno/Limbo implementations, refer to `Repo/opencog/cogutil/Limbo/` as the reference.

## Reference Documents

Load these only when specifically needed:

- **Project overview & tech stack**: `references/ro9se_ReadMe.md`
- **5-phase roadmap (2025-2027+)**: `references/ro9se_ROADMAP.md`
- **Python framework details**: `references/opencog_README.md`
- **Multi-language component guide**: `references/Repo_opencog_README.md`
- **Hypergraph taxonomy (45 subcategories)**: `references/opencog_HYPERGRAPH.md`
- **Formal atom type expressions**: `references/opencog_ATOM_TYPES.md`
- **Full integration architecture**: `references/OPENCOG_INTEGRATION_DESIGN.md`
- **Go implementation summary**: `references/IMPLEMENTATION_SUMMARY_2024.md`
