---
name: fabric-skill-creator
description: Guide for creating effective skills in Fabric Notebook environments (builtin/env folders). This skill should be used when users want to create a new skill (or update an existing skill) that extends Claude's capabilities with specialized knowledge, workflows, or tool integrations for Fabric Notebooks.
---

# Skill Creator for Fabric Notebooks

This skill provides guidance for creating effective skills in Fabric Notebook environments.

## About Skills

Skills are modular, self-contained packages that extend Claude's capabilities by providing
specialized knowledge, workflows, and tools. Think of them as "onboarding guides" for specific
domains or tasks—they transform Claude from a general-purpose agent into a specialized agent
equipped with procedural knowledge that no model can fully possess.

### What Skills Provide

1. Specialized workflows - Multi-step procedures for specific domains
2. Tool integrations - Instructions for working with specific file formats or APIs
3. Domain expertise - Company-specific knowledge, schemas, business logic
4. Bundled resources - Scripts, references, and assets for complex and repetitive tasks

## Core Principles

### Concise is Key

The context window is a public good. Skills share the context window with everything else Claude needs: system prompt, conversation history, other Skills' metadata, and the actual user request.

**Default assumption: Claude is already very smart.** Only add context Claude doesn't already have. Challenge each piece of information: "Does Claude really need this explanation?" and "Does this paragraph justify its token cost?"

Prefer concise examples over verbose explanations.

### Set Appropriate Degrees of Freedom

Match the level of specificity to the task's fragility and variability:

**High freedom (text-based instructions)**: Use when multiple approaches are valid, decisions depend on context, or heuristics guide the approach.

**Medium freedom (pseudocode or scripts with parameters)**: Use when a preferred pattern exists, some variation is acceptable, or configuration affects behavior.

**Low freedom (specific scripts, few parameters)**: Use when operations are fragile and error-prone, consistency is critical, or a specific sequence must be followed.

Think of Claude as exploring a path: a narrow bridge with cliffs needs specific guardrails (low freedom), while an open field allows many routes (high freedom).

### Anatomy of a Skill

Every skill consists of a required SKILL.md file and optional bundled resources:

```
builtin/ (or env/)                    # Fabric Notebook resource folder
└── skills/                           # Skills directory
    └── skill-name/                   # Individual skill folder
        ├── SKILL.md (required)
        │   ├── YAML frontmatter metadata (required)
        │   │   ├── name: (required)
        │   │   └── description: (required)
        │   └── Markdown instructions (required)
        └── Bundled Resources (optional)
            ├── scripts/          - Executable Python scripts (PySpark compatible)
            ├── references/       - Documentation loaded into context as needed
            └── assets/           - Files used in output (templates, data, etc.)
```

#### SKILL.md (required)

Every SKILL.md consists of:

- **Frontmatter** (YAML): Contains `name` and `description` fields. These are the only fields that Claude reads to determine when the skill gets used, thus it is very important to be clear and comprehensive in describing what the skill is, and when it should be used.
- **Body** (Markdown): Instructions and guidance for using the skill. Only loaded AFTER the skill triggers (if at all).

#### Bundled Resources (optional)

##### Scripts (`scripts/`)

Executable code (Python/Bash/etc.) for tasks that require deterministic reliability or are repeatedly rewritten.

- **When to include**: When the same code is being rewritten repeatedly or deterministic reliability is needed
- **Example**: `scripts/rotate_pdf.py` for PDF rotation tasks
- **Benefits**: Token efficient, deterministic, may be executed without loading into context
- **Note**: Scripts may still need to be read by Claude for patching or environment-specific adjustments

**Runtime Environment in Fabric:**
Scripts run in Fabric remote cluster with either:
- **Pure Python runtime**: Standard Python environment
- **Spark runtime**: PySpark environment with distributed computing

**Accessing Scripts in Notebook Skills:**

- **Preferred**: Import directly by adding to Python path:
  ```python
  import sys; sys.path.insert(0, f"{notebookutils.nbResPath}/builtin/skills/skill-name/scripts")
  import module_name
  ```
- **MUST**: Only use this approach for skills belonging to the current active notebook
- **Alternative**: Read script content when patching or debugging is needed

##### References (`references/`)

Documentation and reference material intended to be loaded as needed into context to inform Claude's process and thinking.

