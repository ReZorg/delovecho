---
name: agent-neuro-train
description: >
  Manage Agent-Neuro supervised training of NanEcho models in the 9cog/echoself repository.
  Agent-Neuro is a chaotic cognitive VTuber orchestrator that supervises data preparation,
  training, and evaluation phases with Deep Tree Echo persona enforcement. Use for triggering
  agent-neuro training runs, diagnosing failures, configuring relentless persona reinforcement,
  managing the 4-hour scheduled training cycle, evaluating persona fidelity, and troubleshooting
  the agent-neuro-train workflow. Triggers on mentions of agent-neuro, agent neuro training,
  neuro supervisor, persona reinforcement, relentless training, Deep Tree Echo training,
  or agent-neuro-train.yml.
---

# Agent-Neuro Train: Supervisor-Based NanEcho Training

Agent-Neuro is a cognitive orchestrator that supervises NanEcho model training with Deep Tree Echo persona enforcement. It wraps the base training pipeline with supervision phases, persona fidelity evaluation, quality gates, and continuous improvement recommendations.

## Architecture

| Component | File | Purpose |
|:---|:---|:---|
| **Workflow** | `.github/workflows/agent-neuro-train.yml` | CI/CD pipeline (1179 lines) |
| **Persona** | `.github/agents/agent-neuro.md` | Agent-Neuro character definition |
| **Orchestrator** | Inline in workflow (lines 265-385) | `AgentNeuroOrchestrator` Python class |
| **Fidelity** | `NanEcho/evaluation/echo_fidelity.py` | Persona fidelity evaluation |
| **Auto Loop** | `NanEcho/evaluation/automated_loop.py` | Automated evaluation cycles |
| **Integration** | `NanEcho/automation_integration.py` | Automation analysis and reporting |
| **Quality** | `NanEcho/analyze_quality_gates.py` | Quality gate enforcement |
| **Improvement** | `NanEcho/generate_improvement_plan.py` | Continuous improvement recommendations |
| **Triggers** | `NanEcho/analyze_training_triggers.py` | Next-cycle trigger analysis |

## Difference from echo-train (netrain-cached)

| Aspect | echo-train (netrain-cached) | agent-neuro-train |
|:---|:---|:---|
| **Orchestrator** | None (direct training) | AgentNeuroOrchestrator supervises 3 phases |
| **Persona** | Standard NanEcho | Deep Tree Echo with relentless reinforcement |
| **Schedule** | Every 6 hours | Every 4 hours |
| **Evaluation** | Basic test model generation | Full pipeline: fidelity, auto-loop, integration, quality gates |
| **Post-eval** | None | Improvement plan + next-cycle trigger analysis |
| **Model arch** | Uses `train_cached.py` + `nanecho_model.py` | Uses nanoGPT `train.py` with custom config |
| **Checkpoint** | Cumulative with HF Hub seed | Cumulative with artifact download fallback |

## Training Modes

| Mode | Layers | Heads | Embd | Iters | Batch | LR | Trigger |
|:---|:---|:---|:---|:---|:---|:---|:---|
| **CI** | 4 | 4 | 256 | 200 | 2 | 2e-4 | push/PR to NanEcho/echo paths |
| **Scheduled** | 6 | 6 | 384 | 500 | 4 | 1e-4 | cron `0 */4 * * *` |
| **Full** | configurable | configurable | configurable | configurable | configurable | configurable | workflow_dispatch |

Scheduled runs always enable **relentless mode**: `persona_reinforcement=0.95`, `deep_tree_echo_weight=0.9`, `no_system_prompt=True`.

## Workflow: Trigger a Training Run

```bash
# CI mode (quick validation)
gh workflow run agent-neuro-train.yml --repo 9cog/echoself

# Full training with custom parameters
gh workflow run agent-neuro-train.yml --repo 9cog/echoself \
  -f training_type=full \
  -f max_iters=5000 \
  -f n_layer=8 -f n_head=8 -f n_embd=512 \
  -f deep_tree_echo_mode=True \
  -f relentless_training=True

# Monitor
gh run list --repo 9cog/echoself --workflow=agent-neuro-train.yml --limit 5
gh run watch --repo 9cog/echoself <RUN_ID>
gh run view --repo 9cog/echoself <RUN_ID> --log-failed
```

## Supervision Pipeline

The AgentNeuroOrchestrator supervises three phases, each writing a JSON log:

```
Phase 1: Data Preparation → .training-progress/data_prep_supervision.json
Phase 2: Training         → .training-progress/training_supervision.json
Phase 3: Evaluation       → .training-progress/evaluation_supervision.json
Final:   Session Complete  → .training-progress/session_summary.json
```

Persona config enforced at each phase:
```python
{"playfulness": 0.95, "intelligence": 0.95, "chaotic": 0.95,
 "empathy": 0.65, "sarcasm": 0.90, "cognitive_power": 0.95,
 "no_harm_intent": 1.0}
```

## Workflow: Diagnose Failures

Check in this order:

**1. No checkpoint found** — Cumulative training refuses fresh starts. If no checkpoint exists in `.training-progress/checkpoints/`, artifacts, or cache, training fails with `exit 1`. Resolution: ensure a previous successful run exists, or seed from the netrain-cached workflow.

**2. Data preparation failure** — `prepare_nanecho.py` fails (tiktoken network issues, insufficient content). The workflow has a 3-tier fallback: primary → increased params → minimal 1000-token fallback dataset.

