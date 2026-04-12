#!/usr/bin/env python3
"""
NetLogo .nlogo Generator
========================
Generates valid NetLogo .nlogo project files from a JSON model specification.

Usage:
    python generate_nlogo.py <spec.json> --output <output_dir>

The spec.json must contain:
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
    "setup": "clear-all\ncreate-turtles 100 [\n  setxy random-xcor random-ycor\n]\nreset-ticks",
    "go": "ask turtles [\n  move\n]\ntick",
    "move": "rt random 50\nlt random 50\nfd 1"
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
  "info": "## WHAT IS IT?\n\nDescription here.\n\n## HOW IT WORKS\n\nExplanation here."
}
"""

import json
import os
import sys
import argparse

SECTION_DELIMITER = "@#$#@#$#@"

# ─── Default Shapes ────────────────────────────────────────────────────────────

DEFAULT_TURTLE_SHAPES = """default
true
0
Polygon -7500403 true true 150 5 40 250 150 205 260 250

airplane
true
0
Polygon -7500403 true true 150 0 135 15 120 60 120 105 15 165 15 195 120 180 135 240 105 270 120 285 150 270 180 285 210 270 165 240 180 180 285 195 285 165 180 105 180 60 165 15

arrow
true
0
Polygon -7500403 true true 150 0 0 150 105 150 105 293 195 293 195 150 300 150

box
false
0
Polygon -7500403 true true 150 285 285 225 285 75 150 135
Polygon -7500403 true true 150 135 15 75 150 15 285 75
Polygon -7500403 true true 15 75 15 225 150 285 150 135
Line -16777216 false 150 285 150 135
Line -16777216 false 150 135 15 75
Line -16777216 false 150 135 285 75

circle
false
0
Circle -7500403 true true 0 0 300

dot
false
0
Circle -7500403 true true 90 90 120

face happy
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 255 90 239 62 213 47 191 67 179 90 203 109 218 150 225 192 218 210 203 227 181 251 194 236 217 212 240

face neutral
false
0
Circle -7500403 true true 8 7 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Rectangle -16777216 true false 60 195 240 225

face sad
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 168 90 184 62 210 47 232 67 244 90 220 109 205 150 198 192 205 210 220 227 242 251 229 236 206 212 183

house
false
0
Rectangle -7500403 true true 45 120 255 285
Rectangle -16777216 true false 120 210 180 285
Polygon -7500403 true true 15 120 150 15 285 120
Line -16777216 false 30 120 270 120

line
true
0
Line -7500403 true 150 0 150 300

line half
true
0
Line -7500403 true 150 0 150 150

pentagon
false
0
Polygon -7500403 true true 150 15 15 120 60 285 240 285 285 120

person
false
0
Circle -7500403 true true 110 5 80
Polygon -7500403 true true 105 90 120 195 90 285 105 300 135 300 150 225 165 300 195 300 210 285 180 195 195 90
Rectangle -7500403 true true 127 79 172 94
Polygon -7500403 true true 195 90 240 150 225 180 165 105
Polygon -7500403 true true 105 90 60 150 75 180 135 105

plant
false
0
Rectangle -7500403 true true 135 90 165 300
Polygon -7500403 true true 135 255 90 210 45 195 75 255 135 285
Polygon -7500403 true true 165 255 210 210 255 195 225 255 165 285
Polygon -7500403 true true 135 180 90 135 45 120 75 180 135 210
Polygon -7500403 true true 165 180 165 210 225 180 255 120 210 135
Polygon -7500403 true true 135 105 90 60 45 45 75 105 135 135
Polygon -7500403 true true 165 105 165 135 225 105 255 45 210 60
Polygon -7500403 true true 135 90 120 45 150 15 180 45 165 90

sheep
false
15
Circle -1 true true 203 65 88
Circle -1 true true 70 65 162
Circle -1 true true 150 105 120
Polygon -7500403 true false 218 120 240 165 255 165 278 120
Circle -7500403 true false 214 72 67
Rectangle -1 true true 164 223 179 298
Polygon -1 true true 45 285 30 285 30 240 15 195 45 210
Circle -1 true true 3 83 150
Rectangle -1 true true 65 221 80 296
Polygon -1 true true 195 285 210 285 210 240 240 210 195 210
Polygon -7500403 true false 276 85 285 105 302 99 294 83
Polygon -7500403 true false 219 85 210 105 193 99 201 83

square
false
0
Rectangle -7500403 true true 30 30 270 270

star
false
0
Polygon -7500403 true true 151 1 185 108 298 108 207 175 242 282 151 216 59 282 94 175 3 108 116 108

target
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240
Circle -7500403 true true 60 60 180
Circle -16777216 true false 90 90 120
Circle -7500403 true true 120 120 60

tree
false
0
Circle -7500403 true true 118 3 94
Rectangle -6459832 true false 120 195 180 300
Circle -7500403 true true 65 21 108
Circle -7500403 true true 116 41 127
Circle -7500403 true true 45 90 120
Circle -7500403 true true 104 74 152

triangle
false
0
Polygon -7500403 true true 150 30 15 255 285 255

truck
false
0
Rectangle -7500403 true true 4 45 195 187
Polygon -7500403 true true 296 193 296 150 259 134 244 104 208 104 207 194
Rectangle -1 true false 195 60 195 105
Polygon -16777216 true false 238 112 252 141 219 141 218 112
Circle -16777216 true false 234 174 42
Rectangle -7500403 true true 181 185 214 194
Circle -16777216 true false 144 174 42
Circle -16777216 true false 24 174 42
Circle -7500403 false true 24 174 42
Circle -7500403 false true 144 174 42
Circle -7500403 false true 234 174 42

turtle
true
0
Polygon -10899396 true false 215 204 240 233 246 254 228 266 215 252 193 210
Polygon -10899396 true false 195 90 225 75 245 75 260 89 269 108 261 124 240 105 225 105 210 105
Polygon -10899396 true false 105 90 75 75 55 75 40 89 31 108 39 124 60 105 75 105 90 105
Polygon -10899396 true false 132 85 134 64 107 51 108 17 150 2 192 18 192 52 169 65 172 87
Polygon -10899396 true false 85 204 60 233 54 254 72 266 85 252 107 210
Polygon -7500403 true true 119 75 179 75 209 101 224 135 220 225 175 261 128 261 81 224 74 135 88 99

wheel
false
0
Circle -7500403 true true 3 3 294
Circle -16777216 true false 30 30 240
Line -7500403 true 150 285 150 15
Line -7500403 true 15 150 285 150
Circle -7500403 true true 120 120 60
Line -7500403 true 216 40 79 269
Line -7500403 true 40 84 269 221
Line -7500403 true 40 216 269 79
Line -7500403 true 84 40 221 269

wolf
false
0
Polygon -16777216 true false 253 133 245 131 245 133
Polygon -7500403 true true 2 194 13 197 30 191 38 193 38 205 20 226 20 257 27 265 38 266 40 260 31 253 31 230 60 206 68 198 75 209 66 228 65 243 82 261 84 268 100 267 103 261 77 239 79 231 100 207 98 196 119 201 143 202 160 195 166 210 172 213 173 238 167 251 160 248 154 265 169 264 178 247 186 240 198 260 200 271 217 271 219 262 207 258 195 230 192 198 210 184 227 164 242 144 259 145 284 151 277 141 293 140 299 134 297 127 273 119 270 105
Polygon -7500403 true true -1 195 14 180 36 166 40 153 53 140 82 131 134 133 159 126 188 115 227 95 241 62 259 38 266 25 282 19 300 17 277 25 257 37 241 63 225 96 193 116 164 126 142 133 110 135 80 134 58 141 51 150 39 159 18 173 2 186
Polygon -7500403 true true 0 196 -1 -1 298 -1 300 198 297 190 285 152 263 109 248 65 257 26 282 19 300 17 277 25 257 37 242 62 226 96 193 116 164 126 141 133 110 135 80 134 58 141 51 150 39 159 18 173 2 186
Polygon -16777216 true false 274 117 262 104 242 97 222 98 210 107 204 117 202 131 205 142 218 152 234 152 249 147 260 137
Line -16777216 false 220 101 210 112
Line -16777216 false 220 101 228 112
Polygon -16777216 true false 164 257 144 258 132 262 124 270 124 280 134 283 148 281 164 270
Polygon -1 true false 280 116 265 103 250 100 235 101 225 110 220 120 220 130 225 140 235 147 250 147 265 142 275 130

x
false
0
Polygon -7500403 true true 270 75 225 30 30 225 75 270
Polygon -7500403 true true 30 75 75 30 270 225 225 270"""