- **When to include**: For documentation that Claude should reference while working
- **Examples**: `references/finance.md` for financial schemas, `references/mnda.md` for company NDA template, `references/policies.md` for company policies, `references/api_docs.md` for API specifications
- **Use cases**: Database schemas, API documentation, domain knowledge, company policies, detailed workflow guides
- **Benefits**: Keeps SKILL.md lean, loaded only when Claude determines it's needed
- **Best practice**: If files are large (>10k words), include grep search patterns in SKILL.md
- **Avoid duplication**: Information should live in either SKILL.md or references files, not both. Prefer references files for detailed information unless it's truly core to the skill—this keeps SKILL.md lean while making information discoverable without hogging the context window. Keep only essential procedural instructions and workflow guidance in SKILL.md; move detailed reference material, schemas, and examples to references files.

##### Assets (`assets/`)

Files not intended to be loaded into context, but rather used within the output Claude produces.

- **When to include**: When the skill needs files that will be used in the final output
- **Examples**: `assets/logo.png` for brand assets, `assets/slides.pptx` for PowerPoint templates, `assets/frontend-template/` for HTML/React boilerplate, `assets/font.ttf` for typography
- **Use cases**: Templates, images, icons, boilerplate code, fonts, sample documents that get copied or modified
- **Benefits**: Separates output resources from documentation, enables Claude to use files without loading them into context

#### What to Not Include in a Skill

A skill should only contain essential files that directly support its functionality. Do NOT create extraneous documentation or auxiliary files, including:

- README.md
- INSTALLATION_GUIDE.md
- QUICK_REFERENCE.md
- CHANGELOG.md
- etc.

The skill should only contain the information needed for an AI agent to do the job at hand. It should not contain auxiliary context about the process that went into creating it, setup and testing procedures, user-facing documentation, etc. Creating additional documentation files just adds clutter and confusion.

### Progressive Disclosure Design Principle

Skills use a three-level loading system to manage context efficiently:

1. **Metadata (name + description)** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed by Claude (Unlimited because scripts can be executed without reading into context window)

#### Progressive Disclosure Patterns

Keep SKILL.md body to the essentials and under 500 lines to minimize context bloat. Split content into separate files when approaching this limit. When splitting out content into other files, it is very important to reference them from SKILL.md and describe clearly when to read them, to ensure the reader of the skill knows they exist and when to use them.

**Key principle:** When a skill supports multiple variations, frameworks, or options, keep only the core workflow and selection guidance in SKILL.md. Move variant-specific details (patterns, examples, configuration) into separate reference files.

**Pattern 1: High-level guide with references**

```markdown
# PDF Processing

## Quick start

Extract text with pdfplumber:
[code example]

## Advanced features

- **Form filling**: See [FORMS.md](FORMS.md) for complete guide
- **API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
- **Examples**: See [EXAMPLES.md](EXAMPLES.md) for common patterns
```

Claude loads FORMS.md, REFERENCE.md, or EXAMPLES.md only when needed.

**Pattern 2: Domain-specific organization**

For Skills with multiple domains, organize content by domain to avoid loading irrelevant context:

```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── reference/
    ├── finance.md (revenue, billing metrics)
    ├── sales.md (opportunities, pipeline)
    ├── product.md (API usage, features)
    └── marketing.md (campaigns, attribution)
```

When a user asks about sales metrics, Claude only reads sales.md.

Similarly, for skills supporting multiple frameworks or variants, organize by variant:

```
cloud-deploy/
├── SKILL.md (workflow + provider selection)
└── references/
    ├── aws.md (AWS deployment patterns)
    ├── gcp.md (GCP deployment patterns)
    └── azure.md (Azure deployment patterns)
```

When the user chooses AWS, Claude only reads aws.md.

**Pattern 3: Conditional details**

Show basic content, link to advanced content:

```markdown
# DOCX Processing

## Creating documents

Use docx-js for new documents. See [DOCX-JS.md](DOCX-JS.md).

## Editing documents

For simple edits, modify the XML directly.

**For tracked changes**: See [REDLINING.md](REDLINING.md)
**For OOXML details**: See [OOXML.md](OOXML.md)
```

Claude reads REDLINING.md or OOXML.md only when the user needs those features.

**Important guidelines:**

- **Avoid deeply nested references** - Keep references one level deep from SKILL.md. All reference files should link directly from SKILL.md.
- **Structure longer reference files** - For files longer than 100 lines, include a table of contents at the top so Claude can see the full scope when previewing.

## Skill Creation Process for Fabric Notebooks

Skill creation involves these steps:

1. Understand the skill with concrete examples
2. Plan reusable skill contents (scripts, references, assets)
3. Create the skill structure manually in builtin/ or env/ folder
4. Implement and refine the skill content
5. Iterate based on real usage

Follow these steps in order, skipping only if there is a clear reason why they are not applicable.

### Step 1: Understanding the Skill with Concrete Examples

Skip this step only when the skill's usage patterns are already clearly understood. It remains valuable even when working with an existing skill.

