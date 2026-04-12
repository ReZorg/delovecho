---
name: unreal-blueprint
description: "Unreal Engine 5 Blueprint visual scripting patterns for implementing Deep Tree Echo / MetaHuman DNA cognitive avatars with realistic character behaviors. Use when building UE5 Blueprints for MetaHuman facial animation, Rig Logic integration, cognitive cycle tick graphs, expression state machines, Live Link face capture, Nakama multiplayer, or any Blueprint-driven character behavior system. Covers Animation Blueprints, Actor Components, Event Graphs, and Blueprint-C++ hybrid patterns. Triggers on mentions of Unreal Blueprint, UE5 Blueprint, Animation Blueprint, MetaHuman Blueprint, Blueprint visual scripting, or character behavior Blueprint."
---

# Unreal Blueprint

UE5 Blueprint visual scripting patterns for Deep Tree Echo cognitive avatars with MetaHuman DNA expression.

## Decision Tree

```
What are you building?
├── MetaHuman facial animation? → See "Expression Pipeline Blueprint" below
├── Cognitive avatar behavior? → See "Cognitive Cycle Blueprint" below
├── Multiplayer character sync? → See "Nakama Integration Blueprint" below
├── Live face capture? → See references/livelink_blueprint.md
├── Expression state machine? → See references/expression_statemachine.md
├── Custom Rig Logic control? → Compose with rig-logic skill
└── Full DTE avatar? → Use all patterns together
```

## Core Blueprint Architecture

The DTE MetaHuman avatar uses four Blueprint layers:

| Layer | Blueprint Type | Purpose |
|-------|---------------|--------|
| **Cognitive** | Actor Component (BP_CognitiveComponent) | 9-step Echobeats cycle, ESN reservoir, 4E metrics |
| **Expression** | Actor Component (BP_ExpressionBridge) | FACS AU values → MetaHuman morph targets via Rig Logic |
| **Animation** | Animation Blueprint (ABP_MetaHuman_DTE) | AnimGraph with RigLogic node, blend spaces, state machine |
| **Behavior** | Actor Blueprint (BP_DTECharacter) | Top-level character with all components wired together |

## Expression Pipeline Blueprint

### BP_ExpressionBridge Component

Bridges cognitive/endocrine state to MetaHuman Rig Logic controls.

**Variables** — 20 FACS AU float values (AU1, AU2, AU4–AU26, AU43), Lorenz attractor state (Vector), ChaosIntensity (0.15), aesthetic parameters (ConfidencePosture, Charisma, EyeSparkle).

**Event Graph — Tick:**

```
Event Tick (DeltaTime)
├─ [1] Get Cognitive Component → Read Valence, Arousal, CogLoad
├─ [2] Get Endocrine Component → Read 16 Hormone Channels
├─ [3] Compute Hormone-Driven AUs
│   ├─ Cortisol → AU4(v*0.6) + AU1(v*0.3) + AU15(v*0.4)
│   ├─ Dopamine(phasic) → AU12(v*0.8) + AU6(v*0.6)
│   ├─ Norepinephrine → AU5(v*0.5) + AU7(v*0.3)
│   ├─ Oxytocin → AU6(v*0.4) + AU12(v*0.5) + AU25(v*0.3)
│   └─ Melatonin → AU43(v*0.8)
├─ [4] Compute Cognitive-Driven AUs
│   ├─ Valence(+) → AU6(v*0.5) + AU12(v*0.6)
│   ├─ Valence(-) → AU15(v*0.5) + AU4(v*0.3)
│   ├─ Arousal → AU5(v*0.4) + AU25(v*0.3) + AU26(v*0.2)
│   └─ CogLoad → AU4(v*0.4) + AU7(v*0.3)
├─ [5] Blend: Sum all AU contributions, Clamp(0.0, 1.0)
├─ [6] Step Lorenz Attractor (RK4), add chaos noise
├─ [7] Apply Aesthetic Biases (Confidence → bias AU12)
├─ [8] Map AU Values → CTRL_ Morph Targets (see references/au_to_ctrl_mapping.md)
└─ [9] Apply to Skeletal Mesh Component
```

