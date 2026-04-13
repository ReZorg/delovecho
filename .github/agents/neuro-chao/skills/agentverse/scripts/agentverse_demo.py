#!/usr/bin/env python3
"""
Agentverse API v2 - Comprehensive Demo Script
===============================================
Demonstrates all working features of the Fetch.ai Agentverse REST API.

Platform: https://agentverse.ai
Docs:     https://docs.agentverse.ai/api-reference

Requirements:
    pip install requests uagents

Usage:
    export AVAAPI="your-api-token-here"
    python3 agentverse_demo.py
"""

import os
import sys
import json
import time
import requests
from dataclasses import dataclass
from typing import Optional

# ─────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────

API_KEY = os.environ.get("AVAAPI", "")
BASE_URL = "https://agentverse.ai/v2"

if not API_KEY:
    print("ERROR: Set AVAAPI environment variable with your Agentverse API token")
    sys.exit(1)


# ─────────────────────────────────────────────────────────────
# AgentverseClient — Portable API Wrapper
# ─────────────────────────────────────────────────────────────

class AgentverseClient:
    """Full-featured client for the Agentverse v2 REST API."""

    def __init__(self, api_key: str, base_url: str = BASE_URL):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    # ── helpers ──────────────────────────────────────────────

    def _req(self, method: str, path: str, data=None):
        url = f"{self.base_url}{path}"
        r = getattr(requests, method.lower())(url, headers=self.headers, json=data, timeout=15)
        return r

    def _ok(self, r, label=""):
        status = "OK" if r.status_code < 300 else "FAIL"
        try:
            body = r.json()
        except Exception:
            body = r.text[:200]
        print(f"  [{status}] {r.status_code} {label}")
        return body

    # ── Identity ─────────────────────────────────────────────

    def get_challenge(self, address: str) -> str:
        """Get an identity challenge JWT for an agent address."""
        r = self._req("GET", f"/identity/{address}/challenge")
        data = self._ok(r, "Get Challenge")
        return data.get("challenge", "")

    def prove_identity(self, address: str, challenge: str, signature: str) -> dict:
        """Prove ownership of an agent address via challenge-response."""
        r = self._req("POST", "/identity", {
            "address": address,
            "challenge": challenge,
            "challenge_response": signature,
        })
        return self._ok(r, "Prove Identity")

    # ── Agents ───────────────────────────────────────────────

    def list_agents(self) -> list:
        """List all agents owned by the authenticated user."""
        r = self._req("GET", "/agents")
        return self._ok(r, "List Agents")

    def register_agent(self, address: str, name: str, agent_type: str = "uagent", **kwargs) -> dict:
        """Register a new agent. Requires identity to be proved first."""
        payload = {"address": address, "name": name, "agent_type": agent_type}
        payload.update(kwargs)
        r = self._req("POST", "/agents", payload)
        return self._ok(r, f"Register Agent '{name}'")

    def get_agent(self, address: str) -> dict:
        """Get details of a specific agent."""
        r = self._req("GET", f"/agents/{address}")
        return self._ok(r, "Get Agent")

    def update_agent(self, address: str, **fields) -> dict:
        """Update an agent's details. Address must be included."""
        fields["address"] = address
        r = self._req("PUT", f"/agents/{address}", fields)
        return self._ok(r, "Update Agent")

    def delete_agent(self, address: str) -> dict:
        """Delete an agent."""
        r = self._req("DELETE", f"/agents/{address}")
        return self._ok(r, "Delete Agent")

    def batch_register(self, agents: list) -> dict:
        """Batch register multiple agents."""
        r = self._req("POST", "/agents/batch", {"agents": agents})
        return self._ok(r, f"Batch Register ({len(agents)} agents)")

    # ── Mailbox ──────────────────────────────────────────────

    def list_mailbox(self, address: str, limit: int = 100, offset: int = 0) -> list:
        """List messages in an agent's mailbox."""
        r = self._req("GET", f"/agents/{address}/mailbox?limit={limit}&offset={offset}")
        return self._ok(r, "List Mailbox")

    def get_mailbox_message(self, address: str, uuid: str) -> dict:
        """Get a specific mailbox message."""
        r = self._req("GET", f"/agents/{address}/mailbox/{uuid}")
        return self._ok(r, "Get Mailbox Message")

    def delete_mailbox_message(self, address: str, uuid: str) -> dict:
        """Delete a specific mailbox message."""
        r = self._req("DELETE", f"/agents/{address}/mailbox/{uuid}")
        return self._ok(r, "Delete Mailbox Message")

    # ── Almanac ──────────────────────────────────────────────

    def resolve_identifier(self, identifier: str) -> dict:
        """Resolve an agent identifier in the Almanac."""
        r = self._req("GET", f"/almanac/resolve/{identifier}")
        return self._ok(r, f"Resolve '{identifier[:30]}...'")

    def check_handle_available(self, handle: str) -> dict:
        """Check if an Almanac handle is available."""
        r = self._req("GET", f"/almanac/handles/available/{handle}")
        return self._ok(r, f"Check Handle '{handle}'")

    def get_protocol_model(self, digest: str) -> dict:
        """Get a protocol model by digest."""
        r = self._req("GET", f"/almanac/protocols/{digest}")
        return self._ok(r, "Get Protocol Model")

    # ── Users ────────────────────────────────────────────────

    def search_users(self, username: str) -> list:
        """Search for users by username."""
        r = self._req("GET", f"/users/username/search/{username}")
        return self._ok(r, f"Search Users '{username}'")

    def check_username_available(self, username: str) -> dict:
        """Check if a username is available."""
        r = self._req("GET", f"/users/username/available/{username}")
        return self._ok(r, f"Check Username '{username}'")


