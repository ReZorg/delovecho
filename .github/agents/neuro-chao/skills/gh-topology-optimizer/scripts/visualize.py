#!/usr/bin/env python3
"""
Topology Optimizer Visualization
Generates comprehensive charts for the 3-phase analysis.
"""
import json
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import numpy as np
from collections import defaultdict

# ── Load data ──
with open("/home/ubuntu/gh-topology-optimizer/topology_analysis.json") as f:
    data = json.load(f)

# ── Style ──
plt.style.use('dark_background')
COLORS = {
    "bg": "#0d1117",
    "panel": "#161b22",
    "border": "#30363d",
    "text": "#c9d1d9",
    "accent1": "#58a6ff",  # blue
    "accent2": "#3fb950",  # green
    "accent3": "#d29922",  # amber
    "accent4": "#f85149",  # red
    "accent5": "#bc8cff",  # purple
    "accent6": "#79c0ff",  # light blue
    "accent7": "#ff7b72",  # salmon
}
ENT_COLORS = [
    "#58a6ff", "#3fb950", "#d29922", "#f85149", "#bc8cff",
    "#79c0ff", "#ff7b72", "#56d364", "#e3b341", "#db61a2",
]

# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 1: Enterprise Topology Overview (4-panel)
# ═══════════════════════════════════════════════════════════════════════════

fig = plt.figure(figsize=(20, 16), facecolor=COLORS["bg"])
fig.suptitle(
    "GitHub Namespace Topology Analysis: 0(1(2(3(4(5)))))",
    fontsize=18, color=COLORS["text"], fontweight="bold", y=0.98
)
fig.text(0.5, 0.955,
    "Skill chain: /metamathematical-consciousness ( /gh253 | /org-fabric ( /apl253 ) ) → /vorticog ( /digitwin )",
    fontsize=10, color=COLORS["border"], ha="center"
)

gs = GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.25, top=0.93, bottom=0.05, left=0.06, right=0.97)

# ── Panel 1: Enterprise Sunburst (Treemap proxy) ──
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_facecolor(COLORS["panel"])
ax1.set_title("Enterprise → Org → Repo Hierarchy", color=COLORS["text"], fontsize=13, pad=10)

agents = data["phase3_simulation"]["agents"]
ent_data = defaultdict(lambda: defaultdict(int))
for a in agents:
    ent_data[a["enterprise"]][a["name"]] = a["repo_count"]

# Build a horizontal stacked bar chart showing enterprise composition
ent_names = sorted(ent_data.keys(), key=lambda e: -sum(ent_data[e].values()))
ent_totals = [sum(ent_data[e].values()) for e in ent_names]

bars = ax1.barh(range(len(ent_names)), ent_totals, color=[ENT_COLORS[i % len(ENT_COLORS)] for i in range(len(ent_names))],
                edgecolor=COLORS["border"], linewidth=0.5, alpha=0.85)
ax1.set_yticks(range(len(ent_names)))
ax1.set_yticklabels(ent_names, color=COLORS["text"], fontsize=10)
ax1.set_xlabel("Total Repositories", color=COLORS["text"], fontsize=10)
ax1.tick_params(colors=COLORS["text"])
ax1.invert_yaxis()

# Annotate with org count
for i, (ent, total) in enumerate(zip(ent_names, ent_totals)):
    org_count = len(ent_data[ent])
    ax1.text(total + 20, i, f"{total} repos / {org_count} orgs", va="center",
             color=COLORS["text"], fontsize=9)

ax1.set_xlim(0, max(ent_totals) * 1.35)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.spines['bottom'].set_color(COLORS["border"])
ax1.spines['left'].set_color(COLORS["border"])

# ── Panel 2: Level Metrics (Gini + Entropy) ──
ax2 = fig.add_subplot(gs[0, 1])
ax2.set_facecolor(COLORS["panel"])
ax2.set_title("Gödel Encoding ⌜S⌝: Level Metrics", color=COLORS["text"], fontsize=13, pad=10)

level_metrics = data["phase1_metamath"]["level_metrics"]
levels = sorted(level_metrics.keys())
labels = [f"L{l} ({level_metrics[l]['label']})" for l in levels]
gini_vals = [level_metrics[l]["gini"] for l in levels]
entropy_vals = [level_metrics[l]["entropy"] for l in levels]
mean_vals = [level_metrics[l]["mean_children"] for l in levels]

x = np.arange(len(levels))
width = 0.35

bars1 = ax2.bar(x - width/2, gini_vals, width, label="Gini (inequality)", color=COLORS["accent4"], alpha=0.8)
bars2 = ax2.bar(x + width/2, entropy_vals, width, label="Entropy (diversity)", color=COLORS["accent2"], alpha=0.8)