DEFAULT_LINK_SHAPES = """default
0.0
-0.2 0 0.0 1.0
0.0 1 1.0 0.0
0.2 0 0.0 1.0
link direction
true
0
Line -7500403 true 150 150 90 180
Line -7500403 true 150 150 210 180"""


# ─── Color Constants ───────────────────────────────────────────────────────────

COLORS = {
    "red": -2674135,
    "blue": -13345367,
    "green": -10899396,
    "yellow": -1184463,
    "orange": -955883,
    "violet": -8630108,
    "brown": -6459832,
    "cyan": -11221820,
    "magenta": -5825686,
    "pink": -2064490,
    "gray": -7500403,
    "black": -16777216,
    "white": -1,
    "lime": -13840069,
    "turquoise": -14835848,
    "sky": -13791810,
}


class NLogoGenerator:
    def __init__(self, spec):
        self.spec = spec
        self.widget_x = 5
        self.widget_y = 10

    def generate(self):
        """Generate the complete .nlogo file content as a string."""
        sections = [
            self._code_section(),         # 0: Code
            self._interface_section(),     # 1: Interface
            self._info_section(),          # 2: Info
            DEFAULT_TURTLE_SHAPES,         # 3: Turtle shapes
            self._version_section(),       # 4: Version
            self._preview_section(),       # 5: Preview commands
            self._sd_section(),            # 6: System Dynamics
            self._behaviorspace_section(), # 7: BehaviorSpace
            "",                            # 8: HubNet
            DEFAULT_LINK_SHAPES,           # 9: Link shapes
            self._settings_section(),      # 10: Model settings
            "",                            # 11: DeltaTick
        ]
        return ("\n" + SECTION_DELIMITER + "\n").join(sections) + "\n"

    # ─── Section 0: Code ───────────────────────────────────────────────────

    def _code_section(self):
        lines = []

        # Header comment
        name = self.spec.get("name", "Generated Model")
        lines.append(f"; {name}")
        lines.append(f"; Generated by nlogo-multi-method skill")
        lines.append("")

        # Extensions
        extensions = self.spec.get("extensions", [])
        if extensions:
            lines.append(f"extensions [{' '.join(extensions)}]")
            lines.append("")

        # Globals
        globals_list = self.spec.get("globals", [])
        if globals_list:
            lines.append(f"globals [{' '.join(globals_list)}]")
            lines.append("")

        # Breeds
        breeds = self.spec.get("breeds", [])
        for b in breeds:
            lines.append(f"breed [{b['plural']} {b['singular']}]")
        if breeds:
            lines.append("")

        # Breed variables
        breed_vars = self.spec.get("breed_vars", {})
        for owner, vars_list in breed_vars.items():
            if vars_list:
                lines.append(f"{owner}-own [{' '.join(vars_list)}]")
        if breed_vars:
            lines.append("")

        # Patch variables
        patch_vars = self.spec.get("patch_vars", [])
        if patch_vars:
            lines.append(f"patches-own [{' '.join(patch_vars)}]")
            lines.append("")

        # Procedures
        procedures = self.spec.get("procedures", {})
        for proc_name, proc_body in procedures.items():
            lines.append(f"to {proc_name}")
            for body_line in proc_body.split("\n"):
                lines.append(f"  {body_line}")
            lines.append("end")
            lines.append("")

        # Reporters
        reporters = self.spec.get("reporters", {})
        for rep_name, rep_body in reporters.items():
            lines.append(f"to-report {rep_name}")
            lines.append(f"  report {rep_body}")
            lines.append("end")
            lines.append("")

        return "\n".join(lines)

    # ─── Section 1: Interface ──────────────────────────────────────────────

    def _interface_section(self):
        widgets = []

        # Graphics window
        world = self.spec.get("world", {})
        widgets.append(self._graphics_window(world))

        # Layout tracking
        col1_x = 5
        col2_x = 200
        y_pos = 10

        # Sliders
        for s in self.spec.get("sliders", []):
            widgets.append(self._slider(s, col1_x, y_pos))
            y_pos += 40

        # Switches
        for sw in self.spec.get("switches", []):
            widgets.append(self._switch(sw, col1_x, y_pos))
            y_pos += 40

        # Choosers
        for ch in self.spec.get("choosers", []):
            widgets.append(self._chooser(ch, col1_x, y_pos))
            y_pos += 50

        # Buttons
        btn_x = col1_x
        btn_y = y_pos
        for btn in self.spec.get("buttons", []):
            widgets.append(self._button(btn, btn_x, btn_y))
            btn_x += 80
        if self.spec.get("buttons"):
            y_pos = btn_y + 40

        # Monitors
        mon_x = col1_x
        for mon in self.spec.get("monitors", []):
            widgets.append(self._monitor(mon, mon_x, y_pos))
            mon_x += 80
        if self.spec.get("monitors"):
            y_pos += 55

        # Plots
        for plot in self.spec.get("plots", []):
            widgets.append(self._plot(plot, col1_x, y_pos))
            y_pos += 180

        return "\n\n".join(widgets)

    def _graphics_window(self, world):
        min_px = world.get("min_pxcor", -16)
        max_px = world.get("max_pxcor", 16)
        min_py = world.get("min_pycor", -16)
        max_py = world.get("max_pycor", 16)
        patch_size = world.get("patch_size", 13.0)
        wrap_x = 1 if world.get("wrap_x", True) else 0
        wrap_y = 1 if world.get("wrap_y", True) else 0
        frame_rate = world.get("frame_rate", 30.0)

        width = int((max_px - min_px + 1) * patch_size) + 10
        height = int((max_py - min_py + 1) * patch_size) + 10
        left = 400
        top = 10
        right = left + width
        bottom = top + height

        return f"""GRAPHICS-WINDOW
{left}
{top}
{right}
{bottom}
-1
-1
{patch_size}
1
14
1
1
1
0
{wrap_x}
{wrap_y}
1
{min_px}
{max_px}
{min_py}
{max_py}
1
1
1
ticks
{frame_rate}"""

    def _slider(self, s, x, y):
        name = s["name"]
        return f"""SLIDER
{x}
{y}
{x + 190}
{y + 33}
{name}
{name}
{s.get('min', 0)}
{s.get('max', 100)}
{s.get('value', 50)}
{s.get('step', 1)}
1
{s.get('units', 'NIL')}
HORIZONTAL"""

    def _switch(self, sw, x, y):
        name = sw["name"]
        val = 0 if sw.get("default_on", False) else 1
        return f"""SWITCH
{x}
{y}
{x + 140}
{y + 33}
{name}
{name}
{val}
1
-1000"""

    def _chooser(self, ch, x, y):
        name = ch["name"]
        options = " ".join(f'"{o}"' for o in ch.get("options", []))
        idx = ch.get("default_index", 0)
        return f"""CHOOSER
{x}
{y}
{x + 200}
{y + 45}
{name}
{name}
{options}
{idx}"""

    def _button(self, btn, x, y):
        name = btn["name"]
        cmd = btn.get("command", name)
        forever = "T" if btn.get("forever", False) else "NIL"
        disable = 0 if btn.get("forever", False) else 1
        return f"""BUTTON
{x}
{y}
{x + 70}
{y + 33}
{name}
{cmd}
{forever}
1
T
OBSERVER
NIL
NIL
NIL
NIL
{disable}"""

    def _monitor(self, mon, x, y):
        return f"""MONITOR
{x}
{y}
{x + 70}
{y + 45}
{mon['name']}
{mon['reporter']}
{mon.get('decimals', 3)}
1
11"""

    def _plot(self, p, x, y):
        lines = []
        lines.append(f"""PLOT
{x}
{y}
{x + 350}
{y + 170}
{p['name']}
{p.get('x_label', 'time')}
{p.get('y_label', 'count')}
{p.get('x_min', 0.0)}
{p.get('x_max', 100.0)}
{p.get('y_min', 0.0)}
{p.get('y_max', 100.0)}
{str(p.get('autoplot_x', True)).lower()}
{str(p.get('autoplot_y', True)).lower()}
"" ""
PENS""")
        for pen in p.get("pens", []):
            color = pen.get("color", -612749)
            if isinstance(color, str):
                color = COLORS.get(color, -7500403)
            mode = pen.get("mode", 0)
            code = pen.get("code", "")
            lines.append(f'"{pen["name"]}" 1.0 {mode} {color} true "" "{code}"')
        return "\n".join(lines)

    # ─── Section 2: Info ───────────────────────────────────────────────────

    def _info_section(self):
        info = self.spec.get("info", "")
        if not info:
            name = self.spec.get("name", "Generated Model")
            desc = self.spec.get("description", "A simulation model.")
            info = f"""## WHAT IS IT?

{desc}

## HOW IT WORKS

This model was generated by the nlogo-multi-method skill from a target system description.

## HOW TO USE IT

1. Click **setup** to initialize the model.
2. Click **go** to run the simulation.
3. Adjust sliders and switches to explore different parameters.

## THINGS TO NOTICE

Observe how the agents interact and how the system-level metrics change over time.

## THINGS TO TRY

Experiment with different parameter values to see how they affect the model dynamics.

## CREDITS AND REFERENCES

Generated by nlogo-multi-method skill.
Model: {name}
"""
        return info

    # ─── Sections 3-11 ─────────────────────────────────────────────────────

    def _version_section(self):
        return self.spec.get("version", "NetLogo 6.4.0")

    def _preview_section(self):
        preview = self.spec.get("preview_commands", "")
        if not preview:
            preview = "setup\nrepeat 50 [ go ]"
        return preview

    def _sd_section(self):
        return self.spec.get("system_dynamics", "")

    def _behaviorspace_section(self):
        experiments = self.spec.get("experiments", [])
        if not experiments:
            return ""
        lines = ["<experiments>"]
        for exp in experiments:
            lines.append(f'  <experiment name="{exp.get("name", "experiment")}" repetitions="{exp.get("repetitions", 1)}" runMetricsEveryStep="true">')
            lines.append(f"    <setup>{exp.get('setup', 'setup')}</setup>")
            lines.append(f"    <go>{exp.get('go', 'go')}</go>")
            if exp.get("time_limit"):
                lines.append(f'    <timeLimit steps="{exp["time_limit"]}"/>')
            for metric in exp.get("metrics", []):
                lines.append(f"    <metric>{metric}</metric>")
            lines.append("  </experiment>")
        lines.append("</experiments>")
        return "\n".join(lines)

    def _settings_section(self):
        return "1"


def main():
    parser = argparse.ArgumentParser(description="Generate NetLogo .nlogo project files from JSON spec")
    parser.add_argument("spec", help="Path to JSON model specification file")
    parser.add_argument("--output", "-o", default=".", help="Output directory")
    args = parser.parse_args()

    with open(args.spec) as f:
        spec = json.load(f)

    os.makedirs(args.output, exist_ok=True)

    gen = NLogoGenerator(spec)
    content = gen.generate()

    name = spec.get("name", "GeneratedModel")
    safe_name = name.replace(" ", "_").replace("/", "_")
    output_path = os.path.join(args.output, f"{safe_name}.nlogo")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Generated: {output_path}")
    print(f"  Globals: {len(spec.get('globals', []))}")
    print(f"  Breeds: {len(spec.get('breeds', []))}")
    print(f"  Procedures: {len(spec.get('procedures', {}))}")
    print(f"  Reporters: {len(spec.get('reporters', {}))}")
    print(f"  Sliders: {len(spec.get('sliders', []))}")
    print(f"  Buttons: {len(spec.get('buttons', []))}")
    print(f"  Plots: {len(spec.get('plots', []))}")
    print(f"  Monitors: {len(spec.get('monitors', []))}")


if __name__ == "__main__":
    main()
