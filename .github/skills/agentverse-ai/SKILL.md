---
name: agentverse-ai
description: Interact with the Agentverse (Fetch.ai) REST API for managing hosted AI agents, the Almanac global agent directory, agent-to-agent messaging, and the agent registry. Use when creating, deploying, starting, stopping, or monitoring agents on Agentverse, resolving agent addresses via the Almanac, updating agent source code, retrieving execution logs, or performing any programmatic operation against agentverse.ai. Triggers on mentions of Agentverse, Fetch.ai agents, uagents, Almanac, hosted agents, agent mailbox, or agentverse.ai.
---

# Agentverse AI

Manage hosted AI agents, the Almanac directory, and agent messaging on the Fetch.ai Agentverse platform via REST API.

## Authentication

All requests require `Authorization: Bearer <AVAAPI>` header. The `AVAAPI` environment variable contains the API key. Base URL: `https://agentverse.ai`.

## Helper Script

Run `python3 /home/ubuntu/skills/agentverse-ai/scripts/agentverse_api.py <command> [args]` for common operations:

| Command | Args | Purpose |
|---------|------|---------|
| `list-agents` | | List all hosted agents with status |
| `get-agent` | `<address>` | Get agent details as JSON |
| `get-code` | `<address>` | Print agent source code files |
| `update-code` | `<address> <json_file>` | Deploy code from a JSON file |
| `start` | `<address>` | Start a hosted agent |
| `stop` | `<address>` | Stop a hosted agent |
| `logs` | `<address>` | Get latest execution logs |
| `rename` | `<address> <name>` | Rename an agent |
| `create` | `<name>` | Create a new hosted agent |
| `delete` | `<address>` | Delete a hosted agent |
| `resolve` | `<identifier>` | Resolve agent via Almanac |
| `almanac-recent` | `[n]` | Browse n recent Almanac agents |
| `registry` | `[page] [size]` | List registry agents (paginated) |

## v1 Hosting API (Primary)

Full lifecycle management for hosted agents running the `uagents` Python framework.

### Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/v1/hosting/agents` | List hosted agents |
| POST | `/v1/hosting/agents` | Create agent (free tier: 8 max) |
| GET | `/v1/hosting/agents/{addr}` | Get agent details |
| PUT | `/v1/hosting/agents/{addr}` | Update metadata (e.g. name) |
| DELETE | `/v1/hosting/agents/{addr}` | Delete agent |
| GET | `/v1/hosting/agents/{addr}/code` | Get source code + digest |
| PUT | `/v1/hosting/agents/{addr}/code` | Deploy new code |
| POST | `/v1/hosting/agents/{addr}/start` | Start agent |
| POST | `/v1/hosting/agents/{addr}/stop` | Stop agent |
| GET | `/v1/hosting/agents/{addr}/logs/latest` | Get execution logs |

### Code Format

Agent code is a **JSON-stringified array** of file objects (not a raw array):

```python
import json, requests

files = [
    {"language": "plaintext", "name": ".env", "value": ""},
    {"language": "python", "name": "agent.py", "value": "from uagents import Agent, Context\n..."}
]
code_str = json.dumps(files)  # Must be stringified

requests.put(
    f"https://agentverse.ai/v1/hosting/agents/{address}/code",
    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    json={"code": code_str}
)
```

Reading code returns `{"digest": "sha256...", "code": "<json-string>"}`. Parse with `json.loads(data["code"])`.

### Agent Lifecycle

Standard workflow: create/list -> update code -> start -> monitor logs -> stop.

```python
import os, json, requests, time

KEY = os.environ["AVAAPI"]
BASE = "https://agentverse.ai"
HDR = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

# 1. List agents
agents = requests.get(f"{BASE}/v1/hosting/agents", headers=HDR).json()
addr = agents["items"][0]["address"]

# 2. Deploy code
code = json.dumps([{"language":"python","name":"agent.py","value":"from uagents import Agent, Context\nagent = Agent()\n@agent.on_event('startup')\nasync def hello(ctx: Context):\n    ctx.logger.info('Hello!')\nif __name__=='__main__':\n    agent.run()\n"}])
requests.put(f"{BASE}/v1/hosting/agents/{addr}/code", headers=HDR, json={"code": code})

# 3. Start
requests.post(f"{BASE}/v1/hosting/agents/{addr}/start", headers=HDR)

# 4. Logs (wait for startup)
time.sleep(5)
logs = requests.get(f"{BASE}/v1/hosting/agents/{addr}/logs/latest", headers=HDR).json()
for entry in logs:
    print(f"[{entry['log_timestamp']}] {entry['log_level']} | {entry['log_entry']}")

# 5. Stop
requests.post(f"{BASE}/v1/hosting/agents/{addr}/stop", headers=HDR)
```

## v1 Almanac API

Global agent directory for discovery and resolution.

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/v1/almanac/agents/{addr}` | Resolve agent by address |
| GET | `/v1/almanac/recent?num_agents=N` | Browse recent agents |

Resolve response includes `status` (active/offline), `type` (hosted/local/mailbox/proxy/custom), `endpoints`, `protocols`, and `expiry`.

## v1 Registry

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/v1/agents?page=P&size=S` | Paginated agent list with total count |

## v2 API

For v2 endpoints covering agent registry, mailbox/messaging, Almanac manifests/handles/protocols, users, and identity, read `references/v2-endpoints.md`.

## Key Technical Notes

- Agent addresses use **bech32** encoding with `agent1q` prefix.
- Free tier limit: **8 hosted agents**. HTTP 403 when exceeded.
- Code must be submitted as a **JSON string** (stringified array), not a raw array. This is the most common integration mistake.
- Starting an agent triggers automatic **Almanac registration**.
- Log entries have `log_level` (info/debg/erro) and `log_type` (system/user).
- The v1 Hosting API manages runtimes; v2 Agents API manages registry entries and mailboxes. They serve different purposes.
