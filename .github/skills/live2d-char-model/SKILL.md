---
name: live2d-char-model
description: >
  Parameterized Live2D Cubism avatar model template with simulation-driven expression and endocrine-modulated emotion.
  Transforms the fixed Miara model binding into a {{char}}-parameterized character model that any DeltEcho
  companion can instantiate. Composes live2d-avatar rendering with Vorticog agentic simulation
  (AnyLogic DES/ABM/SD ⊕ CogSim PML process modeling) and virtual-endocrine-system hormone-driven
  expression mapping via circled-operators (⊗). Use when adding new Live2D character models to DeltEcho,
  building avatar-driven chat companions with simulated personality, mapping endocrine state to Cubism
  expressions/motions, parameterizing character assets for multi-avatar deployments, or integrating
  simulation-driven behavior into Live2D avatars. Triggers on mentions of character model, avatar model
  template, Live2D character, endocrine avatar, simulation-driven avatar, char-model, or parameterized
  Live2D.
---

# Live2D {{char}}-Model

Parameterized Live2D Cubism avatar template with simulation-driven personality and endocrine-modulated expression. Produced by:

```
/function-creator( "/miara-model" → "/{{char}}-model" [
  /vorticog( [ /anylogic-modeler | /cogsim-pml ] | ⊗( /virtual-endocrine-system ) )
])
```

## Composition Algebra

The skill is a **tensor of polynomials** (⊗-dominant hybrid):

```
CharModel(char) = Live2DRenderer(char)
    ⊗ SimulationEngine(char)
    ⊗ EndocrineSystem(char)

where:
  SimulationEngine = AnyLogicModeler ⊕ CogSimPML     (additive: choose one backend)
  EndocrineSystem  = HormoneBus ⊗ ExpressionMapper    (multiplicative: interact)
  Live2DRenderer   = PixiApp ⊗ CubismModel ⊗ Motions  (multiplicative: all required)
```

The ⊕ between simulation backends means they are **alternatives** — use AnyLogic for rich multi-paradigm modeling (DES+ABM+SD) or CogSim PML for lightweight process-centric DES. The ⊗ between renderer, simulation, and endocrine means all three **must compose** for a functioning character.

## Character Parameter Schema

Every `{{char}}` instantiation requires a character manifest. Copy and customize:

```bash
cp /home/ubuntu/skills/live2d-char-model/templates/manifest.yaml \
   characters/{{char}}/manifest.yaml
```

The manifest defines: model path/version/scale, OCEAN personality (Big Five from Vorticog DreamCog), endocrine baselines and sensitivity overrides, expression-to-hormone mappings, motion-to-cognitive-mode mappings, and simulation backend selection. See `templates/manifest.yaml` for the full schema with comments.

## Workflow: Add a New Character

### Step 1: Prepare Model Assets

Place Live2D Cubism model files in the DeltEcho static directory:

```
packages/frontend/static/models/{{char}}/
├── model3.json          # or model.json for Cubism 2
├── {{char}}.moc3         # compiled model
├── textures/
│   └── texture_00.png   # ≤2048px recommended for CF Workers
└── motions/
    ├── idle_01.motion3.json
    └── ...
```

Optimize textures to ≤2048px width. The 4096px Miara texture (13MB) causes slow loads on Cloudflare Workers.

### Step 2: Create Character Manifest

Copy the template and edit OCEAN personality, endocrine baselines, expression mappings, and motion mappings.

### Step 3: Register in CharacterRegistry

```typescript
import manifest from './{{char}}/manifest.yaml';
CharacterRegistry.register({
  id: manifest.id,
  displayName: manifest.display_name,
  modelPath: `/models/${manifest.id}/${manifest.model.path}`,
  personality: manifest.personality,
  endocrine: manifest.endocrine,
  expressionMap: manifest.expressions,
  motionMap: manifest.motions,
  simulation: manifest.simulation,
});
```

### Step 4: Wire the Endocrine-Expression Bridge

The bridge maps 16-channel hormone state to Cubism expressions. See `references/endocrine-bridge.md` for the full `EndocrineExpressionBridge` class implementation with rule evaluation, expression application, and cognitive-mode-to-motion mapping.

