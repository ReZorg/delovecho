#!/usr/bin/env python3
"""
Plan 9 CPU Server Grid Monitor
A lightweight Flask-based dashboard for monitoring distributed Plan 9 CPU server grids.
Provides real-time status of grid nodes, 9P2000 connections, and services.
"""

import json
import os
import socket
import subprocess
import time
from datetime import datetime
from pathlib import Path

try:
    from flask import Flask, jsonify, render_template_string
except ImportError:
    print("Flask not installed. Install with: pip3 install flask")
    exit(1)

app = Flask(__name__)

GRID_DIR = Path(os.environ.get("GRID_DIR", "/var/plan9/grid"))
BASE_PORT = int(os.environ.get("PLAN9_9P_PORT", "564"))
GRID_NODES = int(os.environ.get("PLAN9_GRID_NODES", "3"))

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Plan 9 CPU Server Grid Monitor</title>
    <meta http-equiv="refresh" content="5">
    <style>
        body { font-family: monospace; background: #ffffea; color: #333; margin: 2em; }
        h1 { color: #268bd2; border-bottom: 2px solid #268bd2; padding-bottom: 0.3em; }
        .node { border: 1px solid #999; padding: 1em; margin: 0.5em 0; border-radius: 4px; background: #fff; }
        .running { border-color: #2aa198; background: #f0fff0; }
        .stopped { border-color: #dc322f; background: #fff0f0; }
        .status-badge { padding: 2px 8px; border-radius: 3px; font-weight: bold; }
        .status-running { background: #2aa198; color: #fff; }
        .status-stopped { background: #dc322f; color: #fff; }
        table { border-collapse: collapse; width: 100%; margin: 1em 0; }
        th, td { border: 1px solid #999; padding: 8px; text-align: left; }
        th { background: #eee8d5; }
        .metric { font-size: 2em; color: #268bd2; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1em; }
        .footer { margin-top: 2em; color: #93a1a1; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>Plan 9 CPU Server Grid Monitor</h1>
    <p>Last updated: {{ timestamp }}</p>
    <div class="grid">
        <div class="node"><div class="metric">{{ total_nodes }}</div>Total Nodes</div>
        <div class="node"><div class="metric" style="color:#2aa198">{{ running_nodes }}</div>Running</div>
        <div class="node"><div class="metric" style="color:#dc322f">{{ stopped_nodes }}</div>Stopped</div>
        <div class="node"><div class="metric">{{ total_nodes }}</div>9P2000 Endpoints</div>
    </div>
    <h2>Node Status</h2>
    <table>
        <tr><th>Node</th><th>Port</th><th>PID</th><th>Status</th><th>9P2000</th><th>Services</th></tr>
        {% for node in nodes %}
        <tr class="{{ 'running' if node.status == 'running' else 'stopped' }}">
            <td>{{ node.name }}</td>
            <td>{{ node.port }}</td>
            <td>{{ node.pid }}</td>
            <td><span class="status-badge status-{{ node.status }}">{{ node.status }}</span></td>
            <td>{{ 'ok' if node.nine_p else '-' }}</td>
            <td>{{ node.services | join(', ') }}</td>
        </tr>
        {% endfor %}
    </table>
    <div class="footer">
        Plan 9 from Bell Labs &mdash; function-creator(inferno-devcontainer)
    </div>
</body>
</html>
"""


def check_port(host: str, port: int, timeout: float = 1.0) -> bool:
    """Check if a TCP port is open."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def get_node_status(node_id: int) -> dict:
    """Get status of a single grid node."""
    node_dir = GRID_DIR / f"cpu-{node_id}"
    port = BASE_PORT + node_id
    pid_file = node_dir / "cpu.pid"

    status = {
        "name": f"cpu-{node_id}",
        "port": port,
        "pid": "-",
        "status": "stopped",
        "nine_p": False,
        "services": [],
    }

    # Check PID file
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            status["pid"] = str(pid)
            os.kill(pid, 0)
            status["status"] = "running"
        except (ValueError, ProcessLookupError, PermissionError):
            status["status"] = "dead"

    # Check 9P2000 port
    status["nine_p"] = check_port("localhost", port)

    # Read services
    services_file = node_dir / "registry" / "services"
    if services_file.exists():
        for line in services_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                svc_name = line.split("—")[0].strip() if "—" in line else line
                status["services"].append(svc_name)

    return status


@app.route("/")
def dashboard():
    """Render the grid dashboard."""
    nodes = [get_node_status(i) for i in range(GRID_NODES)]
    running = sum(1 for n in nodes if n["status"] == "running")
    return render_template_string(
        DASHBOARD_HTML,
        nodes=nodes,
        total_nodes=GRID_NODES,
        running_nodes=running,
        stopped_nodes=GRID_NODES - running,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )


@app.route("/api/status")
def api_status():
    """Return grid status as JSON."""
    nodes = [get_node_status(i) for i in range(GRID_NODES)]
    return jsonify(
        {
            "grid": {
                "total_nodes": GRID_NODES,
                "running": sum(1 for n in nodes if n["status"] == "running"),
                "timestamp": datetime.now().isoformat(),
            },
            "nodes": nodes,
        }
    )


if __name__ == "__main__":
    port = int(os.environ.get("MONITOR_PORT", "9090"))
    print(f"Plan 9 CPU Server Grid Monitor starting on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
