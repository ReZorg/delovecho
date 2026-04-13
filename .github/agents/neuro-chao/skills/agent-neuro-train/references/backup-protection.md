# Backup Protection Policy

## Core Principle

**Backup after training is the most important thing without exception. Even partial or damaged checkpoint files must be backed up so recovery can be performed.**

## The Problem

GitHub Actions workflows execute steps sequentially. If a step fails and lacks `if: always()`, ALL subsequent steps are skipped. This means a non-critical failure (e.g., evaluation, test generation, quality gate) can cascade and prevent backup of hours of training work.

## The Solution: Defense in Depth

### Layer 1: `if: always()` on ALL post-training steps

Every step after the training run must have `if: always()` to ensure it executes regardless of upstream failures. This includes:
- Evaluation steps
- Quality gate steps
- Backup steps
- Artifact upload steps
- Git commit/push steps

### Layer 2: `continue-on-error: true` on non-critical steps

Non-critical steps (evaluation, quality gates, improvement recommendations) should have `continue-on-error: true` so their internal failures don't set the job status to `failure` and potentially affect conditional logic.

### Layer 3: Multi-location backup

Checkpoints are backed up to 3 independent locations:
1. Git repository (`.training-progress/checkpoints/`)
2. GitHub Actions cache (`.training-progress/cache/`)
3. GitHub Actions artifact (`/tmp/nanecho-checkpoint-backup/`)

### Layer 4: Emergency artifact upload

A final `if: always()` step uploads any `.pt` files found anywhere in the workspace as an emergency artifact with 90-day retention.

### Layer 5: 5-layer git push fallback

The commit/push step tries 5 strategies in order:
1. `git pull --rebase && git push`
2. `git fetch && git rebase && git push`
3. `git push --force-with-lease`
4. Push to a backup branch
5. Upload as emergency artifact

## PyTorch 2.6+ torch.load Compatibility

PyTorch 2.6 changed the default of `torch.load` from `weights_only=False` to `weights_only=True`. NanEcho checkpoints contain numpy scalar types (e.g., `numpy.core.multiarray.scalar`) which are rejected by `weights_only=True`.

**All `torch.load` calls must explicitly use `weights_only=False`.**

### Files requiring this fix:
- `.github/workflows/agent-neuro-train.yml` (inline Python)
- `.github/workflows/netrain-cached.yml` (inline Python)
- `NanEcho/convert_to_huggingface.py`
- `NanEcho/download_from_huggingface.py`
- `scripts/checkpoint_guardian.py`

### Verification command:
```bash
grep -rn "torch.load" --include="*.py" --include="*.yml" | grep -v "weights_only=False"
```

Any results from this command indicate unpatched `torch.load` calls that will fail on PyTorch 2.6+.
