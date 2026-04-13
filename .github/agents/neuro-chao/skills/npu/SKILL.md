---
name: npu
description: >
  Build and operate Neural Processing Unit virtual hardware abstractions for LLM integration.
  Use when modeling LLM inference as memory-mapped peripheral devices, creating virtual PCB architectures
  with MMIO registers, DMA controllers, and interrupt systems, or integrating GGUF-backed coprocessors
  into cognitive systems. Covers VirtualPCB, LLM coprocessor drivers, financial hardware platforms,
  telemetry dashboards, and CogMorph multi-projection state transforms.
  Triggers on mentions of NPU, neural processing unit, virtual hardware, MMIO registers,
  LLM coprocessor, virtual PCB, or hardware-first LLM integration.
---

# NPU — Neural Processing Unit Coprocessor

Hardware-first abstraction framework that models GGUF-backed LLM inference as memory-mapped peripheral devices within a virtual PCB architecture.

## Architecture

```
┌─────────────────────────────────────────────┐
│              Application Layer               │
│    CLI Admin  │  Cognitive Sim  │  Tests     │
├─────────────────────────────────────────────┤
│            Device Driver Layer               │
│  Financial Driver    │  LLM Coprocessor      │
│  (0x40000000)        │  (0x40001000)         │
├─────────────────────────────────────────────┤
│            Virtual PCB Hardware               │
│  Memory │ GPIO(64) │ DMA(8ch) │ IRQ(256)    │
│  SRAM(256KB) │ FLASH(1MB) │ PERIPH(64KB)    │
└─────────────────────────────────────────────┘
```

For full architecture diagrams, read `references/architecture_overview.md`.

## Core Components

### VirtualPCB

Complete simulation of physical hardware device with memory regions, power management, and I/O interfaces.

```cpp
class VirtualPCB {
    MemoryRegion sram_{0x20000000, 256 * 1024};   // 256KB SRAM
    MemoryRegion flash_{0x08000000, 1024 * 1024};  // 1MB FLASH
    MemoryRegion periph_{0x40000000, 64 * 1024};   // 64KB Peripherals
    DMAController dma_{8};                          // 8 channels
    InterruptController irq_{256};                  // 256 vectors
    GPIO gpio_{64};                                 // 64 pins
    PowerManagement power_{{3.3f, 5.0f}};          // Voltage rails
};
```

### LLM Coprocessor Driver (at 0x40001000)

Memory-mapped interface for LLM inference:

```cpp
pcb.write32(NPU_BASE + REG_INPUT_ADDR, prompt_dma_addr);
pcb.write32(NPU_BASE + REG_INPUT_LEN, token_count);
pcb.write32(NPU_BASE + REG_TEMPERATURE, float_to_fixed(0.7f));
pcb.write32(NPU_BASE + REG_CTRL, CTRL_START);

while (!(pcb.read32(NPU_BASE + REG_STATUS) & STATUS_COMPLETE)) {}
uint32_t output_len = pcb.read32(NPU_BASE + REG_OUTPUT_LEN);
```

For full register layout and memory map, read `references/memory-map.md`.

### DMA Controller

8-channel Direct Memory Access. Channels 0-1 high-priority for prompt I/O, channels 2-3 for model weights and KV-cache.

### Interrupt System

256 vectors with priority handling. Key vectors:
- `NPU_COMPLETE` (0x10): Inference finished
- `NPU_TOKEN` (0x11): Streaming token available
- `ENDO_MODE_CHANGE` (0x30): Endocrine cognitive mode transition

### GPIO Pin Mapping (64 pins)

- Pins 0-15: Financial accounts (balance as voltage)
- Pins 16-31: Cognitive state signals
- Pins 32-47: Endocrine hormone levels (analog output)
- Pins 48-63: User-configurable

## CogMorph: Multi-Projection State Transforms

A single cognitive state projected isomorphically into 5 representations:

| Projection | Interface | Use Case |
|------------|-----------|----------|
| Hardware | MMIO registers, DMA | Real-time control, debugging |
| Library | C++ API objects | Application development |
| Static | CGGUF format | Persistence, checkpointing |
| Network | Wire protocols | Distributed systems |
| Glyph | Visual font-based | Visualization, inspection |

Transforms are bidirectional and preserve cognitive semantics.

## Integration Workflow

### 1. Initialize Virtual Hardware

```cpp
VirtualPCB pcb;
LLMCoprocessorDriver npu(pcb, NPU_BASE);
npu.load_model("model.gguf");
```

### 2. Connect Cognitive Subsystems

Map OpenCog components to virtual hardware:
- vCPU = URE (Unified Rule Engine)
- vGPU = SIMD PLN (truth value computation)
- vNPU = LLM coprocessor (neural inference)
- vTPU = Truth value processor
- vAPU = ECAN (attention allocation)

### 3. Run Cognitive Loop

```cpp
while (running) {
    endo.tick(dt);
    for (int i = 0; i < 16; i++)
        pcb.gpio_write(32 + i, endo.bus().concentration(HormoneId(i)));
    
    if (needs_inference) {
        npu.submit_prompt(prompt);
        pcb.irq_wait(NPU_COMPLETE);
        auto result = npu.read_output();
    }
    telemetry.export_metrics(pcb);
}
```

## Composition

| Skill | Integration |
|-------|-------------|
| `virtual-endocrine-system` | Hormone levels mapped to GPIO pins 32-47 |
| `codex-grassmania` | CogMorph projections and ASSD storage device |
| `unreal-echo` | NPU as inference backend for cognitive cycle |
| `meta-echo-dna` | NPU generates expression parameters from cognitive state |
| `nn` | Reservoir state accessible via MMIO registers |
| `deep-tree-echo-core-self` | Identity mesh stored in ASSD |
