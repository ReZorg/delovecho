# Vorticog API Reference

Read this reference when working on tRPC routers, adding endpoints, or understanding the API surface.

## Table of Contents

1. [Business Management Routers](#business-management-routers)
2. [Agentic Simulation Routers](#agentic-simulation-routers)
3. [DreamCog Integration Routers](#dreamcog-integration-routers)
4. [LLM Integration](#llm-integration)
5. [Storage API](#storage-api)

## Business Management Routers

### `company` Router
```
company.mine          → query()                    → Get current user's company
company.create        → mutate({name, description?}) → Create company ($1M start)
company.byId          → query({id})                → Get company by ID
company.all           → query()                    → All companies (leaderboard)
```

### `businessUnit` Router
```
businessUnit.list     → query()                    → List user's units
businessUnit.byId     → query({id})                → Get unit by ID
businessUnit.create   → mutate({type, name, cityId, size?}) → Build unit (deducts cost)
businessUnit.update   → mutate({id, name?, isActive?})      → Update unit
businessUnit.employees → query({unitId})            → Get employees
businessUnit.updateEmployees → mutate({unitId, count, salary}) → Hire/update
businessUnit.inventory → query({unitId})            → Get inventory
```

### `market` Router
```
market.list           → query({cityId?, resourceTypeId?}) → Active listings
market.create         → mutate({businessUnitId, resourceTypeId, quantity, pricePerUnit}) → List item
market.purchase       → mutate({listingId, quantity}) → Buy from market
market.cancel         → mutate({id})                → Cancel listing
```

### `production` Router
```
production.recipes    → query({unitType?})          → Available recipes
production.queue      → query({businessUnitId})     → Active production
production.start      → mutate({businessUnitId, recipeId, quantity}) → Start production
```

### Other Business Routers
```
transaction.list      → query({limit?})             → Company transactions
notification.list     → query()                     → User notifications
notification.markRead → mutate({id})                → Mark as read
game.state            → query()                     → Current game state
```

## Agentic Simulation Routers

### `persona` Router
```
persona.list          → query()                     → All character personas
persona.byId          → query({id})                 → Persona by ID
```

### `trait` Router
```
trait.list            → query()                     → All character traits
trait.byCategory      → query({category})           → Traits by category
```

### `agent` Router
```
agent.create          → mutate({type, name, personaId, cityId, companyId?, businessUnitId?})
agent.byId            → query({id})
agent.byType          → query({type})
agent.byCompany       → query({companyId})
agent.byBusinessUnit  → query({businessUnitId})
agent.update          → mutate({id, ...fields})
agent.updateEmotions  → mutate({id, emotions: {happiness?, satisfaction?, stress?, loyalty?, trust?}})
agent.traits          → query({agentId})
agent.addTrait        → mutate({agentId, traitId, intensity})
agent.history         → query({agentId, limit?})
```

### `relationship` Router
```
relationship.create   → mutate({agent1Id, agent2Id, type})
relationship.between  → query({agent1Id, agent2Id})
relationship.byAgent  → query({agentId})
relationship.recordInteraction → mutate({agent1Id, agent2Id, strengthChange, positivityChange})
```

### `group` Router
```
group.create          → mutate({name, type, description?, companyId?, cityId?})
group.byId            → query({id})
group.byCompany       → query({companyId})
group.members         → query({groupId})
group.addMember       → mutate({groupId, agentId, role?})
group.removeMember    → mutate({groupId, agentId})
```

### `community` Router
```
community.create      → mutate({name, cityId, type, description?})
community.byId        → query({id})
community.byCity      → query({cityId})
community.members     → query({communityId})
community.addMember   → mutate({communityId, agentId})
```

### `event` Router
```
event.create          → mutate({type, initiatorAgentId, targetAgentId?, title, scheduledAt, emotionalImpact?, relationshipImpact?})
event.byId            → query({id})
event.byAgent         → query({agentId})
event.scheduled       → query()
event.process         → mutate({eventId})           → Apply impacts, update status
```

## DreamCog Integration Routers

### `personality` Router
```
personality.get       → query({agentId})            → Big Five profile
personality.create    → mutate({agentId, openness, conscientiousness, extraversion, agreeableness, neuroticism, ...})
personality.update    → mutate({agentId, ...fields})
```

### `motivation` Router
```
motivation.create     → mutate({agentId, motivationType, description, priority?})
motivation.byAgent    → query({agentId, activeOnly?})
motivation.update     → mutate({id, progress?, isActive?, priority?})
```

### `memory` Router
```
memory.create         → mutate({agentId, memoryType, content, emotionalImpact?, importance?, eventId?, relatedAgentId?, locationId?, memoryDate})
memory.byAgent        → query({agentId, limit?})
```

### `relationshipEvent` Router
```
relationshipEvent.create → mutate({relationshipId, eventType, description, impactOnTrust?, impactOnAffection?, impactOnRespect?, eventDate})
relationshipEvent.byRelationship → query({relationshipId})
```

### World Building Routers
```
world.create          → mutate({name, description?, genre?, timePeriod?, ...})
world.byId            → query({id})
world.list            → query()                     → User's worlds
world.update          → mutate({id, ...fields})

location.create       → mutate({worldId, name, locationType, parentLocationId?, attributes?})
location.byId         → query({id})
location.byWorld      → query({worldId})
location.subLocations → query({parentLocationId})

lore.create           → mutate({worldId, category, title, content, ...})
lore.byId             → query({id})
lore.byWorld          → query({worldId, category?})

worldEvent.create     → mutate({worldId, title, eventType, importance?, eventDate, ...})
worldEvent.byId       → query({id})
worldEvent.byWorld    → query({worldId})

scheduledWorldEvent.create  → mutate({worldId, eventName, scheduledFor, eventTrigger?, ...})
scheduledWorldEvent.byId    → query({id})
scheduledWorldEvent.pending → query({worldId})
scheduledWorldEvent.update  → mutate({id, status?, ...})
```

## LLM Integration

`invokeLLM(params)` in `server/_core/llm.ts` calls Gemini 2.5 Flash via the Manus forge API:
- Model: `gemini-2.5-flash` with 32k max tokens, 128 thinking budget
- Supports: messages, tools/function calling, structured output (JSON schema), response format
- Auth: `BUILT_IN_FORGE_API_KEY` env var
- Endpoint: `BUILT_IN_FORGE_API_URL` or `https://forge.manus.im/v1/chat/completions`

## Storage API

`server/storage.ts` provides S3-compatible storage via the Manus forge proxy:
- `storagePut(relKey, data, contentType)` → Upload file, returns `{key, url}`
- `storageGet(relKey)` → Get download URL, returns `{key, url}`
