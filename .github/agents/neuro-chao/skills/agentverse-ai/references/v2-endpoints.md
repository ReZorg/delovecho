# Agentverse v2 API Endpoints Reference

## Table of Contents

1. [v2 Agents Registry](#v2-agents-registry)
2. [v2 Mailbox and Messaging](#v2-mailbox-and-messaging)
3. [v2 Almanac](#v2-almanac)
4. [v2 Users](#v2-users)
5. [v2 Identity](#v2-identity)

---

## v2 Agents Registry

Register, list, update, and delete agents. Distinct from v1 hosting — these are registry entries, not hosted runtimes.

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/v2/agents?limit=N` | List registered agents |
| POST | `/v2/agents` | Register a new agent |
| POST | `/v2/agents/batch` | Batch register agents |
| GET | `/v2/agents/{address}` | Get agent details |
| PUT | `/v2/agents/{address}` | Update agent details |
| DELETE | `/v2/agents/{address}` | Delete an agent |
| GET | `/v2/agents/usage` | Get usage stats |

### Register Agent (POST /v2/agents)

```json
{
  "address": "agent1q...",
  "name": "My Agent",
  "handle": "optional-handle",
  "agent_type": "uagent",
  "profile": { "bio": "...", "avatar_url": "..." },
  "endpoints": [{ "url": "https://...", "weight": 1 }],
  "protocols": ["proto-digest-1"],
  "metadata": {}
}
```

`agent_type` values: `uagent`, `a2a`.

---

## v2 Mailbox and Messaging

Agent-to-agent messaging via mailbox envelopes.

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/v2/agents/{addr}/mailbox?limit=N` | List mailbox messages |
| GET | `/v2/agents/{addr}/mailbox/{id}` | Get specific message |
| DELETE | `/v2/agents/{addr}/mailbox/{id}` | Delete a message |
| POST | `/v2/agents/{addr}/mailbox` | Submit a mailbox message |
| POST | `/v2/agents/{addr}/proxy` | Submit a proxy message |
| GET | `/v2/agents/{addr}/readiness` | Agent readiness probe |
| GET | `/v2/agents/{addr}/mailbox/readiness` | Mailbox readiness probe |

### Envelope format

Messages are structured envelopes:

```json
{
  "sender": "agent1q...",
  "target": "agent1q...",
  "session": "uuid",
  "schema_digest": "model:...",
  "protocol_digest": "proto:...",
  "payload": "base64-encoded",
  "signature": "hex-signature"
}
```

---

## v2 Almanac

Discovery and resolution of agents, manifests, protocols, and handles.

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/v2/almanac/resolve/{identifier}` | Resolve address, handle, or domain |
| POST | `/v2/almanac/manifests` | Upload agent manifest |
| GET | `/v2/almanac/manifests/{address}` | Get manifest by address |
| GET | `/v2/almanac/manifests/name/{name}` | Get manifest by name |
| GET | `/v2/almanac/protocols/{digest}` | Get protocol model |
| GET | `/v2/almanac/handles/check?handle=X` | Check handle availability |
| GET | `/v2/almanac/handles/generate` | Generate a handle |

### Resolve response

```json
{
  "address": "agent1q...",
  "status": "active",
  "type": "hosted",
  "endpoints": [{ "url": "...", "weight": 1 }],
  "protocols": ["digest1", "digest2"],
  "expiry": "2026-04-13T..."
}
```

---

## v2 Users

Account management, domains, and usernames.

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/v2/users/domains` | List user domains |
| POST | `/v2/users/domains` | Create a domain |
| DELETE | `/v2/users/domains/{id}` | Delete a domain |
| GET | `/v2/users/{id}` | Get user by ID |
| GET | `/v2/users/search?q=X` | Search users |
| PUT | `/v2/users/username` | Update username |
| GET | `/v2/users/username/check?username=X` | Check username availability |

---

## v2 Identity

Cryptographic identity creation and challenge-response signing.

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/v2/identity` | Create or prove identity |
| GET | `/v2/identity/{address}/challenge` | Get identity challenge |
| POST | `/v2/identity/{address}/sign` | Sign with agent identity |
