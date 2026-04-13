RosettaCode Data Project
========================

This git repository contains (almost) all of the code samples available on
http://rosettacode.org organized by Language and Task.


## Getting the Data

All of the data is in this repository, so you can just run:

    git clone https://github.com/acmeism/RosettaCodeData

*However...*

It's a lot of data!

If you just want the latest data, the quickest thing to do is:

    git clone https://github.com/acmeism/RosettaCodeData --single-branch --depth=1


## Tools

This repository's data content is created by a Perl program called
`rosettacode`.

You can install it with this command:

    cpanm RosettaCode

You can rebuild the data with:

    make build


This repository has a `bin` directory with various tools for working with the
data.

* `rcd-api-list-all-langs`

    List all the programming language names directly from rosettacode.org

* `rcd-api-list-all-tasks`

    List all the programming task names directly from rosettacode.org

* `rcd-new-langs`

    List the RosettaCode languages not yet add to Conf

* `rcd-new-tasks`

    List the RosettaCode tasks not yet add to Conf

* `rcd-samples-per-lang`

    Show the number of code samples per language

* `rcd-samples-per-task`

    Show the number of code samples per task

* `rcd-tasks-per-lang`

    Show the number of tasks with code samples per language

* `rcd-langs-per-task`

    Show the number of languages with code samples per task


## OpenCog: AI/AGI Evaluation Framework

The `opencog` directory contains a post-polyglot transcendent evaluation framework
that analyzes all programming languages for AI and AGI capabilities. OpenCog
represents the culmination of evaluating every known programming language against
the full spectrum of AI capabilities.

### OpenCog Multi-Agent Reasoning System

OpenCog now includes a sophisticated multi-agent orchestration workbench for
solving LLM reasoning tasks, featuring:

- **Agent-Zero**: Master builder that orchestrates cognitive architectures
- **Pattern Language Library**: 10 foundational cognitive patterns for AGI
- **Multi-Agent Orchestration**: Collaborative problem-solving with specialized agents
- **Strategy Repository**: 7 core reasoning strategies
- **95 Reasoning Tasks**: Comprehensive collection of LLM reasoning challenges

**Quick Start:**
```bash
# Run the reasoning task demo
python3 opencog/opencog_reasoning_demo.py

# Analyze reasoning tasks
opencog/bin/opencog-reasoning

# Solve a specific task with Agent-Zero
opencog/bin/opencog-agent-zero analogical-problem-solving autonomous
```

### OpenCog Tools

The OpenCog framework provides tools to evaluate languages across AI domains:

* `opencog/bin/opencog-analyze`

    Analyze all languages and generate comprehensive AI capability reports
    showing which languages excel at different AI/cognitive tasks

* `opencog/bin/opencog-hypergraph`

    **NEW**: Refined task specialization analyzer with subcategory-level analysis
    and hypergraph generation revealing patterns of peak performance by
    language and paradigm (45 subcategories across 9 paradigms)

* `opencog/bin/opencog-atom-types`

    **NEW**: Generates formalized atom type expressions for cognitive domains and
    language paradigms. Provides mathematical framework with algebraic operations
    for reasoning about language-domain affinities and paradigm composition.

* `opencog/bin/opencog-neurosymbolic`

    **NEW**: Analyzes languages on the neuro-symbolic spectrum - classifies how
    languages balance neural (continuous field) and symbolic (discrete collapse)
    computation. Reveals which languages preserve possibility vs. force commitment,
    and correlates spectrum position with paradigms and AI capabilities.

* `opencog/bin/opencog-reasoning`

    Analyze reasoning tasks and get pattern/strategy recommendations

* `opencog/bin/opencog-agent-zero <task_id> [mode]`

    Orchestrate a reasoning task using Agent-Zero with autonomous,
    collaborative, or guided modes

* `opencog/bin/opencog-manifest`

    Generate the FrankenCog Integration Manifest - identifies the optimal
    language for each AI function to create a "patchwork" of best implementations

* `opencog/bin/opencog-eval-lang <language>`

    Evaluate a specific language's AI capabilities in detail

