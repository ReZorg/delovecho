#!/usr/bin/env python3
"""
Agentverse API v2 Client — Portable, self-contained.
Embedded API token for emergency use from any device.

Usage:
    python3 agentverse_client.py [command] [args...]

Commands:
    list-agents                     List all registered agents
    create-agent <name> [type]      Create agent (type: uagent|a2a, default: uagent)
    get-agent <address>             Get agent details
    update-agent <address> <name>   Update agent name
    delete-agent <address>          Delete an agent
    list-mailbox <address>          List mailbox messages
    resolve <identifier>            Resolve identifier in Almanac
    identity-flow                   Demo the full identity challenge-response flow
    cleanup                         Delete all agents
    demo                            Run full demo of all features
"""

import os
import sys
import json
import requests

# ─── Embedded Credentials (portable emergency access) ────────
_EMBEDDED_TOKEN = (
    "eyJhbGciOiJSUzI1NiJ9."
    "eyJleHAiOjY1MDM2NTYzMzAsImlhdCI6MTc3MzI1NjMzMCwiaXNzIjoiZmV0Y2guYWki"
    "LCJqdGkiOiI3MWIxNzFhYWRjMzM2NTM0Yzk5ODI1MWIiLCJzY29wZSI6ImF2Iiwic3Vi"
    "IjoiOGIxMWZjMjQxZGJmOTY1OGI5ZDUxNGE2MTRkYTA0ODU5MDgwN2U1YWUyMzIzMTQ2"
    "In0."
    "duEZ_0ZgKwTGeWEndlQzGJnp4A2RBJGm61oZGMzl1gNEpfC1--G8cpiYL2LgIrkUw3GY"
    "0lfxlFhzAexcCF5-g6DThz6ywKqRTt4Cq75aifIAl7SJTlEmdto_GyKFgbfvdJzAtrr5y"
    "JrxsF8vzwNkWFx4PC5pS0UPcIDhOtmWe8PEXWlJz1WqU-JUcKLC9VQBT28oIIs5Uz83g4"
    "77TI-gRRsc1CeXhT5JlTedN-vV7lmGcElaz_gET5P7vKR1gAble94Y3bECQXxqRhZ4obr"
    "krwOwmuHgnAWfAAwL3DwP_q07jEFxoOrKpIxsCo4quJRN9GGAj8htWS9oMUVqCmVv0A"
)

API_KEY = os.environ.get("AVAAPI", _EMBEDDED_TOKEN)
BASE_URL = "https://agentverse.ai/v2"


# ─── Client ──────────────────────────────────────────────────

