---
name: agentverse
description: Interact with the Fetch.ai Agentverse REST API v2 for autonomous agent management, identity proving, mailbox messaging, and Almanac resolution. Use for creating/managing agents on agentverse.ai, proving agent identity via challenge-response, sending/receiving mailbox messages, resolving agents in the Almanac, and any Fetch.ai agent ecosystem operation. Triggers on mentions of Agentverse, Fetch.ai agents, uagents, agent mailbox, Almanac resolve, agent identity, or AVAAPI.
---

# Agentverse

Portable skill for the Fetch.ai Agentverse v2 REST API. Includes embedded API token for emergency access from any device.

## Quick Start

Run the bundled CLI client directly:

```bash
python3 /home/ubuntu/skills/agentverse/scripts/agentverse_client.py list-agents
python3 /home/ubuntu/skills/agentverse/scripts/agentverse_client.py create-agent my-agent uagent
python3 /home/ubuntu/skills/agentverse/scripts/agentverse_client.py demo
```

Or import as a library:

```python
sys.path.insert(0, "/home/ubuntu/skills/agentverse/scripts")
from agentverse_client import AgentverseClient
c = AgentverseClient()
agents = c.list_agents()
addr, ident = c.create_agent_full("my-agent", "uagent")
```

## Credentials

The embedded token is baked into `scripts/agentverse_client.py` as `_EMBEDDED_TOKEN`. The env var `AVAAPI` overrides it when set. Token details:

| Field | Value |
|-------|-------|
| Issuer | fetch.ai |
| Scope | av (agentverse) |
| Subject | 8b11fc241dbf9658b9d514a614da04859... |

## Core Workflows

### Agent Lifecycle (Create, Read, Update, Delete)

```python
c = AgentverseClient()
addr, ident = c.create_agent_full("my-agent")  # identity + register
agent = c.get_agent(addr)                       # read
c.update_agent(addr, name="renamed")            # update
c.delete_agent(addr)                            # delete
```

`create_agent_full` handles the full identity challenge-response flow internally. Requires `pip install uagents`.

### Identity Challenge-Response (Manual)

```python
from uagents.crypto import Identity
ident = Identity.generate()
challenge = c.get_challenge(ident.address)
sig = ident.sign(challenge.encode())
c.prove_identity(ident.address, challenge, sig)
```

### Mailbox Operations

```python
messages = c.list_mailbox(addr)
msg = c.get_mailbox_msg(addr, uuid)
c.delete_mailbox_msg(addr, uuid)
```

### Almanac Resolution

```python
result = c.resolve("agent1q...")
```

### Batch Operations

```python
c.batch_register([{"address": addr1, "name": "agent-1"}, {"address": addr2, "name": "agent-2"}])
c.cleanup_all()  # delete all agents
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `list-agents` | List all registered agents |
| `create-agent <name> [type]` | Create agent (uagent or a2a) |
| `get-agent <address>` | Get agent details |
| `update-agent <address> <name>` | Update agent name |
| `delete-agent <address>` | Delete an agent |
| `list-mailbox <address>` | List mailbox messages |
| `resolve <identifier>` | Resolve in Almanac |
| `identity-flow` | Demo identity challenge-response |
| `cleanup` | Delete all agents |
| `demo` | Run full feature demo |

## Agent Types

- `uagent` — Standard Fetch.ai micro-agent (default)
- `a2a` — Agent-to-Agent protocol agent

## API Reference

Read `references/api_v2_reference.md` for the complete endpoint map, request/response schemas, and envelope format.

## Dependencies

```bash
pip install requests uagents
```

`requests` is needed for all operations. `uagents` is needed only for identity generation and signing (agent creation).

## Error Handling

- 401: Token expired or wrong scope. Rotate token at https://agentverse.ai profile.
- 404 on register: Identity not proved yet. Run challenge-response first.
- 422: Missing required fields. Check `address` is bech32 with `agent` prefix.
- 500 on sign: Server-side issue with `/identity/:address/sign` endpoint.
