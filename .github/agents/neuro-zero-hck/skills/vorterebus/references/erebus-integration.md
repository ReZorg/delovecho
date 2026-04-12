# Erebus 350M Integration Reference

Read this reference when integrating the Erebus 350M creative writing model as a narrative engine for Vorticog agent storytelling, event descriptions, and memory generation.

## Composition: vorticog ⊗ erebus-350

This skill composes two parent skills into a single operational unit:

| Parent Skill | Role in Composition |
|---|---|
| **vorticog** | Agentic business simulation engine — companies, agents, events, DreamCog personality, SimsFreePlay behavioral systems, tRPC API, Drizzle ORM |
| **erebus-350** | OPT-350M-Erebus creative writing model — genre-tagged prose generation, 24-layer decoder-only transformer, 2048-token context |

The Vorticog base skill uses `invokeLLM()` (Gemini 2.5 Flash) for structured reasoning, function calling, and JSON schema outputs. In this composition, Erebus 350M replaces Gemini as the **creative writing engine** for generating narrative prose — agent backstories, event descriptions, memory narratives, and world lore. Use `invokeErebus()` for all narrative generation and `invokeLLM()` for structured/JSON tasks.

| Capability | Gemini 2.5 Flash (`invokeLLM`) | Erebus 350M (`invokeErebus`) |
|---|---|---|
| Structured output / JSON | Yes | No |
| Function calling / tools | Yes | No |
| Creative prose generation | Generic | Specialized (fine-tuned on fiction) |
| Genre-tagged storytelling | No | Yes (`[Genre: ...]` tags) |
| Context window | 32k tokens | 2048 tokens |
| Deployment | Cloud API | Local sidecar (CPU/GPU) |
| Cost | Per-token API billing | Free (local inference) |

## Architecture

The Erebus Narrative Engine runs as a Python FastAPI sidecar service alongside the Vorticog Node.js backend. Communication is via HTTP REST.

```
┌─────────────────────────────────────────────┐
│ Vorticog (Node.js / Express / tRPC)         │
│                                             │
│  server/routers.ts                          │
│    ├── invokeLLM()  → Gemini 2.5 Flash     │  (structured reasoning)
│    └── invokeErebus() → localhost:8350      │  (creative prose)
│                                             │
└──────────────────┬──────────────────────────┘
                   │ HTTP POST
                   ▼
┌─────────────────────────────────────────────┐
│ Erebus Narrative Engine (Python / FastAPI)   │
│ Port 8350                                   │
│                                             │
│  POST /generate          (raw generation)   │
│  POST /agent-narrative   (agent → prose)    │
│  POST /event-description (event → prose)    │
│  POST /memory-narrative  (memory → prose)   │
│  GET  /health                               │
└─────────────────────────────────────────────┘
```

## Endpoints

### POST /generate

Raw text generation with full control over Erebus tags and sampling parameters.

```json
{
  "prompt": "[Genre: fantasy, romance]\nThe knight entered the chamber",
  "max_new_tokens": 200,
  "temperature": 1.2,
  "top_p": 0.95,
  "top_k": 50,
  "repetition_penalty": 1.12
}
```

### POST /agent-narrative

Generate a narrative passage for a Vorticog agent. The engine automatically constructs Erebus genre tags from the agent's type, emotional state, and personality.

```json
{
  "agent": {
    "name": "Elena",
    "type": "employee",
    "persona": {"ambition": 85, "caution": 30, "social": 70, "analytical": 60},
    "emotions": {"happiness": 65, "satisfaction": 50, "stress": 80, "loyalty": 70, "trust": 55},
    "personality": {"openness": 85, "conscientiousness": 70, "extraversion": 45, "agreeableness": 80, "neuroticism": 35},
    "traits": [{"name": "Ambitious", "intensity": 90}, {"name": "Empathetic", "intensity": 75}],
    "motivations": [{"description": "Become CTO", "priority": 9}],
    "recent_memories": [{"content": "Closed the biggest deal of the quarter", "memoryType": "achievement"}],
    "context": "Elena walks into the boardroom for the quarterly review."
  },
  "max_new_tokens": 250,
  "temperature": 1.2
}
```

### POST /event-description

Generate a prose description for a Vorticog event. Genre tags are auto-selected from event type.

```json
{
  "event": {
    "type": "negotiation",
    "title": "Contract Negotiation with Apex Corp",
    "initiator_name": "Elena",
    "target_name": "Marcus",
    "emotional_impact": {"satisfaction": 5, "stress": 10},
    "relationship_impact": {"strengthChange": 10, "positivityChange": 5},
    "world_context": "The city's economy is in recession."
  },
  "max_new_tokens": 200,
  "temperature": 1.1
}
```

### POST /memory-narrative

Generate a first-person memory narrative for an agent.

```json
{
  "agent_name": "Elena",
  "memory_type": "achievement",
  "context": "Hired as lead engineer at Nexus Technologies after a grueling interview process",
  "max_new_tokens": 150,
  "temperature": 1.0
}
```

## TypeScript Client Integration

Add an `invokeErebus()` helper in the Vorticog backend:

```typescript
// server/erebus.ts
const EREBUS_URL = process.env.EREBUS_URL || "http://localhost:8350";

export async function invokeErebus(
  endpoint: "/generate" | "/agent-narrative" | "/event-description" | "/memory-narrative",
  body: Record<string, unknown>
): Promise<{ narrative?: string; description?: string; generated_text?: string }> {
  const res = await fetch(`${EREBUS_URL}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`Erebus error: ${res.status} ${await res.text()}`);
  return res.json();
}
```

Add `EREBUS_URL` to the environment:

```
# .env
EREBUS_URL=http://localhost:8350
```

## Prompt Engineering: Auto-Mapped Genre Tags

The engine auto-maps Vorticog agent types and emotional states to Erebus genre tags:

| Agent Type / Event Type | Auto-Selected Genres |
|---|---|
| customer, supplier, partner | business fiction |
| competitor, investor | corporate thriller |
| employee (default) | character study |
| High stress (>70) | + drama |
| High happiness (>80) | + feel-good |
| negotiation event | business fiction, drama |
| conflict event | thriller, drama |
| celebration event | feel-good, slice of life |
| betrayal event | thriller, psychological |
| discovery event | adventure, mystery |
| crisis event | drama, thriller |

## Sampling Parameters by Use Case

| Use Case | Temperature | Top-P | Repetition Penalty | Max Tokens |
|---|---|---|---|---|
| Agent narrative | 1.2 | 0.95 | 1.12 | 250 |
| Event description | 1.1 | 0.95 | 1.12 | 200 |
| Memory narrative | 1.0 | 0.95 | 1.10 | 150 |
| World lore | 1.3 | 0.97 | 1.15 | 300 |
| Raw creative | 1.2–2.0 | 0.90–0.99 | 1.10–1.15 | variable |

## Startup

Start the sidecar before or alongside the Vorticog dev server:

```bash
# Terminal 1: Erebus narrative engine
python scripts/erebus_narrative_engine.py --port 8350 --device cpu

# Terminal 2: Vorticog dev server
cd vorticog && npm run dev
```

Health check: `curl http://localhost:8350/health`

## Limitations

Erebus 350M has a 2048-token context window. Keep prompts under ~500 tokens to leave room for generation. The model has a strong NSFW bias; post-process or filter outputs for age-appropriate content in the game UI. For structured data extraction or complex reasoning, continue using `invokeLLM()` (Gemini).