### ABP_MetaHuman_DTE Animation Blueprint

**AnimGraph:** `[Pose Input] → [RigLogic Node] → [Blend by Expression State] → [Output Pose]`

The RigLogic Node (`FAnimNode_RigLogic`) reads control values from BP_ExpressionBridge and evaluates the full Rig Logic pipeline.

**Expression State Machine:**

| State | Entry Condition | Active AUs |
|-------|----------------|------------|
| Idle | Default | Micro-expressions only (Lorenz layer) |
| Speaking | Speech input detected | AU25+AU26 (viseme-driven) |
| Emoting | Valence > 0.3 or Arousal > 0.4 | All AUs (full expression) |
| Listening | Other agent speaking | Subtle AU tracking (empathy mirror) |
| Transitioning | Any state change | Blend over 0.15–0.3s |

## Cognitive Cycle Blueprint

### BP_CognitiveComponent

9-step Echobeats cycle as Actor Component, ticked at 10–30 Hz via timer.

```
Custom Event: CognitiveTick
├─ [1] Sense: Gather sensory input
├─ [2] Attend: Apply attention filter (NE-modulated)
├─ [3] Remember: Query hypergraph memory
├─ [4] Predict: Generate prediction from memory
├─ [5] Compare: Compute prediction error
├─ [6] Learn: Update ESN reservoir
├─ [7] Decide: Select action (mode-aware)
├─ [8] Act: Execute selected action
└─ [9] Reflect: Update 4E metrics, check evolution
```

**ESN Parameters:** ReservoirSize=512, SpectralRadius=0.9, LeakRate=0.3, Sparsity=0.1.

## Nakama Integration Blueprint

Multiplayer character sync using Nakama open-source game server.

```
Event BeginPlay
├─ Create Default Client (Host: localhost, Port: 7350, ServerKey: defaultkey)
├─ SET → NakamaClient
├─ AuthenticateCustom (Client, UserID, Username, CreateAccount: true)
│   ├─ On Success → SET Session → Join/Create Match
│   └─ On Error → Break Nakama Error → Print String
└─ SyncExpressionState (10 Hz timer)
    ├─ Serialize AU map → JSON
    ├─ Send Match State (Opcode: 1)
    └─ On Receive: Deserialize → Apply to remote character
```

## Blueprint-C++ Hybrid Pattern

For performance-critical paths, expose C++ to Blueprint:

```cpp
UCLASS(BlueprintType, Blueprintable)
class UDTERigLogicBridge : public UActorComponent
{
    UFUNCTION(BlueprintCallable, Category = "DTE|Expression")
    void SetActionUnit(int32 AUNumber, float Value);

    UFUNCTION(BlueprintCallable, Category = "DTE|Expression")
    void SetEmotionPreset(FName PresetName, float Intensity);

    UFUNCTION(BlueprintPure, Category = "DTE|Cognition")
    ECognitiveMode GetCurrentMode() const;

    UFUNCTION(BlueprintImplementableEvent, Category = "DTE|Cognition")
    void OnModeTransition(ECognitiveMode OldMode, ECognitiveMode NewMode);
};
```

## Composition

| Skill | Integration |
|-------|------------|
| `rig-logic` | DNA file format, corrective expressions, LOD, joint groups |
| `facs` | AU numbering, emotion decomposition, MH Standards mapping |
| `meta-echo-dna` | Cognitive state → FACS AUs, Lorenz attractor, aesthetics |
| `unreal-echo` | Full DTE cognitive architecture (Echobeats, ESN, 4E) |
| `echo-angel` | Complete cognitive avatar composition |
| `virtual-endocrine-system` | 10-gland hormone system driving expression |

## Bundled Resources

| Path | Description |
|------|------------|
| `references/au_to_ctrl_mapping.md` | Complete FACS AU → MetaHuman CTRL_ morph target mapping |
| `references/expression_statemachine.md` | Expression state machine with transition rules |
| `references/livelink_blueprint.md` | Live Link face capture Blueprint patterns |
| `references/nakama_blueprint.md` | Full Nakama multiplayer Blueprint patterns |
| `scripts/generate_bp_json.py` | Generate Blueprint JSON for UE5 editor import |
