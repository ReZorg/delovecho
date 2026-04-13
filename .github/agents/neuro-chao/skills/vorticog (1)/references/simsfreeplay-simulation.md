# SimsFreePlay Simulation Extension Reference

Read this reference when working on the Sims-inspired life simulation layer, implementing the needs/action/relationship/skill subsystems, or integrating the Python simulation library with Vorticog's TypeScript backend.

**Repository**: `o9nn/simsfreeplay-ext` — Python simulation library extracted from Sims FreePlay APK patterns.

## Table of Contents

1. [Overview](#overview)
2. [Needs System](#needs-system)
3. [Action Queue System](#action-queue-system)
4. [Relationship System](#relationship-system)
5. [Skill Progression System](#skill-progression-system)
6. [Agent Integration](#agent-integration)
7. [Mapping to Vorticog](#mapping-to-vorticog)

## Overview

The `simulation/` package provides four interconnected subsystems implementing Sims-style agent behavior. Each subsystem operates independently but is wired together through the `Agent` class via callback chains: action completion triggers need fulfillment and skill XP gain, critical needs auto-queue urgent actions, and interactions update relationship scores.

```
Agent
├── NeedsSystem     → 6 needs decaying over time
├── ActionQueue     → priority queue with effects
├── RelationshipSystem → friendship/romance/family tracking
└── SkillSystem     → 15 skills with XP progression
```

## Needs System

Six core needs, each with configurable decay rate (points per game-hour):

| Need | Decay Rate | Purpose |
|---|---|---|
| BLADDER | 10.0 | Fastest decay, highest urgency |
| HUNGER | 8.0 | Food requirement |
| FUN | 7.0 | Entertainment need |
| ENERGY | 6.0 | Sleep/rest requirement |
| SOCIAL | 5.0 | Interaction need |
| HYGIENE | 4.0 | Slowest decay |

All needs range 0-100, start at 100. Critical threshold: 20 (triggers urgent auto-action). Warning threshold: 40 (triggers normal priority action). Callbacks fire on state transitions: `on_critical`, `on_warning`, `on_fulfilled`.

```python
from simulation.needs import NeedsSystem, NeedType, NeedConfig

system = NeedsSystem()
system.update(1.0)                           # 1 game-hour decay
system.fulfill(NeedType.HUNGER, 40.0)        # Replenish hunger
critical = system.get_critical_needs()       # [NeedType.BLADDER, ...]
satisfaction = system.get_overall_satisfaction()  # 0.0-1.0
```

## Action Queue System

Queue-based execution with 10 pre-defined action templates:

| Action | Type | Duration (hrs) | Need Effects | Skill Effects | Relationship Effects |
|---|---|---|---|---|---|
| eat | OBJECT | 0.5 | hunger +40, bladder -10 | — | — |
| sleep | AUTONOMOUS | 8.0 | energy +100 | — | — |
| shower | OBJECT | 0.5 | hygiene +50 | — | — |
| use_bathroom | OBJECT | 0.1 | bladder +100 | — | — |
| chat | SOCIAL | 0.5 | social +20, fun +10 | — | friendship +5 |
| play_game | OBJECT | 1.0 | fun +30 | — | — |
| watch_tv | OBJECT | 2.0 | fun +20, energy -5 | — | — |
| cook | OBJECT | 1.0 | — | cooking +2 | — |
| exercise | AUTONOMOUS | 1.0 | energy -20, fun +10, hygiene -15 | fitness +3 | — |
| read | OBJECT | 1.0 | fun +15 | logic +2 | — |

Actions have priority (1-10), interruptibility flag, and support target agents/objects. Queue max size: 10. Actions progress via `advance(delta_time)` and complete when progress reaches 1.0.

```python
from simulation.actions import ActionQueue, Action, ActionType, ActionEffect

queue = ActionQueue()
queue.add_action_by_name("eat")
queue.add_action_by_name("chat", target_agent_id="bob_123")
effects = queue.update(0.5)  # Returns ActionEffect on completion
queue.interrupt_for(urgent_action)  # Push current back, start urgent
```

## Relationship System

Dual-axis relationship tracking with threshold-based type determination:

| Type | Friendship Threshold | Romance Threshold |
|---|---|---|
| ENEMY | <= -50 | — |
| RIVAL | <= -20 | — |
| STRANGER | < 10 | — |
| ACQUAINTANCE | >= 10 | — |
| FRIEND | >= 30 | — |
| GOOD_FRIEND | >= 60 | — |
| BEST_FRIEND | >= 85 | — |
| ROMANTIC_INTEREST | — | >= 30 |
| PARTNER | — | >= 60 |
| SPOUSE | — | >= 90 |
| FAMILY | (flag) | — |

16 pre-defined interaction effects (friendship/romance change): greet (+2/0), chat (+5/0), deep_conversation (+10/+2), joke (+3/+1), compliment (+5/+3), flirt (+2/+8), hug (+8/+5), kiss (+5/+15), gift (+10/+5), help (+8/+2), argue (-15/-5), insult (-20/-10), betray (-50/-30), apologize (+10/+3), work_together (+7/0), play_together (+8/+2).

Relationships decay toward neutral over time (friendship_decay=0.1/hr, romance_decay=0.05/hr).

## Skill Progression System

15 skills across 5 categories, all with identical default config:

| Category | Skills |
|---|---|
| Life | cooking, gardening, fishing, handiness |
| Social | charisma, comedy |
| Creative | writing, painting, music, photography |
| Mental | logic, programming |
| Physical | fitness, dancing |
| Misc | gaming |

Progression: max level 10, base 100 XP/level, 1.5x scaling per level. Effectiveness multiplier: 0.5 (level 0) to 2.0 (level 10). Diminishing XP returns at higher levels via `1.0 / (1.0 + level * 0.1)` modifier.

## Agent Integration

The `Agent` class wires all subsystems together:

```python
from simulation import Agent

agent = Agent(name="Alice")
agent.queue_action("eat")
agent.queue_action("chat", target_agent_id="bob_123")
agent.update(1.0)  # Advances time, decays needs, processes actions

# Autonomous behavior
action = agent.get_autonomous_action()  # Returns best action for current needs
agent.auto_act()  # Queue autonomous action

# Inter-agent interaction
alice.interact_with(bob, "deep_conversation")  # Updates both agents' relationships

# State
agent.overall_wellbeing  # 0-1 (70% needs + 30% skills)
agent.to_state()  # Serialize to AgentState dataclass
```

`AgentManager` handles population-level operations: `update_all(delta_time)`, `auto_act_all()`, `get_agents_by_wellbeing()`, `get_population_stats()`.

## Mapping to Vorticog

The SimsFreePlay simulation library provides the **behavioral engine** that Vorticog's database-backed agent system currently lacks. The mapping strategy:

| SFP Subsystem | Vorticog Target | Integration Approach |
|---|---|---|
| NeedsSystem (6 needs) | `agents` table (5 emotional states + 5 needs) | Map SFP needs to Vorticog's 10-dimensional state. HUNGER→financialNeed, ENERGY→stress(inverse), SOCIAL→socialNeed, FUN→happiness, HYGIENE→satisfaction, BLADDER→autonomyNeed |
| ActionQueue | `agent_events` + `production_queue` | Action templates become event templates. Queue processing drives the game turn loop |
| RelationshipSystem | `relationships` table + `relationship_events` | Friendship→strength, romance→positivity. Interaction effects→relationship event impacts |
| SkillSystem | `technologies` + `agent_motivations` | Skill types map to agent capabilities. Progression drives motivation progress |
| Agent.auto_act() | `event_triggers` + agent decision AI | Autonomous behavior engine for the unimplemented agent decision-making AI |
| AgentManager | Population queries in `server/db.ts` | Batch update pattern for simulation tick processing |

To integrate, either: (a) port the Python subsystems to TypeScript and embed in the Vorticog server, or (b) run the Python simulation as a sidecar service called from tRPC endpoints. Option (a) is recommended for tighter type safety and single-process deployment.
