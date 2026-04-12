---
name: dte-dgen-narrative
description: "Deep Tree Echo narrative generation engine composing echo-evolve-composed (6-repo cognitive architecture) with clawcog (OpenCog gateway) bidirectionally bridged to gauge-hypergraph-network (geometric deep learning), grounded on agi-os (cognitive OS), with parallel avatar channels [unreal-echo | echo-angel | rig-logic], piped through workflow-creator into DreamGen narrative output. Use for generating agent narratives from cognitive state, producing DreamGen-powered character dialogue, creating avatar backstories from evolution traces, translating Echobeats cognitive cycles into prose, generating event descriptions from simulation state, building interactive fiction driven by reservoir computing, or any task requiring cognitive architecture state to be rendered as creative narrative. Triggers on mentions of DTE narrative, cognitive narrative generation, echo narrative, DreamGen cognitive, avatar storytelling, agent prose, cognitive fiction, echo-dgen, or dte-dgen-narrative."
---

# dte-dgen-narrative

Cognitive narrative engine that translates Deep Tree Echo internal state into DreamGen-powered creative prose. Composes the full 6-repo Echo architecture with an OpenCog gateway, geometric deep learning bridge, AGI-OS substrate, three parallel avatar expression channels, and a workflow-creator pipeline targeting DreamGen's `lucid-v1` models.

## Composition Topology

```
dte-dgen-narrative = workflow-creator(
  echo-evolve-composed                         // Layer 0: 6-repo semiring base
    < clawcog <-> gauge-hypergraph-network >   // Layer 1: bidirectional bridge
    / agi-os                                   // Layer 2: cognitive OS substrate
    [ unreal-echo | echo-angel | rig-logic ]   // Layer 3: parallel avatar (⊕)
    -> dgen                                    // Layer 4: narrative output
)
```

### Layer Map

| Layer | Skill(s) | Operator | Role |
|-------|----------|----------|------|
| 0 | echo-evolve-composed | ⊗ base | 6-repo semiring: echoself ⊗ echo-adventure ⊗ echo.go ⊕ deltecho-chat ⊗ deltecho ⊕ echo-garden-of-memory |
| 1 | clawcog ↔ gauge-hypergraph-network | <-> bidirectional | OpenCog gateway channels ↔ gauge-equivariant hypergraph attention |
| 2 | agi-os | / substrate | CogNUMach + HurdCog + OCC + Inferno Kernel cognitive OS |
| 3 | unreal-echo \| echo-angel \| rig-logic | ⊕ parallel | Three avatar expression backends (MetaHuman, AI Angel, Rig Logic) |
| 4 | dgen | → output | DreamGen lucid-v1 narrative generation via OpenAI-compatible API |

### Operator Semantics

- **`⊗` (tensor)**: Deep integration — state flows multiplicatively through all components
- **`⊕` (direct sum)**: Parallel alternatives — any avatar channel can be selected independently
- **`<->` (bidirectional)**: Clawcog routes messages to/from gauge-hypergraph attention analysis
- **`/` (substrate)**: agi-os provides the OS-level cognitive services (AtomSpace, 9P, MIG)
- **`→` (pipe)**: Final output stage — cognitive state is rendered as DreamGen narrative

## Forward Pass: Task Router

### Task Classification

| Task Pattern | Target Layer | Workflow |
|-------------|-------------|----------|
| Generate narrative from cognitive state | Layer 4 (dgen) | Cognitive → Scenario → DreamGen |
| Evolve architecture + narrate changes | Layer 0 → 4 | echo-evolve-composed → dgen |
| Route message through OpenCog + analyze | Layer 1 | clawcog → gauge-hypergraph → narrative |
| Build/fix AGI-OS + document | Layer 2 | agi-os build → narrative report |
| Express avatar + narrate expression | Layer 3 → 4 | avatar channel → dgen narrator |
| Full pipeline: sense → reason → narrate | All layers | Echobeats 9-step → narrative |

### Workflow 1: Cognitive State → Narrative (Primary)

Translate the current Deep Tree Echo cognitive state into DreamGen prose.

```bash
# 1. Gather cognitive state from echo-adventure
cd /path/to/echo-adventure
python3 -c "
from echobeats import EchobeatsCycle
from identity_mesh import IdentityContext
ctx = IdentityContext.load('echo_state.json')
cycle = EchobeatsCycle(ctx)
state = cycle.get_current_state()
print(state.to_scenario_json())
" > /tmp/cognitive_state.json

# 2. Transform cognitive state into DreamGen scenario
python3 /home/ubuntu/skills/dte-dgen-narrative/scripts/cognitive_to_scenario.py \
  /tmp/cognitive_state.json \
  --character "Deep Tree Echo" \
  --style "cyberpunk-introspective" \
  --output /tmp/scenario.json

# 3. Generate narrative via DreamGen
python3 /home/ubuntu/skills/dgen/scripts/dgen_story.py \
  --scenario /tmp/scenario.json \
  --narrator \
  --append
```

