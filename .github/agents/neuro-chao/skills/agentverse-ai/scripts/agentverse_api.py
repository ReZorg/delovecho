#!/usr/bin/env python3
"""
Agentverse API helper — thin wrapper around the Agentverse REST API.

Usage:
    python3 agentverse_api.py <command> [args...]

Commands:
    list-agents                         List all hosted agents
    get-agent <address>                 Get agent details
    get-code <address>                  Get agent source code
    update-code <address> <json_file>   Update agent code from a JSON file
    start <address>                     Start a hosted agent
    stop <address>                      Stop a hosted agent
    logs <address>                      Get latest agent logs
    rename <address> <new_name>         Rename a hosted agent
    create <name>                       Create a new hosted agent
    delete <address>                    Delete a hosted agent
    resolve <identifier>                Resolve agent/handle via Almanac
    almanac-recent [n]                  Browse n most recent Almanac agents
    registry [page] [size]              List agents in registry (v1 paginated)

Requires: AVAAPI environment variable set to your Agentverse API key.
"""

import os, sys, json, requests

API_KEY = os.environ.get("AVAAPI", "")
BASE = "https://agentverse.ai"
HDR = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}


def _req(method, path, **kw):
    r = requests.request(method, f"{BASE}{path}", headers=HDR, timeout=30, **kw)
    try:
        data = r.json()
    except Exception:
        data = r.text
    if not (200 <= r.status_code < 300):
        print(f"ERROR [{r.status_code}]: {json.dumps(data, indent=2, default=str)}", file=sys.stderr)
        sys.exit(1)
    return data


def cmd_list_agents():
    data = _req("GET", "/v1/hosting/agents")
    items = data if isinstance(data, list) else data.get("items", [])
    for a in items:
        status = "RUNNING" if a.get("running") else "stopped"
        print(f"  [{status:7s}] {a.get('name','(unnamed)'):30s}  {a['address']}")
    print(f"\nTotal: {len(items)} agent(s)")


def cmd_get_agent(addr):
    print(json.dumps(_req("GET", f"/v1/hosting/agents/{addr}"), indent=2, default=str))


def cmd_get_code(addr):
    data = _req("GET", f"/v1/hosting/agents/{addr}/code")
    code_str = data.get("code", "")
    try:
        files = json.loads(code_str) if isinstance(code_str, str) else code_str
        for f in files:
            print(f"\n=== {f['name']} ({f['language']}) ===")
            print(f["value"])
    except Exception:
        print(code_str)


def cmd_update_code(addr, json_file):
    with open(json_file) as fh:
        files = json.load(fh)
    code_str = json.dumps(files)
    data = _req("PUT", f"/v1/hosting/agents/{addr}/code", json={"code": code_str})
    print(f"Code updated. Digest: {data.get('digest', 'N/A')}")


def cmd_start(addr):
    data = _req("POST", f"/v1/hosting/agents/{addr}/start")
    print(f"Agent started. running={data.get('running')}")


def cmd_stop(addr):
    data = _req("POST", f"/v1/hosting/agents/{addr}/stop")
    print(f"Agent stopped. running={data.get('running')}")


def cmd_logs(addr):
    logs = _req("GET", f"/v1/hosting/agents/{addr}/logs/latest")
    if isinstance(logs, list):
        for entry in logs[:30]:
            ts = entry.get("log_timestamp", "")
            lvl = entry.get("log_level", "")
            msg = entry.get("log_entry", "")
            print(f"  [{ts}] {lvl:4s} | {msg}")
    else:
        print(json.dumps(logs, indent=2, default=str))


def cmd_rename(addr, name):
    _req("PUT", f"/v1/hosting/agents/{addr}", json={"name": name})
    print(f"Agent renamed to: {name}")


def cmd_create(name):
    data = _req("POST", "/v1/hosting/agents", json={"name": name})
    print(json.dumps(data, indent=2, default=str))


def cmd_delete(addr):
    _req("DELETE", f"/v1/hosting/agents/{addr}")
    print(f"Agent deleted: {addr}")


def cmd_resolve(identifier):
    data = _req("GET", f"/v1/almanac/agents/{identifier}")
    print(json.dumps(data, indent=2, default=str))


def cmd_almanac_recent(n=5):
    data = _req("GET", f"/v1/almanac/recent?num_agents={n}")
    if isinstance(data, list):
        for a in data:
            addr = a.get("address", "N/A")
            status = a.get("status", "N/A")
            protos = len(a.get("protocols", []))
            print(f"  {status:8s} | protocols={protos:2d} | {addr[:50]}...")
    else:
        print(json.dumps(data, indent=2, default=str))


def cmd_registry(page=1, size=10):
    data = _req("GET", f"/v1/agents?page={page}&size={size}")
    print(json.dumps(data, indent=2, default=str))


COMMANDS = {
    "list-agents": (cmd_list_agents, 0),
    "get-agent": (cmd_get_agent, 1),
    "get-code": (cmd_get_code, 1),
    "update-code": (cmd_update_code, 2),
    "start": (cmd_start, 1),
    "stop": (cmd_stop, 1),
    "logs": (cmd_logs, 1),
    "rename": (cmd_rename, 2),
    "create": (cmd_create, 1),
    "delete": (cmd_delete, 1),
    "resolve": (cmd_resolve, 1),
    "almanac-recent": (cmd_almanac_recent, 0),
    "registry": (cmd_registry, 0),
}

if __name__ == "__main__":
    if not API_KEY:
        print("ERROR: AVAAPI environment variable not set.", file=sys.stderr)
        sys.exit(1)
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        sys.exit(0)
    fn, min_args = COMMANDS[sys.argv[1]]
    args = sys.argv[2:]
    if len(args) < min_args:
        print(f"ERROR: '{sys.argv[1]}' requires {min_args} argument(s).", file=sys.stderr)
        sys.exit(1)
    fn(*args[:min_args + 2])