* `opencog/bin/opencog-eval-category <category>`

    Evaluate all languages for a specific AI category (e.g., symbolic_reasoning,
    machine_learning, natural_language, etc.)

* `opencog/bin/opencog-report`

    Generate a comprehensive Transcendent Expression Report documenting the
    optimal language for each AI function and the overall FrankenCog synthesis

### AI Categories

OpenCog categorizes tasks into these AI/cognitive domains:

- **Symbolic Reasoning**: Logic, theorem proving, constraint satisfaction
  - Refined into 4 subcategories: logic fundamentals, theorem proving, constraint solving, formal computation
- **Pattern Recognition**: Search, matching, classification
  - Refined into 4 subcategories: search algorithms, string pattern matching, lexical patterns, recognition tasks
- **Knowledge Representation**: Data structures, graphs, semantic networks
  - Refined into 4 subcategories: graph structures, tree structures, associative structures, serialization
- **Machine Learning**: Statistical methods, optimization, neural networks
  - Refined into 4 subcategories: optimization, statistical learning, statistical measures, neural networks
- **Natural Language Processing**: Text analysis, parsing, NLP
  - Refined into 6 subcategories: tokenization, parsing, text processing, phonetic matching, text generation, language analysis
- **Planning & Problem Solving**: Heuristic search, game playing, puzzles
  - Refined into 5 subcategories: search strategies, game playing, puzzle solving, optimization problems, path planning
- **Uncertainty Reasoning**: Probabilistic methods, fuzzy logic
  - Refined into 4 subcategories: probability basics, Monte Carlo, statistical tests, distributions
- **Cognitive Architecture**: Concurrent systems, agent-based systems
  - Refined into 4 subcategories: parallelism, synchronization, concurrent patterns, message passing
- **Perception & Motor**: Image processing, signal processing
  - Refined into 5 subcategories: signal processing, image processing, bitmap operations, rendering, time processing
- **Meta-Learning**: Self-improvement, reflection, code generation
  - Refined into 5 subcategories: self reference, code generation, runtime evaluation, introspection, evaluation functions

**Total: 10 categories → 45 refined subcategories**

See `opencog/HYPERGRAPH.md` for complete subcategory taxonomy and hypergraph analysis documentation.

See `opencog/README.md` for complete documentation.

### Evaluation Results

The OpenCog framework has completed the evaluation of all 970+ programming languages
across the 10 AI/AGI functional categories. The system has:

✅ **Analyzed** 970 programming languages  
✅ **Categorized** 10,342 AI task implementations  
✅ **Evaluated** performance across 10 cognitive domains  
✅ **Generated** the FrankenCog Patchwork Inference Fabric  

**Top Languages by AI Capability** (100% category coverage):
1. Wren - 137 AI tasks
2. FreeBASIC - 136 AI tasks
3. Go - 136 AI tasks
4. Nim - 136 AI tasks
5. Julia - 135 AI tasks

**FrankenCog Optimal Language Selection** (best language per AI domain):
- **Symbolic Reasoning**: C# (12 tasks, from 1,185 total category implementations)
- **Pattern Recognition**: Ada (12 tasks, from 1,185 total category implementations)
- **Knowledge Representation**: C++ (16 tasks, from 1,334 total category implementations)
- **Machine Learning**: C (8 tasks, from 677 total category implementations)
- **Natural Language**: C (15 tasks, from 1,236 total category implementations)
- **Planning & Problem Solving**: 11l (13 tasks, from 1,102 total category implementations)
- **Uncertainty Reasoning**: C (11 tasks, from 592 total category implementations)
- **Cognitive Architecture**: Ada (10 tasks, from 494 total category implementations)
- **Perception & Motor**: C (20 tasks, from 1,183 total category implementations)
- **Meta-Learning**: FreeBASIC (16 tasks, from 1,354 total category implementations)