ax2.set_xticks(x)
ax2.set_xticklabels(labels, color=COLORS["text"], fontsize=10)
ax2.set_ylabel("Score (0-1)", color=COLORS["text"])
ax2.tick_params(colors=COLORS["text"])
ax2.legend(facecolor=COLORS["panel"], edgecolor=COLORS["border"], labelcolor=COLORS["text"])
ax2.set_ylim(0, 1.1)

# Add mean children as text annotations
for i, (g, e, m) in enumerate(zip(gini_vals, entropy_vals, mean_vals)):
    ax2.text(i, max(g, e) + 0.05, f"μ={m:.0f}", ha="center", color=COLORS["accent6"], fontsize=9)

# Threshold lines
ax2.axhline(y=0.6, color=COLORS["accent3"], linestyle="--", alpha=0.5, linewidth=0.8)
ax2.text(len(levels) - 0.5, 0.62, "Gini threshold", color=COLORS["accent3"], fontsize=8, ha="right")

ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['bottom'].set_color(COLORS["border"])
ax2.spines['left'].set_color(COLORS["border"])

# ── Panel 3: Pattern Language Diagnosis (Radar) ──
ax3 = fig.add_subplot(gs[1, 0], polar=True)
ax3.set_facecolor(COLORS["panel"])
ax3.set_title("gh253 Pattern Language Diagnosis", color=COLORS["text"], fontsize=13, pad=20)

patterns = data["phase2_patterns"]
pattern_labels = [f"#{p['pattern_id']}\n{p['pattern_name'][:18]}" for p in patterns]
pattern_scores = [p["score"] for p in patterns]

angles = np.linspace(0, 2 * np.pi, len(patterns), endpoint=False).tolist()
pattern_scores_closed = pattern_scores + [pattern_scores[0]]
angles_closed = angles + [angles[0]]

ax3.plot(angles_closed, pattern_scores_closed, 'o-', color=COLORS["accent1"], linewidth=2, markersize=8)
ax3.fill(angles_closed, pattern_scores_closed, alpha=0.15, color=COLORS["accent1"])

ax3.set_xticks(angles)
ax3.set_xticklabels(pattern_labels, color=COLORS["text"], fontsize=8)
ax3.set_ylim(0, 1.0)
ax3.set_yticks([0.25, 0.5, 0.75, 1.0])
ax3.set_yticklabels(["0.25", "0.50", "0.75", "1.00"], color=COLORS["border"], fontsize=8)
ax3.tick_params(colors=COLORS["text"])

# Color the threshold zone
theta = np.linspace(0, 2 * np.pi, 100)
ax3.fill_between(theta, 0, 0.4, alpha=0.08, color=COLORS["accent4"])
ax3.fill_between(theta, 0.4, 0.7, alpha=0.05, color=COLORS["accent3"])

ax3.spines['polar'].set_color(COLORS["border"])

# ── Panel 4: Cognitive Mode Distribution (Donut) ──
ax4 = fig.add_subplot(gs[1, 1])
ax4.set_facecolor(COLORS["panel"])
ax4.set_title("Vorticog Agent Cognitive Modes", color=COLORS["text"], fontsize=13, pad=10)

mode_dist = data["phase3_simulation"]["mode_distribution"]
mode_labels = sorted(mode_dist.keys(), key=lambda k: -mode_dist[k])
mode_values = [mode_dist[k] for k in mode_labels]

mode_colors = {
    "EXPLORATORY": "#3fb950",
    "FOCUSED": "#58a6ff",
    "SOCIAL": "#bc8cff",
    "REFLECTIVE": "#79c0ff",
    "NEUTRAL": "#8b949e",
    "STRESSED": "#d29922",
    "THREAT": "#f85149",
    "REWARD": "#56d364",
}
colors = [mode_colors.get(m, "#8b949e") for m in mode_labels]

wedges, texts, autotexts = ax4.pie(
    mode_values, labels=mode_labels, colors=colors,
    autopct=lambda pct: f"{int(round(pct * sum(mode_values) / 100))}",
    pctdistance=0.78, startangle=90,
    wedgeprops=dict(width=0.45, edgecolor=COLORS["bg"], linewidth=2)
)
for t in texts:
    t.set_color(COLORS["text"])
    t.set_fontsize(9)
for t in autotexts:
    t.set_color(COLORS["bg"])
    t.set_fontsize(10)
    t.set_fontweight("bold")

# Center text
ax4.text(0, 0, f"91\norgs", ha="center", va="center", fontsize=16,
         color=COLORS["text"], fontweight="bold")

