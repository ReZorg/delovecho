---
name: fabric-skill-reviewer
description: Review user-created skills for Fabric notebook related code and scripts. Use when asked to review, validate, or verify skills containing NotebookUtils APIs, %%configure, Spark configurations, or Fabric notebook-specific syntax.
---

# Skill Reviewer

Review skills containing Fabric notebook code against official Microsoft documentation.

## Workflow

When user asks to review a skill:

1. **Decide approach**
   - **Simple review (direct)**: If the skill is short and contains few Fabric notebook components, review it directly without a sub-agent.
   - **Complex review (sub-agent)**: If the skill is long, contains many components, or needs extensive doc validation, delegate to a `FabricNotebook` sub-agent (see template below).
2. **Present results** - Show the review report to the user

## Sub-Agent Instructions

Launch a `FabricNotebook` sub-agent with these instructions:

```
Review the skill at [SKILL_PATH] for Fabric notebook code correctness.

Steps:
1. Read all skill files (SKILL.md and everything in references/, scripts/, etc.)

2. Scan for Fabric notebook components:
   - NotebookUtils APIs (fs, notebook, credentials, lakehouse, workspace, data, variableLibrary, session)
   - Magic commands (%%configure, %%pyspark, %%sql, %pip, etc.)
   - Spark configurations and session settings
   - Path formats (ABFS, relative, OneLake)

3. For EACH Fabric notebook component found:
   - Use get_notebookutils_doc / get_fabric_doc tools if available
   - Or use microsoft_docs_search to find official documentation
   - Search: "Fabric notebook [API/command name]"
   - Validate syntax, parameters, usage patterns
   - Check for common mistakes and limitations
   - Use microsoft_docs_fetch for complete details if needed

4. Generate review report with:
   - Summary: total components found, overall status (✓ Pass / ⚠ Needs Revision)
   - Issues: component location, code snippet, problem, fix recommendation, doc reference
   - Best practices: %%configure placement, path formats, error handling, runtime version checks
   - Priority recommendations

Focus on Fabric-specific code only. Be concise and actionable.
```

## Common Issues to Check

The sub-agent should watch for:

- ❌ `%%configure` not in first cell
- ❌ Wrong path formats (Spark vs Python notebook)
- ❌ `notebookutils.fs.mount()` without ABFS path
- ...

## Documentation Links

- [NotebookUtils API Reference](https://learn.microsoft.com/en-us/fabric/data-engineering/notebook-utilities)
- [%%configure Magic Command](https://learn.microsoft.com/en-us/fabric/data-engineering/author-execute-notebook#spark-session-configuration-magic-command)
- [Best Practices](https://learn.microsoft.com/en-us/fabric/data-engineering/spark-best-practices-development-monitoring)
