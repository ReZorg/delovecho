# Agentic Simulation System Reference

Read this reference when working on agent behavior, event processing, relationship dynamics, or the DreamCog personality/world-building systems.

## Table of Contents

1. [Agent Architecture](#agent-architecture)
2. [Event Processing Pipeline](#event-processing-pipeline)
3. [Relationship Management](#relationship-management)
4. [DreamCog Personality Model](#dreamcog-personality-model)
5. [World Building System](#world-building-system)
6. [Common Patterns](#common-patterns)

## Agent Architecture

Agents are semi-autonomous entities combining three layers:

**Layer 1 — Persona** (template): ambition/caution/social/analytical levels (0-100), communication style (formal/casual/aggressive/passive/diplomatic), decision speed (impulsive to very_slow). Five pre-seeded: Ambitious Leader, Cautious Analyst, Social Connector, Aggressive Competitor, Diplomatic Mediator.

**Layer 2 — Emotional State** (dynamic): happiness, satisfaction, stress, loyalty, trust (all 0-100). Plus five needs: financial, security, recognition, autonomy, social (0-100, higher = greater need).

**Layer 3 — Big Five Personality** (DreamCog): openness, conscientiousness, extraversion, agreeableness, neuroticism (0-100). Plus communication attributes (formality, verbosity, emotional expression, humor, directness) and behavioral tendencies (impulsiveness, risk-taking, empathy, leadership, independence).

Agents also accumulate traits (with intensity 0-100), motivations (short_term/long_term/core_value with priority and progress), and memories (7 types with emotional impact and importance).

## Event Processing Pipeline

When `event.process` is called:

1. Retrieve event with emotional and relationship impact JSON
2. Apply emotional impacts to participating agents (additive to current values, clamped 0-100)
3. Apply relationship impacts (strength and positivity changes)
4. Create agent history snapshots for affected agents
5. Update event status to "completed"

Event triggers define conditions that auto-generate events:
```typescript
conditions: [{
  type: "threshold" | "time" | "relationship" | "emotion",
  metric: string,
  operator: ">" | "<" | "==" | "!=" | "between",
  value: number | string | number[]
}]
```

## Relationship Management

Relationships are stored once with `agent1Id < agent2Id` (lower ID first). Track strength, positivity, frequency (0-100), interaction count, and status (active/dormant/strained/broken).

`recordRelationshipInteraction` increments interaction count and applies strength/positivity changes.

Relationship events (DreamCog) track significant moments: first_meeting, conflict, bonding, betrayal, reconciliation, milestone — each with impact on trust, affection, respect (-100 to +100).

## DreamCog Personality Model

The Big Five personality extends the base persona system. Create after agent creation:

```typescript
// Create agent first
const agent = await trpc.agent.create.mutate({type, name, personaId, cityId});
// Then add Big Five profile
await trpc.personality.create.mutate({agentId: agent.id, openness: 85, ...});
// Add motivations
await trpc.motivation.create.mutate({agentId: agent.id, motivationType: "long_term", description: "...", priority: 9});
// Record memories
await trpc.memory.create.mutate({agentId: agent.id, memoryType: "achievement", content: "...", importance: 8, memoryDate: new Date()});
```

## World Building System

Worlds provide narrative context. Hierarchy: World → Locations (hierarchical via parentLocationId) → Lore Entries + World Events + Scheduled Events.

Location types: city, building, wilderness, dungeon, realm, dimension. Lore categories: history, legend, culture, religion, politics, science, magic, species, language, artifact. World event types: battle, discovery, political, natural, magical, social, economic.

Scheduled world events support three trigger types: time-based, condition-based, and manual. They can be recurring and have priority ordering.

## Common Patterns

**Creating a full character**: agent → Big Five personality → traits → motivations → initial memories.

**Running a simulation tick**: query scheduled events due → process each event → check event triggers → generate new events → record history snapshots.

**Building a game world**: create world → add locations (hierarchical) → add lore entries → create world events (timeline) → schedule future events.