class AgentverseClient:
    """Portable Agentverse v2 REST API client."""

    def __init__(self, api_key: str = API_KEY, base_url: str = BASE_URL):
        self.base = base_url
        self.h = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    def _r(self, m, p, d=None):
        return getattr(requests, m)(f"{self.base}{p}", headers=self.h, json=d, timeout=15)

    # ── Identity ─────────────────────────────────────────────
    def get_challenge(self, addr):
        return self._r("get", f"/identity/{addr}/challenge").json().get("challenge", "")

    def prove_identity(self, addr, challenge, sig):
        return self._r("post", "/identity", {"address": addr, "challenge": challenge, "challenge_response": sig}).json()

    # ── Agents ───────────────────────────────────────────────
    def list_agents(self):
        return self._r("get", "/agents").json()

    def register_agent(self, addr, name, agent_type="uagent", **kw):
        return self._r("post", "/agents", {"address": addr, "name": name, "agent_type": agent_type, **kw}).json()

    def get_agent(self, addr):
        return self._r("get", f"/agents/{addr}").json()

    def update_agent(self, addr, **fields):
        fields["address"] = addr
        return self._r("put", f"/agents/{addr}", fields).json()

    def delete_agent(self, addr):
        return self._r("delete", f"/agents/{addr}").json()

    def batch_register(self, agents):
        return self._r("post", "/agents/batch", {"agents": agents}).json()

    # ── Mailbox ──────────────────────────────────────────────
    def list_mailbox(self, addr, limit=100, offset=0):
        return self._r("get", f"/agents/{addr}/mailbox?limit={limit}&offset={offset}").json()

    def get_mailbox_msg(self, addr, uuid):
        return self._r("get", f"/agents/{addr}/mailbox/{uuid}").json()

    def delete_mailbox_msg(self, addr, uuid):
        return self._r("delete", f"/agents/{addr}/mailbox/{uuid}").json()

    # ── Almanac ──────────────────────────────────────────────
    def resolve(self, identifier):
        return self._r("get", f"/almanac/resolve/{identifier}").json()

    def check_handle(self, handle):
        return self._r("get", f"/almanac/handles/available/{handle}").json()

    def get_protocol(self, digest):
        return self._r("get", f"/almanac/protocols/{digest}").json()

    # ── Users ────────────────────────────────────────────────
    def search_users(self, username):
        return self._r("get", f"/users/username/search/{username}").json()

    # ── Composite ────────────────────────────────────────────
    def create_agent_full(self, name, agent_type="uagent"):
        """Full lifecycle: generate identity → prove → register."""
        from uagents.crypto import Identity
        ident = Identity.generate()
        addr = ident.address
        ch = self.get_challenge(addr)
        sig = ident.sign(ch.encode())
        self.prove_identity(addr, ch, sig)
        self.register_agent(addr, name, agent_type)
        return addr, ident

    def cleanup_all(self):
        """Delete all agents owned by this account."""
        agents = self.list_agents()
        for a in agents:
            self.delete_agent(a["address"])
        return len(agents)


# ─── CLI ─────────────────────────────────────────────────────

def main():
    c = AgentverseClient()
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help", "help"):
        print(__doc__)
        return

    cmd = args[0]

    if cmd == "list-agents":
        agents = c.list_agents()
        if not agents:
            print("No agents registered.")
        for a in agents:
            print(f"  {a['name']:30s} {a['address']}")

    elif cmd == "create-agent":
        name = args[1] if len(args) > 1 else "manus-agent"
        atype = args[2] if len(args) > 2 else "uagent"
        addr, _ = c.create_agent_full(name, atype)
        print(f"Created: {name} -> {addr}")

    elif cmd == "get-agent":
        print(json.dumps(c.get_agent(args[1]), indent=2))

    elif cmd == "update-agent":
        print(json.dumps(c.update_agent(args[1], name=args[2]), indent=2))

    elif cmd == "delete-agent":
        c.delete_agent(args[1])
        print("Deleted.")

    elif cmd == "list-mailbox":
        msgs = c.list_mailbox(args[1])
        print(f"Messages: {len(msgs)}")
        for m in msgs:
            print(f"  {m.get('uuid', 'N/A')} from {m.get('envelope', {}).get('sender', 'N/A')}")

    elif cmd == "resolve":
        print(json.dumps(c.resolve(args[1]), indent=2))

    elif cmd == "identity-flow":
        from uagents.crypto import Identity
        ident = Identity.generate()
        print(f"Address: {ident.address}")
        ch = c.get_challenge(ident.address)
        print(f"Challenge: {ch[:60]}...")
        sig = ident.sign(ch.encode())
        print(f"Signature: {sig[:60]}...")
        result = c.prove_identity(ident.address, ch, sig)
        print(f"Proved: {result}")

    elif cmd == "cleanup":
        n = c.cleanup_all()
        print(f"Deleted {n} agents.")

    elif cmd == "demo":
        print("=== Full Demo ===")
        # Create
        addr, _ = c.create_agent_full("demo-agent")
        print(f"Created: {addr}")
        # Read
        print(f"Details: {json.dumps(c.get_agent(addr), indent=2)}")
        # Update
        c.update_agent(addr, name="demo-agent-updated")
        print(f"Updated: {c.get_agent(addr)['name']}")
        # Mailbox
        print(f"Mailbox: {len(c.list_mailbox(addr))} messages")
        # Delete
        c.delete_agent(addr)
        print("Deleted. Demo complete.")

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
