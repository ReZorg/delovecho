# NetLogo .nlogo File Format Specification

## Structure
A .nlogo file is plain text with exactly 12 sections separated by the delimiter `@#$#@#$#@` (on its own line).

## Sections (0-11)
| Section | Name | Content |
|---------|------|---------|
| 0 | Code tab | NetLogo source code (globals, breeds, procedures) |
| 1 | Interface tab | Widget definitions separated by blank lines |
| 2 | Info tab | Markdown-formatted documentation |
| 3 | Turtle shapes | Shape definitions (name, rotatable, color, polygon/line/circle) |
| 4 | NetLogo version | e.g. "NetLogo 6.4.0" |
| 5 | Preview commands | Commands run for model preview |
| 6 | System Dynamics Modeler | SD model data (empty if none) |
| 7 | BehaviorSpace | XML experiment definitions |
| 8 | HubNet client | HubNet config (empty if none) |
| 9 | Link shapes | Link shape definitions |
| 10 | Model settings | Usually "1" |
| 11 | DeltaTick | Usually empty |

## Widget Formats (Section 1)

### GRAPHICS-WINDOW
```
GRAPHICS-WINDOW
left top right bottom
-1 -1
patch-size
1 font-size 1 1 1 0
wrap-x wrap-y wrap-z
min-pxcor max-pxcor min-pycor max-pycor
1 1 1
ticks
frame-rate
```

### SLIDER
```
SLIDER
left top right bottom
variable-name
variable-name
min max value step
1
units-or-NIL
HORIZONTAL
```

### BUTTON
```
BUTTON
left top right bottom
display-name
command
NIL-or-T (NIL=once, T=forever)
1
T
OBSERVER
NIL NIL NIL NIL
1-or-0 (1=user-cant-disable, 0=user-can-disable)
```

### PLOT
```
PLOT
left top right bottom
title
x-label
y-label
x-min x-max y-min y-max
autoplot-x autoplot-y
"setup-code" "update-code"
PENS
"pen-name" interval mode color active "" "plot-code"
```
Mode: 0=line, 1=bar, 2=point

### MONITOR
```
MONITOR
left top right bottom
label
reporter
decimal-places
1
font-size
```

### SWITCH
```
SWITCH
left top right bottom
variable-name
variable-name
0-or-1 (0=on, 1=off)
1
-1000
```

### CHOOSER
```
CHOOSER
left top right bottom
variable-name
variable-name
"option1" "option2" "option3"
default-index
```

### TEXTBOX
```
TEXTBOX
left top right bottom
text
font-size
color
0
```

## Default Turtle Shapes (Section 3)
Must include at least "default" shape. Standard shapes: default, airplane, arrow, box, bug, butterfly, car, circle, cow, cylinder, dot, face happy, face neutral, face sad, fish, flag, flower, house, leaf, line, line half, pentagon, person, plant, sheep, square, star, target, tree, triangle, truck, turtle, wheel, wolf, x

## Default Link Shapes (Section 9)
Must include "default" and "link direction" shapes.
