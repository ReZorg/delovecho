---
name: unreal-echo
description: Implement Deep Tree Echo cognitive avatar features and functions in any context — Unreal Engine, Unity, web, VTuber, robotics, or custom applications. Use when building cognitive avatars with Echobeats 9-step cycles, Echo State Network reservoirs, 4E embodied cognition, ontogenetic evolution, hypergraph memory, wisdom cultivation, or holistic metamodel streams. Triggers on mentions of Deep Tree Echo, cognitive avatar, Echobeats, echo state network reservoir, 4E cognition avatar, avatar evolution, or cognitive cycle implementation.
---

# Unreal Echo

Implement the Deep Tree Echo cognitive avatar architecture in any runtime context. Provides the complete cognitive pipeline — from sensory input through reservoir computing to avatar expression — adaptable to Unreal Engine, Unity, web, VTuber, robotics, or any custom application.

## Decision Tree

```
Need cognitive avatar?
├── In Unreal Engine? → Use UE5 implementation pattern below
├── In Unity? → Read references/context-adaptation.md for C# mapping
├── On the web? → Read references/context-adaptation.md for JS/TS mapping
├── For VTuber? → Read references/context-adaptation.md for Live2D/Go mapping
├── For robotics? → Read references/context-adaptation.md for ROS mapping
├── Need expression? → Compose with meta-echo-dna skill
├── Need emotions? → Compose with virtual-endocrine-system skill
├── Need LLM inference? → Compose with npu skill
└── Need checkpointing? → Compose with codex-grassmania skill
```

## Core Architecture

For full system details, read `references/cognitive-architecture.md`.

Seven interconnected systems:

| System | Purpose | Update Rate |
|--------|---------|-------------|
| Echobeats | 9-step cognitive cycle (sense→reflect) | 10-30 Hz |
| ESN Reservoir | Temporal pattern processing | Every cycle |
| 4E Cognition | Embodied/Embedded/Enacted/Extended metrics | Every cycle |
| Endocrine | 10-gland hormone system → emotional state | Every tick |
| Evolution | Ontogenetic stage progression | Every 100 cycles |
| Memory | Hypergraph associative storage (ASSD-backed) | On significant events |
| Wisdom | Morality/Meaning/Mastery/Sophrosyne | Every evolution step |
| Holistic Streams | Entropic/Negnentropic/Identity health | Every evolution step |
| NPU | LLM inference via MMIO coprocessor | On demand |

## Implementation Workflow

### 1. Set Up the Cognitive Cycle

Implement the 9-step Echobeats cycle as the main driver:

```cpp
// Unreal Engine pattern
void UCognitiveComponent::TickComponent(float DeltaTime, ...)
{
    // Endocrine pre-tick: update hormone decay and mode detection
    EndocrineSystem->Tick(DeltaTime);
    CognitiveMode Mode = EndocrineSystem->GetBus().CurrentMode();
    
    SensoryData Input = GatherSensoryInput();      // Step 1: Sense
    FocusedData Attended = ApplyAttention(Input);   // Step 2: Attend (modulated by NE)
    MemoryContext Memories = QueryMemory(Attended); // Step 3: Remember (ASSD-backed)
    Prediction Pred = GeneratePrediction(Memories); // Step 4: Predict
    float Error = ComputeError(Pred, Input);        // Step 5: Compare
    UpdateReservoir(Error);                         // Step 6: Learn
    
    // Signal endocrine events based on cognitive results
    if (Error > ErrorThreshold)
        EndocrineSystem->SignalEvent(NOVELTY_ENCOUNTERED, Error);
    if (Pred.Confidence > RewardThreshold)
        EndocrineSystem->SignalEvent(REWARD_RECEIVED, Pred.Confidence);
    
    Action Selected = SelectAction(Mode);           // Step 7: Decide (mode-aware)
    ExecuteAction(Selected);                        // Step 8: Act
    ReflectOnCycle();                               // Step 9: Reflect
    
    // NPU inference for complex reasoning (on demand)
    if (NeedsDeepReasoning(Selected))
        NPUCoprocessor->SubmitPrompt(BuildReasoningPrompt());
    
    // Checkpoint via CogMorph (periodic)
    if (ShouldCheckpoint())
        CogMorph->SaveCGGUF("latest_state.cgguf");
}
```

