# Vorticog Database Schema Reference

Read this reference when working on database operations, schema changes, migrations, or understanding table relationships.

## Table of Contents

1. [Core Business Tables](#core-business-tables)
2. [Agentic Simulation Tables](#agentic-simulation-tables)
3. [DreamCog Integration Tables](#dreamcog-integration-tables)
4. [Key Relations](#key-relations)

## Core Business Tables

| Table | Purpose | Key Columns |
|---|---|---|
| `users` | Player accounts | id, openId, name, email, role |
| `companies` | Player businesses | id, userId, name, cash, reputation |
| `business_units` | Facilities (office/store/factory/mine/farm/lab) | id, companyId, type, cityId, level, efficiency |
| `cities` | Locations for units | id, name, country, population, wealthIndex, taxRate, lat/lng |
| `employees` | Workers at units | id, businessUnitId, count, qualification, salary, morale |
| `inventory` | Resources at units | id, businessUnitId, resourceTypeId, quantity, quality |
| `resource_types` | Resource definitions | id, code, name, category (raw_material/intermediate/finished_good/equipment/consumable), basePrice |
| `production_recipes` | Manufacturing formulas | id, unitType, outputResourceId, inputResources (JSON), laborRequired, timeRequired |
| `production_queue` | Active production | id, businessUnitId, recipeId, quantity, progress |
| `market_listings` | Items for sale | id, companyId, resourceTypeId, quantity, pricePerUnit, cityId |
| `transactions` | Financial history | id, type (purchase/sale/salary/tax/construction/maintenance), companyId, amount |
| `notifications` | Player alerts | id, userId, type, title, message, isRead |
| `technologies` | Research tree | id, code, name, category, researchCost, prerequisites (JSON), effects (JSON) |
| `game_state` | Global game config | id, currentTurn, turnDuration, settings (JSON) |

## Agentic Simulation Tables

| Table | Purpose | Key Columns |
|---|---|---|
| `character_personas` | Personality templates | id, code, ambitionLevel/cautionLevel/socialLevel/analyticalLevel (0-100), communicationStyle, decisionSpeed |
| `character_traits` | Behavioral characteristics | id, code, category (professional/social/cognitive/emotional), positiveEffect |
| `agents` | Simulation entities | id, type (customer/supplier/employee/partner/investor/competitor), personaId, companyId, cityId, happiness/satisfaction/stress/loyalty/trust (0-100), financialNeed/securityNeed/recognitionNeed/autonomyNeed/socialNeed (0-100) |
| `agent_traits` | Agent-trait M:N | id, agentId, traitId, intensity (0-100) |
| `relationships` | Agent connections | id, agent1Id, agent2Id, type (business/personal/professional/familial/competitive), strength/positivity/frequency (0-100), status |
| `agent_groups` | Group structures | id, name, type (department/team/union/association/club/network), cohesion/influence/morale (0-100) |
| `group_memberships` | Agent-group M:N | id, groupId, agentId, role (leader/core_member/member/associate) |
| `communities` | City social structures | id, name, cityId, type (residential/business/industrial/cultural/virtual), prosperity/harmony/growth (0-100) |
| `community_memberships` | Agent-community M:N | id, communityId, agentId, influence, reputation |
| `agent_events` | Time-sensitive occurrences | id, type (interaction/transaction/milestone/crisis/celebration/conflict/negotiation/collaboration), initiatorAgentId, emotionalImpact (JSON), relationshipImpact (JSON), status |
| `event_triggers` | Auto event rules | id, eventType, conditions (JSON), eventTemplate (JSON), priority |
| `agent_histories` | State snapshots | id, agentId, happiness/satisfaction/stress/loyalty/trust, eventId |

## DreamCog Integration Tables

| Table | Purpose | Key Columns |
|---|---|---|
| `agent_big_five_personality` | Big Five model | agentId (unique), openness/conscientiousness/extraversion/agreeableness/neuroticism (0-100), formalityLevel/verbosityLevel/emotionalExpression/humorLevel/directnessLevel (0-100), impulsiveness/riskTaking/empathy/leadership/independence (0-100) |
| `agent_motivations` | Goal tracking | agentId, motivationType (short_term/long_term/core_value), priority (1-10), progress (0-100%) |
| `agent_memories` | Experience tracking | agentId, memoryType (event/interaction/knowledge/emotion/skill/trauma/achievement), emotionalImpact (-100 to +100), importance (1-10), isRepressed |
| `relationship_events` | Relationship history | relationshipId, eventType (first_meeting/conflict/bonding/betrayal/reconciliation/milestone), impactOnTrust/impactOnAffection/impactOnRespect (-100 to +100) |
| `worlds` | Narrative contexts | userId, name, genre, timePeriod, technologyLevel, magicSystem, rules (JSON) |
| `locations` | Hierarchical places | worldId, locationType (city/building/wilderness/dungeon/realm/dimension), parentLocationId, attributes (JSON) |
| `lore_entries` | Knowledge database | worldId, category (11 types), title, content, isPublic, isSecret, tags (JSON) |
| `world_events` | Historical timeline | worldId, eventType (8 types), importance (1-10), eventDate (flexible string), involvedAgentIds (JSON) |
| `scheduled_world_events` | Future events | worldId, scheduledFor, eventTrigger (JSON: time/condition/manual), priority, isRecurring, status |

## Key Relations

Agents connect to the business layer through `companyId` and `businessUnitId`. Relationships are bidirectional but stored once (agent1Id < agent2Id). Events cascade emotional and relationship impacts when processed via `processAgentEvent()`. Worlds contain locations (hierarchical), lore entries, world events, and scheduled events. All tables use Drizzle ORM with full TypeScript type inference.
