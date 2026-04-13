---
name: vorticog
description: Develop, extend, and operate Vorticog — an agentic business simulation game engine with DreamCog AI storytelling integration and SimsFreePlay-inspired life simulation systems. Use when working on the ReZorg/vorticog repository, adding game features (companies, units, production, markets), building agentic simulation systems (agents, personas, emotions, relationships, events), integrating DreamCog personality models (Big Five, motivations, memories), world-building (worlds, locations, lore, timeline events), implementing Sims-style needs/action/relationship/skill subsystems from o9nn/simsfreeplay-ext, extending the tRPC API, modifying the Drizzle ORM schema, or debugging the full-stack TypeScript application. Triggers on mentions of vorticog, virtunomics, agentic business simulation, DreamCog integration, semi-autonomous agents, business simulation game engine, SimsFreePlay simulation, needs system, action queue, or life simulation.
---

# Vorticog

Vorticog (package name: virtunomics) is a full-stack agentic business simulation game engine combining business management (companies, units, production, markets, finance) with AI-driven semi-autonomous agents, DreamCog narrative storytelling, and SimsFreePlay-inspired life simulation systems. Built on the Manus WebDev scaffold (web-db-user).

**Repositories**: `ReZorg/vorticog` (main app, forked from `o9nn/vorticog`) + `o9nn/simsfreeplay-ext` (Python simulation library)

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, TypeScript, TailwindCSS v4, Radix UI (shadcn/ui), Recharts, wouter, tRPC client, Streamdown |
| Backend | Express, tRPC, Drizzle ORM, MySQL/TiDB, Manus OAuth |
| AI | invokeLLM() via Gemini 2.5 Flash (forge API), AIChatBox component |
| Build | Vite 7, esbuild, vite-plugin-manus-runtime |
| Testing | Vitest |
| Storage | S3-compatible via Manus forge proxy |
| Simulation Engine | Python 3.10+ (simsfreeplay-ext: needs, actions, relationships, skills) |

## Architecture Overview

The system has four interconnected layers:

**Business Simulation**: Companies own business units (office, store, factory, mine, farm, laboratory) in cities. Units have employees, inventory, and production queues. Resources flow through production recipes. A market system enables trading between companies. Financial transactions and a technology research tree drive progression.

**Agentic Simulation**: Semi-autonomous agents (customer, supplier, employee, partner, investor, competitor) have personas with motivational levels, emotional states (happiness, satisfaction, stress, loyalty, trust), needs (financial, security, recognition, autonomy, social), and character traits. Agents form relationships, join groups and communities, and participate in events that cascade emotional and relationship impacts.

**DreamCog Integration**: Extends agents with Big Five personality (OCEAN), communication style attributes, behavioral tendencies, motivations (short/long-term goals, core values), and memories (with emotional impact and importance). Adds world-building: worlds with genre/rules, hierarchical locations, lore entries, historical timeline events, and scheduled future events with condition-based triggers.

**SimsFreePlay Simulation Engine** (`o9nn/simsfreeplay-ext`): A Python library providing the behavioral engine for agent autonomy. Four subsystems: NeedsSystem (6 decaying needs: hunger, energy, hygiene, social, fun, bladder), ActionQueue (priority queue with 10 action templates producing need/skill/relationship effects), RelationshipSystem (friendship -100 to +100, romance 0-100, 16 interaction types, threshold-based type progression from stranger to spouse), and SkillSystem (15 skills across 5 categories, level 0-10 with XP scaling). The Agent class wires these together with callback chains: action completion fulfills needs and grants skill XP, critical needs auto-queue urgent actions, and an AgentManager handles population-level batch updates.

## Development Workflow

### Clone and Setup

```bash
gh repo clone ReZorg/vorticog
cd vorticog
pnpm install
cp .env.example .env   # Configure DATABASE_URL and API keys
npm run db:push         # Apply migrations
npm run dev             # Start dev server at http://localhost:5000
```

### Adding a New Feature

1. **Schema**: Define tables in `drizzle/schema.ts` with Drizzle ORM. Add relations. Export Select and Insert types.
2. **Database functions**: Add CRUD functions in `server/db.ts`. Import schema types.
3. **API routes**: Add tRPC router in `server/routers.ts`. Use `protectedProcedure` for auth-required endpoints. Validate input with Zod.
4. **Frontend**: Add page in `client/src/pages/`. Register route in `App.tsx`. Use tRPC hooks from `@/lib/trpc`.
5. **Tests**: Add test file in `server/`. Run `npm run test`.
6. **Migrate**: Run `npm run db:push` to generate and apply migrations.

