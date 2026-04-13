---
name: alp-multi-method
description: Generates valid AnyLogic .alp XML project files for target simulation models. Composes target-to-anylogic with a reverse-engineered AnyLogic XML schema generator. Use when the user requests an actual AnyLogic model file (.alp) for a target system, business, or process.
---

# AnyLogic ALP Multi-Method Generator

This skill generates valid AnyLogic `.alp` XML project files from a target description. It acts as a bridge between conceptual simulation design (via `target-to-anylogic`) and the proprietary AnyLogic XML format.

## Core Workflow

When tasked with generating an AnyLogic `.alp` file for a target system, follow these steps:

1. **Decompose the Target** (using `target-to-anylogic`)
2. **Create the JSON Specification**
3. **Generate the `.alp` File**
4. **Deliver the File**

### Step 1: Decompose the Target

First, use the `target-to-anylogic` skill to decompose the target system into P49 patterns and determine the appropriate simulation paradigms (SD, DES, ABM).

```bash
python /home/ubuntu/skills/target-to-anylogic/scripts/decompose_target.py "Description of the target system" --output /home/ubuntu/target_spec.json
```

### Step 2: Create the JSON Specification

Based on the decomposition, create a detailed JSON specification for the AnyLogic model. The specification must follow the schema expected by the generator.

Create a file `model_spec.json` with the following structure:

```json
{
  "name": "Model Name",
  "description": "Description of the model",
  "package_name": "model_package",
  "time_unit": "Minute",
  "final_time": 480.0,
  "paradigms": ["SD", "DES", "ABM"],
  "variables": [
    {"class": "StockVariable", "name": "Money", "initial_value": "1000", "x": 150, "y": 100},
    {"class": "Flow", "name": "Expenses", "formula": "100", "source_name": "Money", "x": 150, "y": 100},
    {"class": "AuxVariable", "name": "Rate", "formula": "sin(time())", "x": 300, "y": 100}
  ],
  "flowchart_blocks": [
    {"class": "Source", "name": "source", "params": {"rate": {"code": "1", "unit_class": "RateUnits", "unit": "PER_MINUTE"}}, "x": 50, "y": 300},
    {"class": "Queue", "name": "queue", "params": {"capacity": "100"}, "x": 150, "y": 300},
    {"class": "Service", "name": "service", "params": {"delayTime": "triangular(1,3,5)"}, "x": 250, "y": 300},
    {"class": "Sink", "name": "sink", "x": 350, "y": 300}
  ],
  "connections": [
    {"from": "source", "to": "queue"},
    {"from": "queue", "to": "service"},
    {"from": "service", "to": "sink"}
  ],
  "statechart": {
    "states": [
      {"name": "Idle", "x": 500, "y": 100, "width": 100, "height": 30},
      {"name": "Working", "x": 500, "y": 170, "width": 100, "height": 30}
    ],
    "transitions": [
      {"name": "Start", "from": "Idle", "to": "Working", "trigger": "condition", "condition": "queue.size() > 0", "action": ""},
      {"name": "Finish", "from": "Working", "to": "Idle", "trigger": "timeout", "timeout": "1", "timeout_unit": "MINUTE", "action": ""}
    ]
  },
  "events": [
    {"name": "myEvent", "trigger": "condition", "condition": "Money <= 0", "action": "traceln(\"triggered\");", "mode": "occuresOnce"}
  ],
  "functions": [],
  "agent_classes": [],
  "libraries": ["processmodeling"]
}
```

*Note: For detailed XML element structures and supported parameters, refer to `references/alp_element_templates.md` and `references/alp_schema.json`.*

### Step 3: Generate the `.alp` File

Run the generator script to produce the AnyLogic project file:

```bash
python /home/ubuntu/skills/alp-multi-method/scripts/generate_alp.py /home/ubuntu/model_spec.json --output /home/ubuntu/
```

This will create a file named `Model_Name.alp` in the output directory.

### Step 4: Deliver the File

Use the `message` tool to deliver the generated `.alp` file to the user, explaining the multimethod architecture and how the P49 patterns mapped to the AnyLogic constructs.

## Supported AnyLogic Constructs

The generator supports the following AnyLogic elements:
- **System Dynamics**: `StockVariable`, `Flow`, `AuxVariable`
- **Discrete Event (Process Modeling Library)**: `Source`, `Sink`, `Queue`, `Delay`, `Service`, `Hold`, `ResourcePool`, `SelectOutput`, `Combine`, `Seize`, `Release`
- **Agent-Based**: `StatechartElement` (`State`, `Transition`, `EntryPoint`), `Event`, `Function`, custom `ActiveObjectClass`
- **General**: `PlainVariable`, `Parameter`

## Composition Architecture

This skill implements the composition:
`ALP = Target ⊗ (target-to-anylogic) ⊗ (XML_Schema_Generator)`
