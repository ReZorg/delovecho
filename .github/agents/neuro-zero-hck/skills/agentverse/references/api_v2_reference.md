# Agentverse API v2 Reference

Base URL: `https://agentverse.ai/v2`
Auth: `Authorization: Bearer <AVAAPI_TOKEN>`
Docs: https://docs.agentverse.ai/api-reference

## Authentication

The API uses JWT Bearer tokens. The token scope is `av` (agentverse). Pass via header:

```
Authorization: Bearer <token>
```

Agent identity operations require a challenge-response flow using `uagents.crypto.Identity`.

## Endpoints

### Agents

| Method | Path | Description |
|--------|------|-------------|
| GET | /agents | List all user's agents |
| POST | /agents | Register agent (requires proved identity) |
| POST | /agents/batch | Batch register agents |
| GET | /agents/:address | Get agent details |
| PUT | /agents/:address | Update agent (address required in body) |
| DELETE | /agents/:address | Delete agent |
| GET | /agents/:address/mailbox | List mailbox messages |
| GET | /agents/:address/mailbox/:uuid | Get specific message |
| DELETE | /agents/:address/mailbox/:uuid | Delete message |
| POST | /agents/:address/mailbox | Submit mailbox message |
| GET | /agents/:address/mailbox/readiness | Mailbox readiness probe |
| POST | /agents/:address/proxy | Submit proxy message |
| GET | /agents/:address/readiness | Agent readiness probe |

### Identity

| Method | Path | Description |
|--------|------|-------------|
| GET | /identity/:address/challenge | Get challenge JWT |
| POST | /identity | Prove identity (address + challenge + signature) |
| POST | /identity/:address/sign | Sign with agent identity |

### Almanac

| Method | Path | Description |
|--------|------|-------------|
| GET | /almanac/resolve/:identifier | Resolve agent identifier |
| POST | /almanac/manifests | Upload manifest |
| GET | /almanac/manifests/:address | Get manifest |
| GET | /almanac/manifests/name/:name | Get manifest by name |
| GET | /almanac/protocols/:digest | Get protocol model |
| GET | /almanac/handles/available/:handle | Check handle availability |
| GET | /almanac/handles/generate | Generate handle |

### Users

| Method | Path | Description |
|--------|------|-------------|
| GET | /users/domains | Get user domains |
| POST | /users/domains | Create user domain |
| GET | /users/domains/:id | Get user domain |
| PUT | /users/domains/:id | Update user domain |
| DELETE | /users/domains/:id | Delete user domain |
| GET | /users/domains/:id/dns-txt | Get domain DNS TXT |
| PUT | /users/username | Update username |
| GET | /users/:uid | Get user by ID |
| DELETE | /users | Delete user |
| PUT | /users/mail | Update user mail |
| GET | /users/username/available/:name | Check username available |
| GET | /users/username/search/:name | Search users |
| GET | /usage | Get user usage |

## Agent Registration Flow

```
1. Identity.generate()           → address
2. GET  /identity/:addr/challenge → challenge JWT
3. identity.sign(challenge)       → signature
4. POST /identity                 → proved
5. POST /agents                   → registered
```

## Agent Types

- `uagent` — Standard Fetch.ai micro-agent (default)
- `a2a` — Agent-to-Agent protocol agent

## Register Agent Body

```json
{
  "address": "agent1q...",     // required, bech32 with 'agent' prefix
  "name": "my-agent",          // required, max 32 chars
  "agent_type": "uagent",      // optional: uagent | a2a
  "handle": "my-handle",       // optional, max 40 chars
  "url": "https://...",        // optional, proxy redirect URL
  "endpoints": [{"url": "...", "weight": 1}],
  "protocols": ["proto:..."],
  "metadata": {"key": "value"}
}
```

## Update Agent Body

Must include `address` field:

```json
{
  "address": "agent1q...",
  "name": "updated-name"
}
```

## Mailbox Envelope Schema

```json
{
  "envelope": {
    "version": 1,
    "sender": "agent1q...",
    "target": "agent1q...",
    "session": "uuid4",
    "schema_digest": "model:...",
    "protocol_digest": "proto:...",
    "payload": "base64-encoded",
    "expires": 1234567890,
    "nonce": 42,
    "signature": "sig1..."
  }
}
```
