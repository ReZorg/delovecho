---
name: vorterebus
description: Vorticog agentic business simulation with Erebus 350M local creative writing engine for agent narrative generation, event storytelling, and DreamCog world-building prose. Composes vorticog (agentic business simulation + DreamCog + SimsFreePlay behavioral engine) with erebus-350 (OPT-350M-Erebus fine-tuned creative writing model) via a FastAPI sidecar that translates agent states into genre-tagged narrative prose. Use when building Vorticog features that require creative narrative output, generating agent backstories, producing event descriptions, creating memory narratives, writing world lore, or running the Erebus narrative sidecar alongside the Vorticog dev server. Triggers on mentions of vorterebus, Vorticog Erebus, agent narrative generation, Erebus storytelling sidecar, or creative writing simulation engine.
---

# Vorterebus

Vorterebus composes **vorticog** (agentic business simulation game engine) with **erebus-350** (KoboldAI OPT-350M-Erebus creative writing model) into a dual-LLM architecture where Gemini handles structured reasoning and Erebus handles narrative prose generation.

## Composition

| Component | Skill | Role |
|---|---|---|
| Business + Agent Simulation | vorticog | Companies, units, agents, events, DreamCog personality, SimsFreePlay needs/actions/relationships |
| Structured Reasoning | vorticog (`invokeLLM`) | JSON output, function calling, decision logic via Gemini 2.5 Flash |
| Creative Narrative Engine | erebus-350 (`invokeErebus`) | Genre-tagged prose for agent narratives, event descriptions, memories, world lore via local OPT-350M-Erebus |

## When to Use Each LLM

Use `invokeLLM()` (Gemini) for structured tasks: agent decision-making AI, JSON schema outputs, tool/function calling, game turn processing logic, and any task requiring >2048 tokens of context.

Use `invokeErebus()` (Erebus sidecar) for creative tasks: agent backstory generation, event narrative descriptions, memory prose, world lore entries, relationship event storytelling, and any task requiring genre-aware fiction writing.

## Quick Start

```bash
# 1. Start the Erebus narrative sidecar (requires: pip install fastapi uvicorn transformers torch)
python /home/ubuntu/skills/vorterebus/scripts/erebus_narrative_engine.py --port 8350 --device cpu

# 2. In another terminal, start Vorticog
cd vorticog && npm run dev

# 3. Test the sidecar
curl http://localhost:8350/health
```

## Narrative Generation Endpoints

The sidecar at `localhost:8350` exposes four endpoints that auto-construct Erebus `[Genre: ...]` tags from Vorticog data:

| Endpoint | Input | Output |
|---|---|---|
| `POST /agent-narrative` | Agent object (name, type, emotions, Big Five, traits, motivations, memories, context) | Genre-tagged character prose |
| `POST /event-description` | Event object (type, title, initiator, target, impacts, world context) | Narrative event description |
| `POST /memory-narrative` | Agent name + memory type + context string | First-person memory passage |
| `POST /generate` | Raw prompt with manual `[Genre: ...]` tags | Free-form creative text |

## Integration Pattern

Add `server/erebus.ts` to the Vorticog backend:

```typescript
const EREBUS_URL = process.env.EREBUS_URL || "http://localhost:8350";

export async function invokeErebus(
  endpoint: "/generate" | "/agent-narrative" | "/event-description" | "/memory-narrative",
  body: Record<string, unknown>
) {
  const res = await fetch(`${EREBUS_URL}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`Erebus error: ${res.status} ${await res.text()}`);
  return res.json();
}
```

Then call from routers:

```typescript
// In server/routers.ts — generate narrative when creating a memory
const { narrative } = await invokeErebus("/memory-narrative", {
  agent_name: agent.name,
  memory_type: "achievement",
  context: "Promoted to senior engineer after leading the infrastructure overhaul",
});
await db.createMemory({ agentId: agent.id, content: narrative, ... });
```

## Genre Auto-Mapping

The sidecar maps Vorticog agent types and emotional states to Erebus genre tags automatically:

| Vorticog State | Erebus Genre Tags |
|---|---|
| employee agent | character study |
| customer / supplier / partner | business fiction |
| competitor / investor | corporate thriller |
| stress > 70 | + drama |
| happiness > 80 | + feel-good |
| negotiation event | business fiction, drama |
| conflict event | thriller, drama |
| betrayal event | thriller, psychological |
| discovery event | adventure, mystery |

## Parent Skill References

For Vorticog internals (schema, API, agents, SimsFreePlay), read the vorticog skill and its references. For Erebus model architecture (OPT-350M weights, tensor shapes, GGUF conversion), read the erebus-350 skill and its references.

## Bundled Resources

- **`references/erebus-integration.md`**: Full integration reference — architecture diagram, all endpoint schemas with examples, TypeScript client code, sampling parameters per use case, prompt engineering details, and limitations.
- **`scripts/erebus_narrative_engine.py`**: The FastAPI sidecar service that loads OPT-350M-Erebus and serves the four narrative generation endpoints.

## Important Notes

- Erebus 350M has a 2048-token context. Keep prompts under ~500 tokens to leave room for generation.
- The model has a strong NSFW bias. Post-process or filter outputs for age-appropriate game content.
- The sidecar runs on port 8350 by default. Add `EREBUS_URL=http://localhost:8350` to the Vorticog `.env`.
- For CPU-only deployment, use `--device cpu`. The 662 MB F16 model fits comfortably in RAM.