### 2. Initialize the ESN Reservoir

```
ReservoirSize = 512;      // Neurons
SpectralRadius = 0.9;     // Edge of chaos
LeakRate = 0.3;           // Temporal memory
Sparsity = 0.1;           // 10% connectivity
InputScaling = 0.5;       // Input amplitude

// Leaky integrator update (per cycle):
State[t] = (1 - LeakRate) * State[t-1]
         + LeakRate * tanh(W * State[t-1] + Win * Input)
Output = Wout * State[t]
```

### 3. Track 4E Cognition Metrics

Each dimension has 3-4 metrics (0.0 to 1.0):
- **Embodied:** Body schema integration, proprioceptive accuracy, somatic marker strength
- **Embedded:** Affordance detection rate, niche coupling, environmental sensitivity
- **Enacted:** Sensorimotor coordination, prediction accuracy, active inference efficiency
- **Extended:** Tool use competence, external memory integration, social cognition depth

### 4. Implement Evolution System

Track ontogenetic stage (Embryonic → Juvenile → Adolescent → Adult → Transcendent). Advance when:
```
4E_Score >= StageThreshold AND
Entelechy_Fitness >= StageThreshold AND
Wisdom_Score >= StageThreshold * 0.8 AND
Meta_Coherence >= StageThreshold * 0.7
```

### 5. Initialize Endocrine System

Connect the `virtual-endocrine-system` as the emotional substrate:

```cpp
// Initialize endocrine system with 10 glands
EndocrineSystem = NewObject<UEndocrineComponent>(this);
EndocrineSystem->ConnectAttention(AttentionBank);  // ECAN adapter
EndocrineSystem->ConnectPLN(PLNEngine);            // PLN adapter

// Register mode change callbacks
EndocrineSystem->OnModeChange.AddDynamic(this, &UCognitiveComponent::HandleModeTransition);
```

The endocrine system modulates attention (via norepinephrine), reasoning confidence (via serotonin/cortisol), and expression (via `meta-echo-dna`).

### 6. Connect NPU for Deep Reasoning

Compose with `npu` skill for LLM-backed inference:

```cpp
NPUCoprocessor = NewObject<UNPUComponent>(this);
NPUCoprocessor->LoadModel("cognitive_model.gguf");
// NPU fires IRQ on completion, handled asynchronously
NPUCoprocessor->OnInferenceComplete.AddDynamic(this, &UCognitiveComponent::HandleNPUResult);
```

### 7. Connect to Expression System

Compose with `meta-echo-dna` skill for MetaHuman expression (now endocrine-driven), or implement a custom expression mapper for your target platform.

### 8. Enable CogMorph Checkpointing

Compose with `codex-grassmania` for cognitive state persistence:

```cpp
CogMorph = NewObject<UCogMorphComponent>(this);
CogMorph->SetCheckpointInterval(1000);  // Every 1000 cycles
CogMorph->EnableASSD(PCB, ASSD_BASE);   // Hardware-backed atom storage
```

## Context Adaptation

For adapting to non-Unreal contexts, read `references/context-adaptation.md`. It provides:
- Component mapping table (UE5 → Unity → Web → VTuber → ROS)
- Minimal interface definitions for any language
- Performance budgets per platform
- Language-specific implementation notes (C++, C#, JS/TS, Go, Python)

## Composition

| Skill | Integration |
|-------|-------------|
| `virtual-endocrine-system` | 10-gland emotional substrate, cognitive mode detection |
| `meta-echo-dna` | MetaHuman expression pipeline (endocrine + FACS + chaos) |
| `npu` | LLM inference via MMIO coprocessor for deep reasoning |
| `codex-grassmania` | CogMorph checkpointing, ASSD atom storage, CGGUF format |
| `deep-tree-echo-core-self` | Identity mesh and hypergraph structure |
| `nn` | Reservoir computing patterns and training |
| `neuro-nn` | Self-aware personality traits |
| `agent-neuro` | Hyper-chaotic cognitive orchestration |
| `ec9o` | Wisdom cultivation and relevance realization |
| `Autognosis` | Hierarchical self-image building |