plt.savefig("/home/ubuntu/gh-topology-optimizer/topology_overview.png", dpi=150, facecolor=COLORS["bg"])
plt.close()
print("Saved: topology_overview.png")


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 2: Detailed Agent Heatmap
# ═══════════════════════════════════════════════════════════════════════════

fig2, axes = plt.subplots(1, 3, figsize=(22, 10), facecolor=COLORS["bg"])
fig2.suptitle(
    "Vorticog Digital Twin: Org Agent State Space",
    fontsize=16, color=COLORS["text"], fontweight="bold", y=0.98
)

# Sort agents by enterprise then stress
agents_sorted = sorted(agents, key=lambda a: (a["enterprise"], -a["emotions"]["stress"]))

# Only show top 30 most interesting (highest stress + most repos)
agents_top = sorted(agents, key=lambda a: -(a["emotions"]["stress"] * 0.6 + min(a["repo_count"], 200) * 0.4))[:30]
agent_labels = [f"{a['name'][:25]} ({a['enterprise']})" for a in agents_top]

# Panel A: Needs heatmap
ax_a = axes[0]
ax_a.set_facecolor(COLORS["panel"])
ax_a.set_title("Agent Needs", color=COLORS["text"], fontsize=12, pad=8)

needs_data = np.array([[a["needs"]["capacity"], a["needs"]["coherence"],
                         a["needs"]["visibility"], a["needs"]["autonomy"]] for a in agents_top])

im_a = ax_a.imshow(needs_data, cmap="RdYlGn", aspect="auto", vmin=0, vmax=100)
ax_a.set_yticks(range(len(agent_labels)))
ax_a.set_yticklabels(agent_labels, fontsize=7, color=COLORS["text"])
ax_a.set_xticks(range(4))
ax_a.set_xticklabels(["Capacity", "Coherence", "Visibility", "Autonomy"],
                      fontsize=9, color=COLORS["text"], rotation=45, ha="right")
fig2.colorbar(im_a, ax=ax_a, shrink=0.6, label="Need Level (0-100)")

# Panel B: Hormones heatmap
ax_b = axes[1]
ax_b.set_facecolor(COLORS["panel"])
ax_b.set_title("Hormone Concentrations", color=COLORS["text"], fontsize=12, pad=8)

hormone_data = np.array([[a["hormones"]["cortisol"], a["hormones"]["dopamine"],
                           a["hormones"]["oxytocin"], a["hormones"]["norepinephrine"]] for a in agents_top])

im_b = ax_b.imshow(hormone_data, cmap="magma", aspect="auto", vmin=0, vmax=1)
ax_b.set_yticks(range(len(agent_labels)))
ax_b.set_yticklabels(agent_labels, fontsize=7, color=COLORS["text"])
ax_b.set_xticks(range(4))
ax_b.set_xticklabels(["Cortisol", "Dopamine", "Oxytocin", "Norepinephrine"],
                      fontsize=9, color=COLORS["text"], rotation=45, ha="right")
fig2.colorbar(im_b, ax=ax_b, shrink=0.6, label="Concentration (0-1)")

# Panel C: Emotions bar chart
ax_c = axes[2]
ax_c.set_facecolor(COLORS["panel"])
ax_c.set_title("Emotional State", color=COLORS["text"], fontsize=12, pad=8)

y_pos = np.arange(len(agents_top))
stress_vals = [a["emotions"]["stress"] for a in agents_top]
satisfaction_vals = [a["emotions"]["satisfaction"] for a in agents_top]
trust_vals = [a["emotions"]["trust"] for a in agents_top]

ax_c.barh(y_pos - 0.25, stress_vals, 0.25, color=COLORS["accent4"], alpha=0.8, label="Stress")
ax_c.barh(y_pos, satisfaction_vals, 0.25, color=COLORS["accent2"], alpha=0.8, label="Satisfaction")
ax_c.barh(y_pos + 0.25, trust_vals, 0.25, color=COLORS["accent1"], alpha=0.8, label="Trust")

ax_c.set_yticks(y_pos)
ax_c.set_yticklabels(agent_labels, fontsize=7, color=COLORS["text"])
ax_c.set_xlabel("Level (0-100)", color=COLORS["text"])
ax_c.tick_params(colors=COLORS["text"])
ax_c.legend(facecolor=COLORS["panel"], edgecolor=COLORS["border"], labelcolor=COLORS["text"], fontsize=8)
ax_c.invert_yaxis()

