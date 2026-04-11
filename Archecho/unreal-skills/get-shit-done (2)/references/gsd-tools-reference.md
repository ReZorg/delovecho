# gsd-tools.js CLI Reference

Full command reference for `node ~/.claude/get-shit-done/bin/gsd-tools.js <command> [args]`.

## State Management

| Command | Description |
|---------|-------------|
| `state load` | Load project config + state |
| `state update <field> <value>` | Update a STATE.md field |
| `state get [section]` | Get STATE.md content or section |
| `state patch --field val ...` | Batch update STATE.md fields |
| `state advance-plan` | Increment plan counter |
| `state record-metric --phase N --plan M --duration Xmin` | Record execution metrics |
| `state update-progress` | Recalculate progress bar |
| `state add-decision --summary "..." [--phase N] [--rationale "..."]` | Add decision |
| `state add-blocker --text "..."` | Add blocker |
| `state resolve-blocker --text "..."` | Remove blocker |
| `state record-session` | Update session continuity |
| `state-snapshot` | Structured parse of STATE.md as JSON |

## Phase Operations

| Command | Description |
|---------|-------------|
| `find-phase <phase>` | Find phase directory by number |
| `phase next-decimal <phase>` | Calculate next decimal phase number |
| `phase add <description>` | Append new phase to roadmap + create dir |
| `phase insert <after> <description>` | Insert decimal phase after existing |
| `phase remove <phase> [--force]` | Remove phase, renumber all subsequent |
| `phase complete <phase>` | Mark phase done, update state + roadmap |
| `phase-plan-index <phase>` | Index plans with waves and status |

## Roadmap Operations

| Command | Description |
|---------|-------------|
| `roadmap get-phase <phase>` | Extract phase section from ROADMAP.md |
| `roadmap analyze` | Full roadmap parse with disk status |

## Milestone Operations

| Command | Description |
|---------|-------------|
| `milestone complete <version> [--name <name>]` | Archive milestone |

## Init Commands (Used by Workflows)

| Command | Description |
|---------|-------------|
| `init new-project` | Initialize new-project context |
| `init plan-phase <N> [--include ...]` | Initialize plan-phase context with file contents |
| `init execute-phase <N>` | Initialize execute-phase context |
| `init map-codebase` | Initialize codebase mapping context |
| `init quick <description>` | Initialize quick task context |

## Git Operations

| Command | Description |
|---------|-------------|
| `commit <message> [--files f1 f2]` | Commit planning docs (respects commit_docs config) |

## Verification Suite

| Command | Description |
|---------|-------------|
| `verify plan-structure <file>` | Check PLAN.md structure + tasks |
| `verify phase-completeness <phase>` | Check all plans have summaries |
| `verify references <file>` | Check @-refs + paths resolve |
| `verify commits <h1> [h2] ...` | Batch verify commit hashes |
| `verify artifacts <plan-file>` | Check must_haves.artifacts |
| `verify key-links <plan-file>` | Check must_haves.key_links |

## Frontmatter CRUD

| Command | Description |
|---------|-------------|
| `frontmatter get <file> [--field k]` | Extract frontmatter as JSON |
| `frontmatter set <file> --field k --value jsonVal` | Update single field |
| `frontmatter merge <file> --data '{json}'` | Merge JSON into frontmatter |
| `frontmatter validate <file> --schema plan\|summary\|verification` | Validate required fields |

## Template Fill

| Command | Description |
|---------|-------------|
| `template fill summary --phase N [--plan M]` | Create pre-filled SUMMARY.md |
| `template fill plan --phase N [--plan M] [--type execute\|tdd]` | Create pre-filled PLAN.md |
| `template fill verification --phase N` | Create pre-filled VERIFICATION.md |

## Scaffolding

| Command | Description |
|---------|-------------|
| `scaffold context --phase <N>` | Create CONTEXT.md template |
| `scaffold uat --phase <N>` | Create UAT.md template |
| `scaffold verification --phase <N>` | Create VERIFICATION.md template |
| `scaffold phase-dir --phase <N> --name <name>` | Create phase directory |

## Utilities

| Command | Description |
|---------|-------------|
| `resolve-model <agent-type>` | Get model for agent based on profile |
| `generate-slug <text>` | Convert text to URL-safe slug |
| `current-timestamp [format]` | Get timestamp (full\|date\|filename) |
| `list-todos [area]` | Count and enumerate pending todos |
| `verify-path-exists <path>` | Check file/directory existence |
| `history-digest` | Aggregate all SUMMARY.md data |
| `summary-extract <path> [--fields]` | Extract structured data from SUMMARY.md |
| `progress [json\|table\|bar]` | Render progress in various formats |
| `validate consistency` | Check phase numbering, disk/roadmap sync |
| `todo complete <filename>` | Move todo from pending to completed |
| `websearch <query> [--limit N] [--freshness day\|week\|month]` | Search web via Brave API |
