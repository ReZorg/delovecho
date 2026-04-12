# Skillm Training Data Sources

## Overview

A Skillm learns from **execution traces** — records of successful action sequences observed across connectors and databases. This document catalogs available training sources and how to extract action sequences from each.

## Source 1: MCP Connector Tool Invocations

Every MCP tool call produces a result file in `/home/ubuntu/.mcp/tool-results/` or `/tmp/manus-mcp/`. These files contain timestamped records of tool invocations with inputs and outputs.

**Extraction**: Parse the result files to reconstruct action sequences. Each file name encodes `{timestamp}_{server}_{tool}.json`.

**Training value**: Defines the vocabulary and provides concrete parameter examples for each action verb.

## Source 2: Neon Database State Transitions

### deltecho-cognitive (Project: little-breeze-47283522)

The `dte_thoughts` table records cognitive processing phases with emotional valence and attention salience. Each thought belongs to a session and has a phase number, enabling reconstruction of the cognitive action sequence within a session.

**Extraction**: `SELECT session_id, phase, content, valence, arousal, salience FROM dte_thoughts ORDER BY session_id, phase`

**Training value**: Provides weighted training examples where high-salience, positive-valence sequences indicate successful cognitive workflows.

### regima-rag-knowledge (Project: summer-silence-47312919)

The `training_jobs` table records the state machine of knowledge ingestion: `queued → processing → completed/failed`. The `knowledge_sources` table records source types and statuses.

**Extraction**: `SELECT id, job_type, status, total_sources, processed_sources, total_chunks FROM training_jobs ORDER BY created_at`

**Training value**: Provides the RAG training pipeline as a canonical action sequence template.

### b2bkp-exchange-sync (Project: square-butterfly-04468397)

The `exchange_sync.sync_commands` table records sync operations across multiple users. The `exchange_sync.sync_log` table records outcomes with counts.

**Extraction**: `SELECT command, user_email, status, created_at FROM exchange_sync.sync_commands ORDER BY created_at`

**Training value**: Provides multi-tenant synchronization patterns with temporal ordering.

## Source 3: Existing Skill Definitions (63 skills)

Each skill in `/home/ubuntu/skills/*/SKILL.md` contains procedural workflows expressed as numbered steps. These are the highest-quality training data because they represent expert-curated action sequences.

**Extraction**: Parse SKILL.md files for numbered step lists, workflow diagrams, and command sequences.

**Training value**: HIGHEST — these are pre-validated procedural programs.

## Source 4: Meta Marketing Campaign Hierarchy

The Meta Marketing connector exposes a strict hierarchy: `ad_account → campaign → adset → ad → insights`. Traversing this hierarchy is a canonical DISCOVER drill-down pattern.

**Extraction**: Use `meta_marketing_get_ad_accounts`, then `get_campaigns`, then `get_adsets`, then `get_ads`, then `get_insights` to record the traversal.

**Training value**: Provides hierarchical navigation patterns with pagination.

## Training Data Schema

Each training example is a JSON record:

```json
{
  "id": "uuid",
  "source": "connector|database|skill",
  "source_id": "specific source identifier",
  "goal": "natural language description of what the sequence achieves",
  "sequence": [
    {
      "verb": "DISCOVER",
      "tool": "notion-search",
      "params": {"query": "..."},
      "result_summary": "found 3 pages"
    },
    {
      "verb": "INSPECT",
      "tool": "notion-fetch",
      "params": {"id": "..."},
      "result_summary": "retrieved page content"
    }
  ],
  "outcome": "success|failure",
  "weight": 1.0,
  "metadata": {
    "valence": 0.0,
    "salience": 0.5,
    "duration_ms": 1200,
    "connector": "notion"
  }
}
```