To create an effective skill, clearly understand concrete examples of how the skill will be used. This understanding can come from either direct user examples or generated examples that are validated with user feedback.

For example, when building an image-editor skill, relevant questions include:

- "What functionality should the image-editor skill support? Editing, rotating, anything else?"
- "Can you give some examples of how this skill would be used?"
- "I can imagine users asking for things like 'Remove the red-eye from this image' or 'Rotate this image'. Are there other ways you imagine this skill being used?"
- "What would a user say that should trigger this skill?"

To avoid overwhelming users, avoid asking too many questions in a single message. Start with the most important questions and follow up as needed for better effectiveness.

Conclude this step when there is a clear sense of the functionality the skill should support.

### Step 2: Planning the Reusable Skill Contents

To turn concrete examples into an effective skill, analyze each example by:

1. Considering how to execute on the example from scratch
2. Identifying what scripts, references, and assets would be helpful when executing these workflows repeatedly

Example: When building a `lakehouse-analytics` skill to handle queries like "Analyze sales data by region":

1. Analyzing lakehouse data requires re-discovering table schemas and common patterns each time
2. Useful resources: `references/lakehouse-schema.md` for table schemas, `scripts/common_transforms.py` for reusable transformations

Apply this pattern to each concrete example to build the list of reusable resources (scripts, references, assets).

### Step 3: Create the Skill Structure in Fabric Notebook

At this point, create the skill directory structure in the Fabric Notebook.

#### Choose Location: builtin/ or env/

- **Use `builtin/skills/`**: For notebook-specific skills, experimental features, or in-development skills
- **Use `env/skills/`**: For shared skills used across multiple notebooks in the same environment

#### Create Directory Structure

Manually create the following structure:

```
builtin/skills/<skill-name>/         # Or env/skills/<skill-name>/
├── SKILL.md                         # Required: Skill documentation
├── scripts/                         # Optional: Python scripts
│   └── example_script.py
├── references/                      # Optional: Reference documentation
│   └── example_reference.md
└── assets/                          # Optional: Templates and data files
    └── example_template.json
```

#### Create SKILL.md and Example Files

Use the templates provided in the `references/` directory:

1. **Main skill file**: Copy [references/SKILL.md.template](references/SKILL.md.template) as your `SKILL.md`
   - Includes proper YAML frontmatter structure
   - Common skill organization patterns (workflow-based, task-based, reference-based, capabilities-based)
   - Resource directory guidance with Fabric-specific examples

2. **Example files** (copy as needed):
   - **Script**: [references/example_script.py](references/example_script.py) - PySpark-compatible Python script template
   - **Reference**: [references/example_reference.md](references/example_reference.md) - Documentation template
   - **Asset README**: [references/example_asset_readme.txt](references/example_asset_readme.txt) - Asset directory guide

Replace `{skill_name}` and `{skill_title}` placeholders with your actual skill name and title.

#### Implement Resources

Now implement the planned scripts, references, and assets:

- **Scripts**: Write PySpark-compatible Python code
- **References**: Create markdown documentation files
- **Assets**: Add any templates, sample data, or configuration files

**Fabric Runtime Considerations:**
- Scripts execute in Fabric remote cluster (pure Python or Spark runtime)
- **Cannot use relative file paths** to access other notebook files
- **To access other notebooks**: Use `notebookutils.notebook` CRUD APIs (call `get_notebookutils_doc(module_name=["notebook_crud"])` for complete documentation):
  - `getDefinition(name)` — retrieve notebook content (.ipynb JSON) for reading or reuse
  - `get(name)` — retrieve notebook metadata (id, description)
  - `list()` — enumerate all notebooks in workspace
  - `create(name, content=...)` / `updateDefinition(name, content=...)` — create or update notebooks programmatically
- Scripts have access to `notebookutils` for Fabric-specific operations

**Testing Scripts**: Test all Python scripts by running them in notebook cells to ensure compatibility with the Fabric Spark environment.

### Step 4: Implement and Refine

Remember that skills in Fabric Notebooks are created for AI agents (like Claude) to use when helping users with data engineering tasks. Include information that would be beneficial and non-obvious, especially:

- **Fabric-specific APIs**: NotebookUtils, lakehouse operations, Spark configurations
- **Environment limitations**: What works in local Python may not work in PySpark
- **Common patterns**: Data loading, transformations, visualizations specific to Fabric
- **Resource paths**: How to reference files in builtin/ or env/ folders

#### Learn Proven Design Patterns

Consult these helpful guides based on your skill's needs:

- **Multi-step processes**: See references/workflows.md for sequential workflows and conditional logic
- **Specific output formats or quality standards**: See references/output-patterns.md for template and example patterns

These files contain established best practices for effective skill design.