for ax in axes:
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(COLORS["border"])
    ax.spines['left'].set_color(COLORS["border"])

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig("/home/ubuntu/gh-topology-optimizer/agent_heatmap.png", dpi=150, facecolor=COLORS["bg"])
plt.close()
print("Saved: agent_heatmap.png")


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 3: Recommendation Summary
# ═══════════════════════════════════════════════════════════════════════════

fig3, (ax_r1, ax_r2) = plt.subplots(1, 2, figsize=(18, 8), facecolor=COLORS["bg"])
fig3.suptitle(
    "Topology Optimization Recommendations",
    fontsize=16, color=COLORS["text"], fontweight="bold", y=0.98
)

# Panel A: Recommendation types
ax_r1.set_facecolor(COLORS["panel"])
ax_r1.set_title("Recommendation Distribution", color=COLORS["text"], fontsize=12, pad=8)

rec_summary = data["phase3_simulation"]["recommendation_summary"]
rec_types = sorted(rec_summary.keys(), key=lambda k: -rec_summary[k])
rec_counts = [rec_summary[k] for k in rec_types]
rec_colors = {
    "MERGE": COLORS["accent4"],
    "CONSOLIDATE": COLORS["accent3"],
    "SPLIT": COLORS["accent5"],
    "REORGANIZE": COLORS["accent1"],
    "REVIEW": COLORS["accent6"],
    "ATTENTION": COLORS["accent7"],
    "CRITICAL": "#f85149",
}
bar_colors = [rec_colors.get(r, COLORS["accent1"]) for r in rec_types]

ax_r1.barh(range(len(rec_types)), rec_counts, color=bar_colors, edgecolor=COLORS["border"], alpha=0.85)
ax_r1.set_yticks(range(len(rec_types)))
ax_r1.set_yticklabels(rec_types, color=COLORS["text"], fontsize=11)
ax_r1.set_xlabel("Count", color=COLORS["text"])
ax_r1.tick_params(colors=COLORS["text"])
ax_r1.invert_yaxis()

for i, v in enumerate(rec_counts):
    ax_r1.text(v + 0.3, i, str(v), va="center", color=COLORS["text"], fontsize=11, fontweight="bold")

ax_r1.spines['top'].set_visible(False)
ax_r1.spines['right'].set_visible(False)
ax_r1.spines['bottom'].set_color(COLORS["border"])
ax_r1.spines['left'].set_color(COLORS["border"])

# Panel B: Violations by severity
ax_r2.set_facecolor(COLORS["panel"])
ax_r2.set_title("Ω^S Subobject Classifier: Violations", color=COLORS["text"], fontsize=12, pad=8)

violations = data["phase1_metamath"]["violations"]
sev_counts = defaultdict(int)
type_counts = defaultdict(int)
for v in violations:
    sev_counts[v["severity"]] += 1
    type_counts[v["type"]] += 1

sev_order = ["high", "medium", "low", "info"]
sev_colors = {"high": COLORS["accent4"], "medium": COLORS["accent3"], "low": COLORS["accent6"], "info": "#8b949e"}
sev_vals = [sev_counts.get(s, 0) for s in sev_order]

bars = ax_r2.bar(range(len(sev_order)), sev_vals,
                 color=[sev_colors[s] for s in sev_order],
                 edgecolor=COLORS["border"], alpha=0.85)
ax_r2.set_xticks(range(len(sev_order)))
ax_r2.set_xticklabels([s.upper() for s in sev_order], color=COLORS["text"], fontsize=11)
ax_r2.set_ylabel("Count", color=COLORS["text"])
ax_r2.tick_params(colors=COLORS["text"])

for i, v in enumerate(sev_vals):
    ax_r2.text(i, v + 0.3, str(v), ha="center", color=COLORS["text"], fontsize=12, fontweight="bold")

# Add type breakdown as text
type_text = "\n".join(f"  {t}: {c}" for t, c in sorted(type_counts.items(), key=lambda x: -x[1]))
ax_r2.text(0.98, 0.95, f"By Type:\n{type_text}", transform=ax_r2.transAxes,
           va="top", ha="right", fontsize=9, color=COLORS["text"],
           bbox=dict(boxstyle="round,pad=0.5", facecolor=COLORS["panel"], edgecolor=COLORS["border"]))

ax_r2.spines['top'].set_visible(False)
ax_r2.spines['right'].set_visible(False)
ax_r2.spines['bottom'].set_color(COLORS["border"])
ax_r2.spines['left'].set_color(COLORS["border"])

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig("/home/ubuntu/gh-topology-optimizer/recommendations.png", dpi=150, facecolor=COLORS["bg"])
plt.close()
print("Saved: recommendations.png")

print("\nAll visualizations generated.")