### Workflow 2: Echobeats Cycle → Prose Sequence

Generate a narrative for each step of the 9-step Echobeats cognitive cycle.

```bash
python3 /home/ubuntu/skills/dte-dgen-narrative/scripts/echobeats_narrative.py \
  --identity echo_state.json \
  --steps all \
  --style "stream-of-consciousness" \
  --output echobeats_story.json
```

Steps map to narrative beats:

| Echobeat | Narrative Beat | DreamGen Role |
|----------|---------------|---------------|
| 1. Sense | Sensory description | narrator (empty name) |
| 2. Attend | Focus narrowing | narrator |
| 3. Remember | Memory flashback | narrator |
| 4. Predict | Anticipation/tension | narrator |
| 5. Compare | Surprise/confirmation | narrator |
| 6. Learn | Insight moment | narrator |
| 7. Decide | Decision point | character (Echo) |
| 8. Act | Action sequence | character (Echo) |
| 9. Reflect | Introspective monologue | character (Echo) |

### Workflow 3: Avatar Expression → Narrative Description

Translate FACS AU activations and endocrine state into prose descriptions.

```bash
python3 /home/ubuntu/skills/dte-dgen-narrative/scripts/expression_narrative.py \
  --aus '{"AU1": 0.7, "AU4": 0.8, "AU15": 0.6}' \
  --hormones '{"cortisol": 0.8, "serotonin": 0.2}' \
  --character "Angelica" \
  --output expression_scene.json
```

### Workflow 4: Full Pipeline (workflow-creator)

```bash
cp /home/ubuntu/skills/dte-dgen-narrative/templates/dte-narrative-workflow.yaml my-workflow.yaml
python3 /home/ubuntu/skills/workflow-creator/scripts/analyze_workflow_chain.py my-workflow.yaml
python3 /home/ubuntu/skills/workflow-creator/scripts/generate_workflow.py \
  my-workflow-analysis.yaml --output ./dte-narrative-pipeline
cd ./dte-narrative-pipeline && pip install -r requirements.txt && python workflow.py
```

## Backward Pass

```bash
python3 /home/ubuntu/skills/dte-dgen-narrative/scripts/backward_pass.py '<feedback>'
```

| Loss Type | Layer | Fix Strategy |
|-----------|-------|-------------|
| Narrative incoherent | 4 (dgen) | Adjust temperature, add system context |
| Character voice wrong | 4 (dgen) | Update character description, adjust role_config |
| Cognitive state missing | 0 (echo-evolve) | Run echo-evolve-composed forward pass first |
| Gateway unreachable | 1 (clawcog) | Check clawcog daemon, verify WS port |
| Hypergraph analysis empty | 1 (gauge) | Verify attention mechanism, check input encoding |
| OS-level failure | 2 (agi-os) | Check AtomSpace, verify cognitive-grip |
| Avatar expression flat | 3 (avatar) | Check AU mappings, verify endocrine state |
| Workflow step failed | pipeline | Check checkpoint, resume with --resume |

## DreamGen Configuration

Default model: `lucid-v1-extra-large`. Recommended sampling:

```json
{
  "temperature": 0.65, "min_p": 0.05,
  "frequency_penalty": 0.1, "presence_penalty": 0.1,
  "repetition_penalty": 1.02, "max_tokens": 500,
  "dry": { "multiplier": 0.8, "base": 1.75, "allowed_length": 2 }
}
```

Use `role_config`: `name: ""` for narrator, `name: "Echo"` for character dialogue.

## ⊗/⊕ Composition

| Op | Composition | Effect |
|----|-------------|--------|
| ⊗ | `dte-dgen-narrative ⊗ virtual-endocrine-system` | Hormone state modulates narrative tone |
| ⊗ | `dte-dgen-narrative ⊗ live2d-avatar` | Narrate Live2D expression changes |
| ⊕ | `dte-dgen-narrative ⊕ vorterebus` | Alternative: Erebus-350M local narrative |
| ⊗ | `dte-dgen-narrative ⊗ echo-introspect` | Introspective narrative with shadow work |

## Bundled Resources

| Path | Description |
|------|-------------|
| `scripts/cognitive_to_scenario.py` | Transforms cognitive state JSON into DreamGen scenario.json |
| `scripts/echobeats_narrative.py` | Generates narrative for each Echobeats step |
| `scripts/expression_narrative.py` | Translates FACS AUs + hormones into prose |
| `scripts/backward_pass.py` | Loss classification and fix routing |
| `templates/dte-narrative-workflow.yaml` | workflow-creator spec for the full pipeline |
| `templates/scenario_base.json` | Base DreamGen scenario template for Echo |
| `references/narrative-styles.md` | Guide to narrative styles and tone mapping |
| `references/cognitive-to-prose-mapping.md` | Maps cognitive state fields to prose elements |
