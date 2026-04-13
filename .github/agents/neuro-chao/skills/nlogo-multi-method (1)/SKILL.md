---
name: nlogo-multi-method
description: Generates valid NetLogo .nlogo project files for target simulation models. Composes target-to-anylogic decomposition with a NetLogo code generator. Use when the user requests a NetLogo model file (.nlogo) for a target system, business, process, ecosystem, or any agent-based simulation.
---

# NetLogo Multi-Method Generator

## Description
This skill converts any target (a business, a process, a system, a supply chain, an ecosystem, etc.) into a runnable NetLogo simulation model. It first uses the `target-to-anylogic` skill's P49 pattern decomposition to understand the system dynamics, then maps those dynamics to NetLogo constructs (turtles, patches, links, globals), and finally generates a valid `.nlogo` file with a complete interface (sliders, buttons, plots, monitors) and BehaviorSpace experiments.

## Composition
`nlogo-multi-method` = `skill-creator` ( `target-to-anylogic` [ multimethod_cogsim_models ] -> `{{target}}.nlogo` )

## Prerequisites
- The `target-to-anylogic` skill must be available at `/home/ubuntu/skills/target-to-anylogic` for the decomposition step.

## Workflow

### Step 1: Decompose the Target
When the user requests a NetLogo model for a specific target, first use the `target-to-anylogic` decomposition script to analyze the target and extract its entities and dynamics.

```bash
python3 /home/ubuntu/skills/target-to-anylogic/scripts/decompose_target.py "Your target description here" --output /home/ubuntu/target_decomp.json
```

### Step 2: Create the NetLogo JSON Specification
Based on the decomposition, write a JSON specification file for the NetLogo model. The JSON must follow this structure:

```json
{
  "name": "Model Name",
  "description": "Description of the model (used in Info tab)",
  "version": "NetLogo 6.4.0",
  "world": {
    "min_pxcor": -25, "max_pxcor": 25,
    "min_pycor": -25, "max_pycor": 25,
    "patch_size": 10.0,
    "wrap_x": true, "wrap_y": true,
    "frame_rate": 30.0
  },
  "globals": ["global-var1", "global-var2"],
  "breeds": [
    {"plural": "sheep", "singular": "a-sheep"},
    {"plural": "wolves", "singular": "wolf"}
  ],
  "breed_vars": {
    "turtles": ["energy"],
    "sheep": [],
    "wolves": ["pack-size"]
  },
  "patch_vars": ["countdown", "fertility"],
  "procedures": {
    "setup": "clear-all\\ncreate-turtles 100 [\\n  setxy random-xcor random-ycor\\n]\\nreset-ticks",
    "go": "ask turtles [\\n  move\\n]\\ntick",
    "move": "rt random 50\\nlt random 50\\nfd 1"
  },
  "reporters": {
    "average-energy": "mean [energy] of turtles"
  },
  "sliders": [
    {"name": "initial-population", "min": 0, "max": 500, "value": 100, "step": 1, "units": "NIL"}
  ],
  "switches": [
    {"name": "show-energy?", "default_on": false}
  ],
  "choosers": [
    {"name": "model-version", "options": ["basic", "advanced"], "default_index": 0}
  ],
  "buttons": [
    {"name": "setup", "command": "setup", "forever": false},
    {"name": "go", "command": "go", "forever": true}
  ],
  "monitors": [
    {"name": "population", "reporter": "count turtles", "decimals": 0}
  ],
  "plots": [
    {
      "name": "Population",
      "x_label": "time",
      "y_label": "count",
      "x_min": 0, "x_max": 100, "y_min": 0, "y_max": 100,
      "autoplot_x": true, "autoplot_y": true,
      "pens": [
        {"name": "turtles", "color": -612749, "mode": 0, "code": "plot count turtles"}
      ]
    }
  ],
  "experiments": [
    {
      "name": "experiment-1",
      "repetitions": 10,
      "setup": "setup",
      "go": "go",
      "time_limit": 500,
      "metrics": ["count turtles"]
    }
  ]
}
```

### Step 3: Generate the .nlogo File
Run the generator script, passing the JSON specification file.

```bash
python3 /home/ubuntu/skills/nlogo-multi-method/scripts/generate_nlogo.py /home/ubuntu/model_spec.json --output /home/ubuntu/
```

### Step 4: Deliver the Model
Deliver the generated `.nlogo` file to the user, explaining how the P49 patterns were mapped to NetLogo agents (turtles/patches) and procedures.

## References
- `references/nlogo_format_spec.md`: Detailed specification of the 12 sections in a `.nlogo` file and the exact format for interface widgets.