#### Start with Reusable Skill Contents

To begin implementation, start with the reusable resources identified above: `scripts/`, `references/`, and `assets/` files. Note that this step may require user input. For example, when implementing a `brand-guidelines` skill, the user may need to provide brand assets or templates to store in `assets/`, or documentation to store in `references/`.

**Testing Scripts in Fabric**: All Python scripts must be tested in Fabric Notebook cells to ensure:
- Compatibility with PySpark runtime
- Proper handling of Spark DataFrames vs Pandas DataFrames
- Correct path references to builtin/ or env/ folders
- No dependencies on unavailable packages

If there are many similar scripts, only a representative sample needs to be tested to ensure confidence.

#### Write SKILL.md

**Writing Guidelines:** Always use imperative/infinitive form.

**Validate Fabric Code Against Official Docs (MUST):**

For every Fabric-specific API or configuration in the skill, query official documentation to verify correctness *while writing*:
- Use `get_notebookutils_doc` for NotebookUtils APIs (fs, notebook, credentials, lakehouse, workspace, etc.)
- Use `get_fabric_doc` for lakehouse access, OneLake paths, magic commands (%%configure), and Spark configurations
- Use `microsoft_docs_search` or `microsoft_docs_fetch` for other Fabric features

Key items to verify against docs:
- `%%configure` must be in the first cell; magic commands use correct syntax (`%%sql`, `%%spark`, `%%sparkr`)
- NotebookUtils API parameters, return types, and module names (`fs`, `notebook`, `credentials`, `lakehouse`, `workspace`, `data`, `variableLibrary`, `session`)
- Path formats: ABFS for mount operations, relative paths for builtin/env access, OneLake conventions
- PySpark compatibility: Spark DataFrames vs Pandas, distributed vs local operations

##### Frontmatter

Write the YAML frontmatter with `name` and `description`:

- `name`: The skill name
- `description`: This is the primary triggering mechanism for your skill, and helps Claude understand when to use the skill.
  - Include both what the Skill does and specific triggers/contexts for when to use it.
  - Include all "when to use" information here - Not in the body. The body is only loaded after triggering, so "When to Use This Skill" sections in the body are not helpful to Claude.
  - Example description for a `docx` skill: "Comprehensive document creation, editing, and analysis with support for tracked changes, comments, formatting preservation, and text extraction. Use when Claude needs to work with professional documents (.docx files) for: (1) Creating new documents, (2) Modifying or editing content, (3) Working with tracked changes, (4) Adding comments, or any other document tasks"

Do not include any other fields in YAML frontmatter.

##### Body

Write instructions for using the skill and its bundled resources. Include:
- Clear usage examples with Fabric-specific code (validated against official docs)
- References to bundled scripts, assets, and documentation
- Any Fabric environment requirements or constraints
- Proper NotebookUtils API usage patterns

### Step 5: Iterate Based on Usage

After testing the skill in real Fabric Notebook workflows, iterate based on actual usage patterns.

**Iteration workflow:**

1. Use the skill on real Fabric data engineering tasks
2. Notice struggles, inefficiencies, or Fabric-specific issues (e.g., PySpark incompatibilities, missing lakehouse patterns)
3. Identify improvements to SKILL.md, scripts, references, or assets
4. Implement changes and test in notebook cells
5. If the skill is in `builtin/`, consider moving to `env/` when it becomes stable and useful for multiple notebooks

**Common iteration triggers in Fabric:**
- Script fails due to PySpark vs Pandas differences
- Missing lakehouse/warehouse access patterns
- Need for additional NotebookUtils examples
- Incomplete Fabric environment context in documentation
- Performance issues with Spark operations

### Step 6: Final Review

After completing the skill, do a final pass:

1. **Fabric code validated** — All Fabric-specific code was verified against official docs during writing (Step 4)
2. **Scripts tested** — All Python scripts run successfully in Fabric Notebook cells
3. **SKILL.md size** — Under 500 lines, follows progressive disclosure
4. **No duplication** — Information lives in either SKILL.md or references, not both

For skills with many Fabric components, consider delegating a thorough review to a sub-agent that reads all skill files and validates each Fabric component against official docs using `get_notebookutils_doc`, `get_fabric_doc`, or `microsoft_docs_search`.

**Reference docs:**
- [NotebookUtils API](https://learn.microsoft.com/en-us/fabric/data-engineering/notebook-utilities)
- [Magic Commands](https://learn.microsoft.com/en-us/fabric/data-engineering/author-execute-notebook#spark-session-configuration-magic-command)
- [Best Practices](https://learn.microsoft.com/en-us/fabric/data-engineering/spark-best-practices-development-monitoring)