### Key Files to Modify

| Task | File(s) |
|---|---|
| Add/modify tables | `drizzle/schema.ts` |
| Add database functions | `server/db.ts` |
| Add API endpoints | `server/routers.ts` |
| Add pages/routes | `client/src/pages/`, `client/src/App.tsx` |
| Add UI components | `client/src/components/` |
| Configure environment | `server/_core/env.ts`, `.env` |
| Use LLM | `server/_core/llm.ts` → `invokeLLM()` |
| Use storage | `server/storage.ts` → `storagePut()`, `storageGet()` |

### Agent Creation Pattern

Create a fully-modeled agent in this order:

```typescript
// 1. Create base agent
const agent = await trpc.agent.create.mutate({
  type: "employee", name: "Elena", personaId: 1, cityId: 1, companyId: myCompanyId
});
// 2. Add Big Five personality
await trpc.personality.create.mutate({
  agentId: agent.id, openness: 85, conscientiousness: 70,
  extraversion: 45, agreeableness: 80, neuroticism: 35, leadership: 75, empathy: 85
});
// 3. Add traits
await trpc.agent.addTrait.mutate({agentId: agent.id, traitId: 1, intensity: 80});
// 4. Add motivations
await trpc.motivation.create.mutate({
  agentId: agent.id, motivationType: "long_term",
  description: "Become CTO", priority: 9
});
// 5. Record initial memories
await trpc.memory.create.mutate({
  agentId: agent.id, memoryType: "achievement",
  content: "Hired as lead engineer", importance: 7, memoryDate: new Date()
});
```

### Event Processing Pattern

```typescript
// Create event with impacts
const event = await trpc.event.create.mutate({
  type: "negotiation", initiatorAgentId: 1, targetAgentId: 2,
  title: "Contract Negotiation", scheduledAt: new Date(),
  emotionalImpact: {satisfaction: 5, stress: 10},
  relationshipImpact: {agentIds: [1, 2], strengthChange: 10, positivityChange: 5}
});
// Process when ready — applies impacts, creates history snapshots
await trpc.event.process.mutate({eventId: event.id});
```

## References

- **Database schema details**: See `references/database-schema.md` for all 27+ tables, columns, and relations
- **Full API reference**: See `references/api-reference.md` for all tRPC router endpoints and LLM/storage APIs
- **Agentic simulation deep-dive**: See `references/agentic-simulation.md` for agent architecture, event processing pipeline, DreamCog personality model, and world-building system
- **SimsFreePlay simulation engine**: See `references/simsfreeplay-simulation.md` for needs/action/relationship/skill subsystems, Python API, action templates, interaction effects, and mapping strategy to Vorticog's TypeScript backend
- **Project structure**: See `references/project-structure.md` for directory layout, build commands, environment variables, and coding conventions

## Current Status

Implemented and tested: core business simulation (companies, units, production, markets, finance, leaderboard), full agentic simulation (agents, personas, traits, relationships, groups, communities, events, triggers, history), and DreamCog integration (Big Five personality, motivations, memories, relationship events, worlds, locations, lore, world events, scheduled events).

Not yet implemented: supply chain logistics, quality control, technology research tree UI, contract system, game turn processing loop, and agent decision-making AI. The SimsFreePlay simulation engine (Python) provides the behavioral patterns for the unimplemented game turn loop and agent decision AI — needs decay, autonomous action selection, and population-level batch updates.

## Important Notes

- The `server/_core/` directory is the Manus WebDev scaffold framework layer. Avoid modifying unless extending core capabilities.
- Relationships store `agent1Id < agent2Id` (lower ID first) to prevent duplicates.
- All agent emotional values are 0-100. Event impacts are additive and should be clamped.
- The LLM uses `gemini-2.5-flash` with 32k max tokens and 128 thinking budget tokens.
- Import shared types from `@shared/types` (re-exports from `drizzle/schema.ts`).
- The SimsFreePlay simulation library (`o9nn/simsfreeplay-ext`) is a Python package. To integrate, either port subsystems to TypeScript (recommended for type safety) or run as a sidecar service.
