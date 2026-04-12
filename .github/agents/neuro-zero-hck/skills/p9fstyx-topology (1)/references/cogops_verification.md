# CogOps Verification Results

Verified 2026-03-02 via `marduk-cogops-test` worker deployed to Cloudflare.

## Full Cognitive Cycle Summary

- **Phases**: 8
- **Elapsed**: ~7.6s
- **All Healthy**: true

| Subsystem | Status | Key Metrics |
|---|---|---|
| topology | ok | β₀=1, 5 bindings connected, cross-namespace bidirectional |
| marduk_memory | ok | 4 types, 0.4% utilization, read-back verified |
| atomspace | ok | 10 atoms (5 nodes, 5 links), BindLink match: [P9Fstyx, AtomSpace, MOSES] |
| p9fstyx | ok | 9 PowerScribe modules, 9-node kernel mesh (density 0.639), 4 λ-promises |
| ecan_attention | ok | 5 subsystems allocated, spreading activation + decay applied |
| wave_field | ok | 5 steps, 65.74% energy dissipated |
| gauge_kernel | ok | U1(3), curvature norm 0.112, holonomy 0.005 |
| task_metrics_moses | ok | Gen 1, best fitness 0.97, converged (threshold 0.7) |

## Deployment Chain

1. `ReZorg/marduk-ml-sdk` wrangler.jsonc → Cloudflare Pages (Worker Version `1c505f4e`)
2. `marduk-cogops-test` worker → `https://marduk-cogops-test.dan-cdc.workers.dev` (Version `b18ac275`)

## KV Namespace Verification

All namespaces tested with write-read-delete probe cycle:

```
MARDUK_KV:      bed8f7fba72f4101bf7cf5fdfa43fbd3  ✓
TASK_METRICS:   94599ec5a4af49a4bc66c8815e85a1d8  ✓
ATOMSPACE_KV:   5b5c50565a984a85b0967bd06683b27d  ✓
P9FSTYX_STATE:  12d928e7197a4799bb57b68fd9975198  ✓
MardukStore:    1ecc1e3d85c745d387c675dd7bfd4d93  ✓
DB (D1):        7e2e03fa-1b31-4355-a4ee-4a6e3d5ff60e  ✓
```