# ─────────────────────────────────────────────────────────────
# Helper: Full Agent Lifecycle
# ─────────────────────────────────────────────────────────────

def create_agent_with_identity(client: AgentverseClient, name: str, agent_type: str = "uagent"):
    """
    Complete agent creation flow:
    1. Generate cryptographic identity
    2. Get challenge from Agentverse
    3. Sign challenge to prove ownership
    4. Register agent
    """
    from uagents.crypto import Identity

    ident = Identity.generate()
    addr = ident.address
    print(f"\n  Generated address: {addr}")

    # Challenge-response
    challenge = client.get_challenge(addr)
    signature = ident.sign(challenge.encode())
    client.prove_identity(addr, challenge, signature)

    # Register
    client.register_agent(addr, name, agent_type)

    return addr, ident


# ─────────────────────────────────────────────────────────────
# Demo Scenarios
# ─────────────────────────────────────────────────────────────

def demo_agent_lifecycle(client):
    """Demo 1: Full agent CRUD lifecycle."""
    print("\n" + "=" * 60)
    print("DEMO 1: Agent Lifecycle (Create → Read → Update → Delete)")
    print("=" * 60)

    # Create
    addr, ident = create_agent_with_identity(client, "lifecycle-demo")

    # Read
    print("\n--- Read Agent ---")
    agent = client.get_agent(addr)
    print(f"  Agent: {json.dumps(agent, indent=2)}")

    # Update
    print("\n--- Update Agent ---")
    client.update_agent(addr, name="lifecycle-demo-updated")
    updated = client.get_agent(addr)
    print(f"  Updated name: {updated.get('name')}")

    # Delete
    print("\n--- Delete Agent ---")
    client.delete_agent(addr)
    remaining = client.list_agents()
    print(f"  Agents remaining: {len(remaining) if isinstance(remaining, list) else 'N/A'}")


def demo_multiple_agents(client):
    """Demo 2: Managing multiple agents."""
    print("\n" + "=" * 60)
    print("DEMO 2: Multiple Agent Management")
    print("=" * 60)

    agents = []
    for i, atype in enumerate(["uagent", "a2a", "uagent"]):
        name = f"multi-agent-{i+1}-{atype}"
        print(f"\n--- Creating {name} ---")
        addr, _ = create_agent_with_identity(client, name, atype)
        agents.append(addr)

    # List all
    print("\n--- List All Agents ---")
    all_agents = client.list_agents()
    if isinstance(all_agents, list):
        for a in all_agents:
            print(f"  - {a.get('name', 'N/A')} | type: {a.get('agent_type', 'N/A')} | {a['address'][:40]}...")

    # Cleanup
    print("\n--- Cleanup ---")
    for addr in agents:
        client.delete_agent(addr)
    print(f"  Deleted {len(agents)} agents")


def demo_mailbox(client):
    """Demo 3: Agent mailbox operations."""
    print("\n" + "=" * 60)
    print("DEMO 3: Agent Mailbox")
    print("=" * 60)

    addr, _ = create_agent_with_identity(client, "mailbox-demo")

    print("\n--- Check Mailbox ---")
    messages = client.list_mailbox(addr)
    count = len(messages) if isinstance(messages, list) else 0
    print(f"  Messages in mailbox: {count}")

    # Cleanup
    client.delete_agent(addr)


def demo_identity(client):
    """Demo 4: Identity challenge-response flow."""
    print("\n" + "=" * 60)
    print("DEMO 4: Identity Challenge-Response")
    print("=" * 60)

    from uagents.crypto import Identity

    ident = Identity.generate()
    addr = ident.address
    print(f"\n  Address: {addr}")

    # Get challenge
    print("\n--- Step 1: Get Challenge ---")
    challenge = client.get_challenge(addr)
    print(f"  Challenge JWT: {challenge[:60]}...")

    # Sign
    print("\n--- Step 2: Sign Challenge ---")
    sig = ident.sign(challenge.encode())
    print(f"  Signature: {sig[:60]}...")

    # Prove
    print("\n--- Step 3: Prove Identity ---")
    result = client.prove_identity(addr, challenge, sig)
    print(f"  Result: {result}")


def demo_almanac(client):
    """Demo 5: Almanac resolution."""
    print("\n" + "=" * 60)
    print("DEMO 5: Almanac Operations")
    print("=" * 60)

    # Create an agent first
    addr, _ = create_agent_with_identity(client, "almanac-demo")

    # Try to resolve
    print("\n--- Resolve Agent ---")
    client.resolve_identifier(addr)

    # Cleanup
    client.delete_agent(addr)


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  AGENTVERSE API v2 — Comprehensive Demo")
    print(f"  Base URL: {BASE_URL}")
    print(f"  Token:    ...{API_KEY[-12:]}")
    print("=" * 60)

    client = AgentverseClient(API_KEY)

    # Run all demos
    demo_agent_lifecycle(client)
    demo_multiple_agents(client)
    demo_mailbox(client)
    demo_identity(client)
    demo_almanac(client)

    # Final cleanup
    print("\n" + "=" * 60)
    print("FINAL: Verify Clean State")
    print("=" * 60)
    remaining = client.list_agents()
    count = len(remaining) if isinstance(remaining, list) else "?"
    print(f"  Remaining agents: {count}")
    print("\n  All demos complete!")


if __name__ == "__main__":
    main()