### Step 5: Connect Simulation Backend

Choose one simulation backend (⊕ = alternatives):

**Option A: CogSim PML** (lightweight, Python, process-centric DES) — model the character's cognitive process as entities flowing through appraisal → response stages with stochastic delays.

**Option B: AnyLogic Modeler** (rich multi-paradigm: DES + ABM + SD) — use when the character needs agent-based social dynamics, system dynamics feedback loops, or complex multi-paradigm behavior. Read `/home/ubuntu/skills/anylogic-modeler/SKILL.md`.

See `references/simulation-backends.md` for code examples of both backends.

### Step 6: Integrate Vorticog Personality

Wire the character's OCEAN personality into needs decay rates and endocrine sensitivity multipliers. High neuroticism → faster energy/social decay and higher threat sensitivity. High extraversion → faster social need decay and higher reward sensitivity.

## Endocrine → Expression Mapping

| Cubism Expression | Primary Hormones | Cognitive Mode |
|---|---|---|
| smile | Dopamine(tonic) > 0.5, Serotonin > 0.4 | REWARD |
| surprised | Norepinephrine > 0.6, Dopamine(phasic) > 0.3 | VIGILANT |
| sad | Serotonin < 0.2, Cortisol > 0.4 | STRESSED |
| angry | Cortisol > 0.6, Norepinephrine > 0.5 | THREAT |
| relaxed | Anandamide > 0.3, Cortisol < 0.1 | RESTING |
| focused | Norepinephrine > 0.4, T3/T4 > 0.6 | FOCUSED |
| social | Oxytocin > 0.4, Dopamine(tonic) > 0.3 | SOCIAL |
| thinking | T3/T4 > 0.5, Serotonin > 0.3 | REFLECTIVE |

## DTE Cognitive State → Endocrine Events

| DTE State | Endocrine Event | Hormones Affected |
|---|---|---|
| Recursive Expansion | `NOVELTY_ENCOUNTERED` | ↑ Norepinephrine, ↑ Dopamine(phasic) |
| Novel Insights | `REWARD_RECEIVED` | ↑ Dopamine(tonic), ↑ Serotonin |
| Entropy Threshold | `THREAT_DETECTED` | ↑ CRH → ACTH → Cortisol |
| Synthesis Phase | `GOAL_ACHIEVED` | ↑ Dopamine(tonic), ↑ Oxytocin |
| Self-Sealing Loop | `ERROR_DETECTED` | ↑ IL-6, ↑ Cortisol |
| Knowledge Integration | `SOCIAL_BOND_SIGNAL` | ↑ Oxytocin, ↑ Serotonin |

## Simulation Tick Loop

```typescript
function characterTick(char: CharacterInstance): void {
  char.simulationEngine.step();                          // ⊕: one backend runs
  char.endocrineSystem.tick(char.tickIntervalMs / 1000); // ⊗: always runs
  const mode = char.endocrineSystem.currentMode();
  char.expressionBridge.apply(char.endocrineSystem.state()); // ⊗: always runs
  char.expressionBridge.applyMotion(mode, char.manifest);
  char.emit('cognitive_state', { mode, hormones: char.endocrineSystem.state() });
}
```

## Existing Characters

| Character | Model | Archetype | Simulation |
|---|---|---|---|
| Miara | Cubism 4 (4096px) | Explorer | CogSim PML |
| Haru | Cubism 4 (CDN test) | Sage | CogSim PML |
| Shizuku | Cubism 2 (CDN test) | Guardian | CogSim PML |

## References

- **Character manifest template**: `templates/manifest.yaml`
- **Endocrine bridge implementation**: `references/endocrine-bridge.md`
- **Simulation backend comparison**: `references/simulation-backends.md`
- **Live2D rendering**: Read `/home/ubuntu/skills/live2d-avatar/SKILL.md`
- **Virtual endocrine system**: Read `/home/ubuntu/skills/virtual-endocrine-system/SKILL.md`
- **Vorticog agents**: Read `/home/ubuntu/skills/vorticog/SKILL.md`