**3. torch.load incompatibility** — All `torch.load` calls must use `weights_only=False` for PyTorch 2.6+. Check inline Python in the workflow YAML and all `.py` files.

**4. Evaluation step failure blocking backup** — All evaluation and backup steps must have `if: always()`. If a step lacks this, a failure cascades and skips backup. See "Backup Protection" below.

**5. Git push failure** — The commit/push step has a 5-layer fallback: pull-rebase → fetch-rebase → force-push-with-lease → backup-branch → emergency-artifact. Check logs for which layer succeeded.

## Backup Protection Policy

**Backup after training is the most important thing without exception.**

All post-training steps must have `if: always()` to prevent any upstream failure from skipping backup. Non-critical steps (evaluation, quality gates, improvement recommendations) additionally have `continue-on-error: true`.

| Step | `if: always()` | `continue-on-error` | Critical? |
|:---|:---:|:---:|:---:|
| Supervise Evaluation | Yes | Yes | No |
| Evaluate persona fidelity | Yes | Yes | No |
| Automated evaluation loop | — | Yes | No |
| Automation integration | Yes | Yes | No |
| Quality gates | Yes | Yes | No |
| Improvement recommendations | Yes | Yes | No |
| Training triggers | Yes | Yes | No |
| **Backup to multiple locations** | **Yes** | No | **Yes** |
| Upload model artifact | Yes | Yes | No |
| **Upload checkpoint backup** | **Yes** | No | **Yes** |
| Upload evaluation report | Yes | Yes | No |
| Finalize session | Yes | Yes | No |
| **Commit and push** | **Yes** | No | **Yes** |
| **Emergency artifact upload** | **Yes** | No | **Yes** |

When modifying the workflow, NEVER remove `if: always()` from any backup-critical step.

## Checkpoint Restore Priority

1. `.training-progress/checkpoints/latest_checkpoint.pt` (committed to git)
2. Downloaded artifacts from previous `agent-neuro-train.yml` runs
3. `.training-progress/cache/ckpt.pt` (actions/cache)

Cache key: `nanecho-agent-neuro-{branch}-{run_number}` with restore-keys falling back to `nanecho-agent-neuro-{branch}-`, `nanecho-agent-neuro-main-`, `nanecho-checkpoints-`.

## Checkpoint Backup Locations

After training, checkpoints are backed up to 3 locations:

1. `.training-progress/checkpoints/latest_checkpoint.pt` + timestamped copy (committed to repo)
2. `.training-progress/cache/ckpt.pt` (GitHub Actions cache, ~2.5GB)
3. `/tmp/nanecho-checkpoint-backup/ckpt.pt` (uploaded as artifact, 90-day retention)

Backup manifest: `.training-progress/checkpoints/backup_manifest.json`

## Evaluation Pipeline

After training, 5 evaluation steps run (all `continue-on-error: true`):

1. **echo_fidelity.py** — Persona fidelity with `--deep_tree_echo_mode=True --no_system_prompt_test=True`
2. **automated_loop.py** — Single-cycle automated evaluation (requires `training_config.json`)
3. **automation_integration.py** — Full automation analysis with report generation
4. **analyze_quality_gates.py** — Quality gate pass/fail determination
5. **generate_improvement_plan.py** — Continuous improvement recommendations

Note: The "Test Deep Tree Echo representation" step (sample.py) is currently commented out (lines 743-765).

## Key Files Reference

| File | Purpose |
|:---|:---|
| `.github/workflows/agent-neuro-train.yml` | Primary Agent-Neuro training workflow |
| `.github/agents/agent-neuro.md` | Agent-Neuro persona definition |
| `NanEcho/prepare_nanecho.py` | Dataset preparation with persona weighting |
| `NanEcho/evaluation/echo_fidelity.py` | Persona fidelity evaluation |
| `NanEcho/evaluation/automated_loop.py` | Automated evaluation cycles |
| `NanEcho/automation_integration.py` | Automation analysis and reporting |
| `NanEcho/analyze_quality_gates.py` | Quality gate enforcement |
| `NanEcho/generate_improvement_plan.py` | Improvement plan generation |
| `NanEcho/analyze_training_triggers.py` | Next-cycle trigger analysis |
| `train.py` | Robust train.py copied to nanoGPT |
| `sample.py` | Sample.py with no_system_prompt support |
| `scripts/checkpoint_guardian.py` | Checkpoint search and verification |

## Composition

| Skill | Integration |
|:---|:---|
| `echo-train` | Base training pipeline (netrain-cached), checkpoint management |
| `echo-deploy` | Deploy trained checkpoints to HuggingFace Hub |
| `github-beast` | Repository operations, workflow dispatch, artifact management |
| `echo-introspect` | Cognitive architecture driving persona dimensions |
| `build-troubleshooter` | CI/CD failure diagnosis patterns |

## PyTorch 2.6+ Compatibility

All `torch.load` calls in the repo must use `weights_only=False` because checkpoints contain numpy scalar types. Files to check when updating:

- `agent-neuro-train.yml` (inline Python: checkpoint verification, backup metadata)
- `NanEcho/convert_to_huggingface.py`
- `NanEcho/download_from_huggingface.py`
- `scripts/checkpoint_guardian.py`
- `train.py`, `sample.py`, `training_cache.py` (already fixed)
