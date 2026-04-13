# Agent-Neuro Train Workflow Inputs

## workflow_dispatch Inputs

| Input | Type | Default | Description |
|:---|:---|:---|:---|
| `training_type` | choice | ci | Training mode: `ci`, `scheduled`, `full` |
| `max_iters` | string | 500 | Maximum training iterations |
| `n_layer` | string | 6 | Number of transformer layers |
| `n_head` | string | 6 | Number of attention heads |
| `n_embd` | string | 384 | Embedding dimension |
| `batch_size` | string | 4 | Training batch size |
| `learning_rate` | string | 1e-4 | Learning rate |
| `deep_tree_echo_mode` | boolean | true | Enable Deep Tree Echo persona |
| `relentless_training` | boolean | false | Enable relentless persona reinforcement |
| `no_system_prompt` | boolean | true | Train without system prompt dependency |

## Computed Parameters (from `set-params` step)

| Output | Source | Description |
|:---|:---|:---|
| `output_dir` | `nanecho-cached-ci` or `nanecho-deep-tree-echo` | Training output directory |
| `relentless_mode` | Derived from inputs + schedule | Whether relentless mode is active |
| `persona_reinforcement` | 0.95 if relentless, 0.5 otherwise | Persona reinforcement weight |
| `deep_tree_echo_weight` | 0.9 if relentless, 0.5 otherwise | Deep Tree Echo weight |

## Trigger Paths

The workflow triggers on push/PR changes to these paths:
- `NanEcho/**`
- `echoself.md`
- `train.py`
- `sample.py`
- `.github/workflows/agent-neuro-train.yml`
- `.github/agents/agent-neuro.md`

## Schedule

- Cron: `0 */4 * * *` (every 4 hours)
- Schedule always enables: `relentless_mode=True`, `deep_tree_echo_mode=True`, `no_system_prompt=True`