The evaluation demonstrates that no single language is optimal for all AI functions.
Instead, the FrankenCog approach leverages each language's unique strengths:
- **C** dominates in 4 performance-critical domains (ML, NLP, Uncertainty, Perception)
- **Ada** excels in concurrent and pattern recognition systems
- **C++** leads in knowledge representation
- **C#** is optimal for symbolic reasoning
- **11l** is best for planning and problem solving
- **FreeBASIC** leads in meta-learning and self-reflection

This post-polyglot synthesis represents the transcendent expression of each language's
core purpose - the specific functions each language was conceived to express.


## Development Roadmap

RosettaCog is on a path toward **entelechy** - the full realization of its potential as a living, adaptive meta-intelligence. See our comprehensive strategic planning documents:

### 📋 Strategic Documents

- **[ROADMAP.md](ROADMAP.md)** - Comprehensive 5-phase development roadmap (2025-2027+)
  - Phase 1: Quality & Robustness (Q1 2025)
  - Phase 2: Intelligence Amplification (Q2 2025)
  - Phase 3: Automation & Synthesis (Q3-Q4 2025) ⭐ **Critical Phase**
  - Phase 4: Ecosystem & Community (2026)
  - Phase 5: Meta-Intelligence & Self-Improvement (2027+)

- **[STRATEGIC_ANALYSIS.md](STRATEGIC_ANALYSIS.md)** - Deep analysis of current state, gaps, and opportunities
  - Current state assessment across 7 dimensions
  - Gap analysis with priorities
  - Competitive landscape evaluation
  - Strategic opportunities and recommendations

- **[ROADMAP_QUICK.md](ROADMAP_QUICK.md)** - Quick reference summary
  - Visual roadmap overview
  - Key milestones and success metrics
  - Critical path and priorities
  - How to get involved

### 🎯 Next Milestones

| Timeline | Milestone | Impact |
|----------|-----------|--------|
| 2025 Q1 | **Production-grade quality** with 80% test coverage | Foundation for reliability |
| 2025 Q3 | **FrankenCog compilation** - Automated polyglot synthesis ⭐ | **Game changer** |
| 2025 Q4 | **AI-assisted code translation** with >80% accuracy | Practical utility |
| 2026 | **Web platform** with interactive hypergraph visualization | Broad accessibility |
| 2027+ | **Self-improving meta-intelligence** with AGI scaffolding | Full entelechy |

### 🚀 Key Features Coming

- ✅ **Now**: Language analysis, hypergraph, multi-agent reasoning, FrankenCog manifest
- 🔄 **Phase 1**: Testing infrastructure, performance optimization, enhanced documentation
- 🔮 **Phase 2**: Advanced analytics, pattern discovery, strategy optimization
- 🚀 **Phase 3**: Automated FrankenCog compilation, code translation, benchmarking ⭐
- 🌍 **Phase 4**: Web visualization, REST API, plugin ecosystem, community platform
- 🧠 **Phase 5**: Self-improvement, language discovery, emergent patterns, AGI scaffolding

See [ROADMAP.md](ROADMAP.md) for complete details and technical specifications.


## Contributing

We welcome contributions! Here's how you can help:

- **Testing**: Write tests for core modules (Phase 1 priority)
- **Documentation**: Improve tutorials and guides
- **Analysis**: Validate language categorizations and cognitive mappings
- **Development**: Implement roadmap features
- **Community**: Join discussions, help users, share ideas

See our [roadmap documents](ROADMAP.md) for specific contribution opportunities.


## To Do (Legacy)

Pull requests welcome!

This project is not a perfect representation of RosettaCode yet.
It has a few unicode issues.
It also has to deal with various formatting mistakes in the mediawiki source
pages.

* Fix bugs

* Correct the 100s of guessed file extensions in `Conf/lang.yaml`

* Ability to only fetch cache pages since last pushed data update

* Support names with non-ascii characters

* Add more bin tools

* Address errors reported in rosettacode.log after running `make build`

**Note**: These legacy items are now integrated into our comprehensive [ROADMAP.md](ROADMAP.md).
See Phase 1 for testing/quality improvements and Phase 3+ for feature additions.
