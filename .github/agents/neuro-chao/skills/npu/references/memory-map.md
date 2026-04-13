# NPU Memory Map & Register Layout

## System Memory Map

```
0x20000000 - SRAM (256KB)      General purpose memory
0x08000000 - FLASH (1MB)       Firmware storage
0x40000000 - PERIPH (64KB)     Peripheral registers
  ├── 0x40000000 - Financial Device Registers
  ├── 0x40001000 - LLM NPU Registers
  ├── 0x40002000 - Endocrine Device Registers (extension)
  ├── 0x40003000 - Cognitive Bus Registers (extension)
  └── 0x40004000 - ASSD (AtomSpace State Drive)
```

## LLM NPU Register Layout (at 0x40001000)

| Offset | Register | Width | Access | Description |
|--------|----------|-------|--------|-------------|
| 0x00 | REG_CTRL | 32-bit | R/W | Control register (start/stop/reset) |
| 0x04 | REG_STATUS | 32-bit | R | Status (idle/busy/error/complete) |
| 0x08 | REG_MODEL_ID | 32-bit | R/W | Active model identifier |
| 0x0C | REG_CONTEXT_LEN | 32-bit | R/W | Context window length |
| 0x10 | REG_INPUT_ADDR | 32-bit | R/W | DMA input buffer address |
| 0x14 | REG_OUTPUT_ADDR | 32-bit | R/W | DMA output buffer address |
| 0x18 | REG_INPUT_LEN | 32-bit | R/W | Input token count |
| 0x1C | REG_OUTPUT_LEN | 32-bit | R | Generated token count |
| 0x20 | REG_TEMPERATURE | 32-bit | R/W | Sampling temperature (fixed-point) |
| 0x24 | REG_TOP_P | 32-bit | R/W | Top-p sampling (fixed-point) |
| 0x28 | REG_TOP_K | 32-bit | R/W | Top-k sampling |
| 0x2C | REG_TOKENS_SEC | 32-bit | R | Throughput (tokens/second) |
| 0x30 | REG_IRQ_MASK | 32-bit | R/W | Interrupt mask |
| 0x34 | REG_IRQ_STATUS | 32-bit | R/C | Interrupt status (write-1-to-clear) |

## DMA Controller (8 channels)

| Channel | Purpose | Priority |
|---------|---------|----------|
| 0 | Prompt input transfer | High |
| 1 | Token output streaming | High |
| 2 | Model weight loading | Medium |
| 3 | KV-cache management | Medium |
| 4 | Attention map export | Low |
| 5 | Embedding transfer | Low |
| 6 | Telemetry export | Low |
| 7 | Reserved | - |

## Interrupt Vectors

| Vector | IRQ | Description |
|--------|-----|-------------|
| 0x10 | NPU_COMPLETE | Inference complete |
| 0x11 | NPU_TOKEN | New token generated (streaming) |
| 0x12 | NPU_ERROR | Inference error |
| 0x13 | NPU_OOM | Out of memory |
| 0x20 | DMA_COMPLETE | DMA transfer complete |
| 0x30 | ENDO_MODE_CHANGE | Endocrine mode transition |
| 0x31 | ENDO_THRESHOLD | Hormone threshold crossed |

## GPIO Pin Mapping (64 pins)

Pins 0-15: Financial account mapping (balance as voltage 0-3.3V)
Pins 16-31: Cognitive state signals
Pins 32-47: Endocrine hormone levels (analog output)
Pins 48-63: User-configurable
