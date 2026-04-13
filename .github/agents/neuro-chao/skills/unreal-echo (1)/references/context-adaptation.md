# Context Adaptation Guide

## Adapting Deep Tree Echo to Different Contexts

The Deep Tree Echo architecture is context-agnostic at its core. This guide shows how to adapt it beyond Unreal Engine.

## Context Mapping Table

| Deep Tree Echo Component | Unreal Engine | Unity | Web (Three.js) | VTuber (Live2D) | Robotics (ROS) |
|--------------------------|---------------|-------|-----------------|-----------------|----------------|
| Echobeats Cycle | UActorComponent::TickComponent | MonoBehaviour.Update | requestAnimationFrame | Live2D Cubism update | ROS timer callback |
| ESN Reservoir | C++ module in plugin | C# ScriptableObject | WebAssembly module | Go backend service | C++ ROS node |
| 4E Cognition | UObject properties | ScriptableObject fields | JavaScript state | JSON config | ROS parameters |
| Morph Targets | SetMorphTarget on SkeletalMesh | SkinnedMeshRenderer.SetBlendShapeWeight | morphTargetInfluences | CubismParameter | Joint commands |
| Material Updates | Dynamic Material Instance | Material.SetFloat | ShaderMaterial.uniforms | Cubism drawable opacity | LED/display control |
| Bone Control | FAnimNode_ModifyBone | Animator.SetBoneLocalRotation | Bone.rotation | CubismModel parts | Servo positions |
| Memory System | UDataAsset or SQLite | ScriptableObject or JSON | IndexedDB or localStorage | File-based JSON | ROS bag or database |
| Input Sensing | UInputComponent | Input.GetAxis | addEventListener | Audio/video capture | Sensor topics |

## Minimal Implementation (Any Context)

Every context needs these five components:

### 1. Cognitive Cycle Runner
```
interface ICognitiveCycle {
    sense(): SensoryData
    process(data: SensoryData): CognitiveState
    act(state: CognitiveState): void
    reflect(): void
}
```

### 2. Reservoir Computer
```
interface IReservoir {
    initialize(size: int, spectralRadius: float, leakRate: float)
    update(input: float[]): float[]
    readout(): float[]
}
```

### 3. Expression Mapper
```
interface IExpressionMapper {
    mapCognitiveToAU(state: CognitiveState): ActionUnitValues
    addChaoticNoise(aus: ActionUnitValues): ActionUnitValues
    applyAesthetics(aus: ActionUnitValues): ActionUnitValues
    applyToAvatar(aus: ActionUnitValues): void
}
```

### 4. Memory System
```
interface IMemorySystem {
    store(fragment: MemoryFragment): void
    retrieve(query: MemoryQuery): MemoryFragment[]
    associate(a: MemoryFragment, b: MemoryFragment, type: string): void
}
```

### 5. Evolution Tracker
```
interface IEvolutionTracker {
    getCurrentStage(): OntogeneticStage
    update4EMetrics(metrics: FourEMetrics): void
    checkAdvancement(): bool
    getWisdomScore(): float
}
```

## Performance Budgets

| Context | Target FPS | Cycle Budget | Reservoir Budget | Expression Budget |
|---------|-----------|-------------|-----------------|-------------------|
| Unreal Engine (game) | 60 | 2ms | 1ms | 0.5ms |
| Unreal Engine (cinematic) | 30 | 5ms | 3ms | 1ms |
| Unity (mobile) | 30 | 3ms | 2ms | 1ms |
| Web (Three.js) | 60 | 2ms | 1ms | 0.5ms |
| VTuber (Live2D) | 30 | 5ms | 3ms | 1ms |
| Robotics (ROS) | 10 | 50ms | 20ms | 10ms |

## Language-Specific Notes

### C++ (Unreal/Robotics)
- Use `TArray<float>` for reservoir state, `TMap<FString, float>` for AU values
- Leverage SIMD for reservoir matrix multiplication
- Use `FRunnable` for async cognitive cycle

### C# (Unity)
- Use `NativeArray<float>` with Burst compiler for reservoir
- Implement as `MonoBehaviour` with `FixedUpdate` for consistent timing
- Use Jobs system for parallel reservoir updates

### JavaScript/TypeScript (Web)
- Use `Float32Array` for reservoir, consider WebAssembly for heavy math
- Use Web Workers for cognitive cycle to avoid blocking main thread
- Use `SharedArrayBuffer` for zero-copy reservoir state sharing

### Go (VTuber backend)
- Use goroutines for concurrent cognitive cycle steps
- Implement reservoir with `gonum` matrix library
- Serve expression state via HTTP/WebSocket to Live2D frontend

### Python (Prototyping/Research)
- Use NumPy for reservoir, SciPy for Lorenz integration
- Use ReservoirPy for production ESN implementation
- Use asyncio for concurrent cognitive cycle
