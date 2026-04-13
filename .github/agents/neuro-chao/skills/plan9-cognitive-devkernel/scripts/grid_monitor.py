#!/usr/bin/env python3
"""
Plan 9 CPU Server Grid Monitor — Flask Dashboard

Provides a web dashboard on port 9090 for monitoring the distributed
Plan 9 CPU server grid. Displays node status, 9P2000 connections,
cognitive namespace health, and temporal hierarchy state.

Transformed from inferno-devcontainer/cluster_monitor.py via function-creator.
"""

import json
import os
import time
from datetime import datetime

try:
    from flask import Flask, jsonify, render_template_string
except ImportError:
    print("Flask not installed. Install with: pip install flask")
    raise

app = Flask(__name__)

# Grid configuration
GRID_NODES = int(os.environ.get("PLAN9_GRID_NODES", "3"))
P9_BASE_PORT = int(os.environ.get("PLAN9_9P_PORT", "564"))

# Simulated grid state (in production, query actual 9P2000 endpoints)
grid_state = {
    "nodes": [],
    "start_time": time.time(),
}


def init_grid_state():
    """Initialize simulated grid state."""
    grid_state["nodes"] = []
    for i in range(GRID_NODES):
        role = "auth-server" if i == 0 else "cpu-server"
        grid_state["nodes"].append({
            "id": i,
            "hostname": f"plan9-{'registry' if i == 0 else f'cpu-{i}'}",
            "role": role,
            "port": P9_BASE_PORT + i,
            "status": "running",
            "uptime_s": 0,
            "9p_connections": 0,
            "cognitive_ns": {
                "/cognitive/atomspace": "mounted" if i == 0 else "bound",
                "/cognitive/inference": "mounted" if i == 0 else "bound",
                "/cognitive/attention": "mounted" if i <= 1 else "unmounted",
                "/cognitive/learning": "mounted" if i == 0 else "unmounted",
            },
            "cpu_pct": 0.0,
            "mem_mb": 0,
        })


DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Plan 9 CPU Server Grid Monitor</title>
    <style>
        body { font-family: 'Lucida Console', monospace; background: #1a1a2e; color: #e0e0e0; margin: 20px; }
        h1 { color: #00d4ff; border-bottom: 2px solid #00d4ff; padding-bottom: 10px; }
        h2 { color: #7fdbca; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 15px; }
        .node { background: #16213e; border: 1px solid #0f3460; border-radius: 8px; padding: 15px; }
        .node.registry { border-color: #00d4ff; }
        .node.cpu { border-color: #7fdbca; }
        .status { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 5px; }
        .status.running { background: #00ff88; }
        .status.stopped { background: #ff4444; }
        .ns-path { font-size: 0.85em; color: #aaa; }
        .ns-mounted { color: #00ff88; }
        .ns-bound { color: #ffaa00; }
        .ns-unmounted { color: #666; }
        table { border-collapse: collapse; width: 100%; margin: 10px 0; }
        th, td { padding: 6px 10px; text-align: left; border-bottom: 1px solid #333; }
        th { color: #00d4ff; }
        .refresh { color: #666; font-size: 0.8em; }
    </style>
    <script>
        setTimeout(function(){ location.reload(); }, 5000);
    </script>
</head>
<body>
    <h1>Plan 9 CPU Server Grid Monitor</h1>
    <p class="refresh">Auto-refresh every 5s | Uptime: {{ uptime }}</p>

    <h2>Grid Nodes ({{ node_count }})</h2>
    <div class="grid">
    {% for node in nodes %}
        <div class="node {{ node.role.replace('-', ' ').split()[0] }}">
            <h3>
                <span class="status {{ node.status }}"></span>
                {{ node.hostname }} ({{ node.role }})
            </h3>
            <table>
                <tr><td>9P2000 Port</td><td>{{ node.port }}</td></tr>
                <tr><td>Connections</td><td>{{ node['9p_connections'] }}</td></tr>
                <tr><td>CPU</td><td>{{ "%.1f"|format(node.cpu_pct) }}%</td></tr>
                <tr><td>Memory</td><td>{{ node.mem_mb }} MB</td></tr>
            </table>
            <h4>Cognitive Namespace</h4>
            {% for path, status in node.cognitive_ns.items() %}
            <div class="ns-path ns-{{ status }}">{{ path }} [{{ status }}]</div>
            {% endfor %}
        </div>
    {% endfor %}
    </div>
</body>
</html>
"""


@app.route("/")
def dashboard():
    """Render the grid monitoring dashboard."""
    import random
    uptime = int(time.time() - grid_state["start_time"])
    hours, remainder = divmod(uptime, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Simulate dynamic metrics
    for node in grid_state["nodes"]:
        node["uptime_s"] = uptime
        node["9p_connections"] = random.randint(1, 20)
        node["cpu_pct"] = random.uniform(5, 65)
        node["mem_mb"] = random.randint(64, 512)

    return render_template_string(
        DASHBOARD_HTML,
        nodes=grid_state["nodes"],
        node_count=len(grid_state["nodes"]),
        uptime=f"{hours}h {minutes}m {seconds}s",
    )


@app.route("/api/status")
def api_status():
    """JSON API for grid status."""
    return jsonify({
        "grid_nodes": len(grid_state["nodes"]),
        "uptime_s": int(time.time() - grid_state["start_time"]),
        "nodes": grid_state["nodes"],
    })


@app.route("/api/namespace")
def api_namespace():
    """JSON API for cognitive namespace status."""
    ns = {}
    for node in grid_state["nodes"]:
        ns[node["hostname"]] = node["cognitive_ns"]
    return jsonify(ns)


if __name__ == "__main__":
    init_grid_state()
    port = int(os.environ.get("MONITOR_PORT", "9090"))
    print(f"Plan 9 Grid Monitor starting on port {port}")
    print(f"Monitoring {GRID_NODES} nodes, 9P2000 base port {P9_BASE_PORT}")
    app.run(host="0.0.0.0", port=port, debug=False)
