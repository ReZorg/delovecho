# Plan 9 C IDE Guide

## Table of Contents

1. [IDE Options](#ide-options)
2. [acme Editor (Native Plan 9 IDE)](#acme-editor)
3. [sam Editor](#sam-editor)
4. [VS Code Integration](#vs-code-integration)
5. [Plan 9 C Compiler Workflow](#plan-9-c-compiler-workflow)
6. [Debugging and Profiling](#debugging-and-profiling)

## IDE Options

The devcontainer provides multiple IDE options for Plan 9 C development:

| IDE | Type | Best For | Launch |
|-----|------|----------|--------|
| **acme** | plan9port native | Authentic Plan 9 experience, mouse-driven | `9 acme /workspace/src` |
| **sam** | plan9port native | Structural regex editing | `9 sam file.c` |
| **VS Code** | Host editor | Modern IDE with extensions | Automatic via devcontainer |
| **vim/neovim** | Terminal | Quick edits, SSH sessions | `vim` / `nvim` |

## acme Editor

acme is the native Plan 9 programmer's IDE, available via plan9port. It provides a mouse-driven, text-command interface.

### Starting acme

```sh
# Via plan9port
9 acme /workspace/src
```

### acme Mouse Commands

| Button | Action |
|--------|--------|
| **Left (B1)** | Select text |
| **Middle (B2)** | Execute command |
| **Right (B3)** | Look/search/open file |
| **B1+B2** | Cut (snarf) |
| **B1+B3** | Paste |

### Built-in Commands

Type these in any acme tag or window and middle-click to execute:

| Command | Action |
|---------|--------|
| `Put` | Save file |
| `Get` | Reload file |
| `Undo` | Undo last change |
| `Redo` | Redo last undo |
| `Del` | Close window |
| `New` | New window |
| `Edit ,d` | Delete all text |
| `Edit ,s/old/new/g` | Find and replace |
| `Look pattern` | Search for pattern |

### Compiling from acme

In the window tag, type and middle-click:
```
9c file.c
```

To compile and link:
```
9c file.c && 9l -o file.out file.o
```

## sam Editor

sam is Plan 9's structural regular expression editor, ideal for complex text transformations.

### Starting sam

```sh
9 sam file.c
# Or with multiple files
9 sam *.c
```

### sam Commands

| Command | Action |
|---------|--------|
| `,` | Select entire file |
| `x/pattern/` | For each match of pattern |
| `g/pattern/` | If selection contains pattern |
| `v/pattern/` | If selection does not contain pattern |
| `c/text/` | Change selection to text |
| `a/text/` | Append text after selection |
| `i/text/` | Insert text before selection |
| `d` | Delete selection |
| `p` | Print selection |
| `w` | Write file |

### Structural Regex Examples

```
# Replace all occurrences of "foo" with "bar"
,x/foo/ c/bar/

# Delete all blank lines
,x/\n\n+/ c/\n/

# Add "static " before every function definition
,x/^[a-z].*\(/ i/static /
```

## VS Code Integration

The devcontainer configures VS Code with Plan 9 C-aware settings.

### File Associations

| Extension | Language | Purpose |
|-----------|----------|---------|
| `.c` | C | Plan 9 C source files |
| `.h` | C | Header files |
| `.o` | Object | Compiled object files |
| `.out` | Executable | Linked executables |
| `mkfile` | Makefile | Plan 9 build files |
| `mkconfig` | Makefile | Build configuration |

### Build Tasks

Create `.vscode/tasks.json` in your workspace:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Plan 9: Compile",
            "type": "shell",
            "command": "plan9-build compile ${file}",
            "group": "build",
            "problemMatcher": {
                "pattern": {
                    "regexp": "^(.+):(\\d+): (.+)$",
                    "file": 1,
                    "line": 2,
                    "message": 3
                }
            }
        },
        {
            "label": "Plan 9: Run",
            "type": "shell",
            "command": "plan9-build run ${file}",
            "group": "test"
        },
        {
            "label": "Grid: Start",
            "type": "shell",
            "command": "plan9-grid start"
        },
        {
            "label": "Grid: Status",
            "type": "shell",
            "command": "plan9-grid status"
        }
    ]
}
```

### Keyboard Shortcuts

Add to `.vscode/keybindings.json`:

```json
[
    { "key": "ctrl+shift+b", "command": "workbench.action.tasks.runTask", "args": "Plan 9: Compile" },
    { "key": "ctrl+shift+r", "command": "workbench.action.tasks.runTask", "args": "Plan 9: Run" }
]
```

## Plan 9 C Compiler Workflow

### Using plan9port Compilers

```bash
# Compile a single file (via plan9port wrapper)
9c hello.c                    # produces hello.o
9l -o hello.out hello.o       # link to executable

# Or use the plan9-build CLI
plan9-build compile src/hello.c
plan9-build run src/hello.c
```

### Plan 9 C Differences from ANSI C

| Feature | Plan 9 C | ANSI C |
|---------|----------|--------|
| Headers | `#include <u.h>`, `#include <libc.h>` | `#include <stdio.h>` |
| Print | `print("hello\n")` | `printf("hello\n")` |
| Main | `void main(void)` | `int main(void)` |
| Exit | `exits(0)` | `exit(0)` |
| String format | `smprint(...)` | `sprintf(...)` |
| Memory | `mallocz(n, 1)` | `calloc(1, n)` |

### Build with mk

Create a `mkfile` for your project:

```mk
</$PLAN9/src/mkmk.proto

TARG=hello
OFILES=\
    hello.$O\

</usr/local/plan9/src/mkone
```

## Debugging and Profiling

### Using acid (Plan 9 debugger)

Inside a native Plan 9 environment:
```sh
# Start acid on a binary
acid hello.out

# Set breakpoint
bpset(main)

# Run
cont()

# Print variable
*varname
```

### Host-Side Debugging

For plan9port programs, use GDB:

```bash
# Compile with debug symbols
9c -g hello.c
9l -o hello.out hello.o

# Debug with GDB
gdb ./hello.out
```

### Performance Profiling

```bash
# Profile CPU usage (Linux host)
perf stat ./hello.out

# Memory analysis
valgrind --tool=memcheck ./hello.out
```
