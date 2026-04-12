# Limbo IDE Guide

## Table of Contents

1. [IDE Options](#ide-options)
2. [Acme Editor (Native Inferno IDE)](#acme-editor)
3. [VS Code Integration](#vs-code-integration)
4. [Limbo Compiler Workflow](#limbo-compiler-workflow)
5. [Debugging and Profiling](#debugging-and-profiling)

## IDE Options

The devcontainer provides multiple IDE options for Limbo development:

| IDE | Type | Best For | Launch |
|-----|------|----------|--------|
| **Acme** | Native Inferno | Authentic Plan 9/Inferno experience | `emu -c1 "wm/wm; acme"` |
| **VS Code** | Host editor | Modern IDE with extensions | Automatic via devcontainer |
| **Vim/Neovim** | Terminal | Quick edits, SSH sessions | `vim` / `nvim` |
| **wm/edit** | Native Inferno | Simple text editing inside Inferno | `emu -c1 "wm/wm; wm/edit file.b"` |

## Acme Editor

Acme is the native Inferno IDE, inherited from Plan 9. It provides a mouse-driven, text-command interface.

### Starting Acme

```sh
# Inside Inferno (via emu)
wm/wm
acme /workspace/src
```

### Acme Mouse Commands

| Button | Action |
|--------|--------|
| **Left (B1)** | Select text |
| **Middle (B2)** | Execute command |
| **Right (B3)** | Look/search/open file |
| **B1+B2** | Cut (snarf) |
| **B1+B3** | Paste |

### Built-in Commands

Type these in any Acme tag or window and middle-click to execute:

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
| `Limbo file.b` | Compile Limbo source |
| `Look pattern` | Search for pattern |

### Compiling from Acme

In the window tag, type and middle-click:
```
limbo -g file.b
```

To compile and run:
```
limbo -g file.b; emu file.dis
```

## VS Code Integration

The devcontainer configures VS Code with Limbo-aware settings.

### File Associations

| Extension | Language | Purpose |
|-----------|----------|---------|
| `.b` | Limbo | Limbo source files |
| `.m` | Limbo module | Module interface definitions |
| `.dis` | Dis bytecode | Compiled Dis virtual machine code |
| `.sbl` | Dis symbols | Debug symbol files |
| `mkfile` | Makefile | Inferno build files |

### Build Tasks

Create `.vscode/tasks.json` in your workspace:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Limbo: Compile",
            "type": "shell",
            "command": "limbo-build compile ${file}",
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
            "label": "Limbo: Run",
            "type": "shell",
            "command": "limbo-build run ${file}",
            "group": "test"
        },
        {
            "label": "Limbo: Type Check",
            "type": "shell",
            "command": "limbo-build check ${file}",
            "group": "build"
        },
        {
            "label": "Cluster: Start",
            "type": "shell",
            "command": "inferno-cluster start"
        },
        {
            "label": "Cluster: Status",
            "type": "shell",
            "command": "inferno-cluster status"
        }
    ]
}
```

### Keyboard Shortcuts

Add to `.vscode/keybindings.json`:

```json
[
    { "key": "ctrl+shift+b", "command": "workbench.action.tasks.runTask", "args": "Limbo: Compile" },
    { "key": "ctrl+shift+r", "command": "workbench.action.tasks.runTask", "args": "Limbo: Run" },
    { "key": "ctrl+shift+t", "command": "workbench.action.tasks.runTask", "args": "Limbo: Type Check" }
]
```

## Limbo Compiler Workflow

### Basic Compilation

```bash
# Compile a single file
limbo -g -o output.dis source.b

# Compile with debug symbols
limbo -g source.b          # produces source.dis and source.sbl

# Type-check only (no code generation)
limbo -w source.b

# Compile with include path
limbo -I /workspace/src/module -g source.b
```

### Compiler Flags

| Flag | Purpose |
|------|---------|
| `-g` | Generate debug symbols (.sbl) |
| `-w` | Warnings only, no code generation |
| `-o file` | Specify output file |
| `-I dir` | Add include directory |
| `-e` | Generate code for each module |
| `-a` | Generate assembly listing |
| `-S` | Generate symbol table |

### Build with mk

Create a `mkfile` for your project:

```mk
</$INFERNO_ROOT/mkconfig

TARG=myapp.dis
MODULES=\
    src/main.b\
    src/util.b\

SYSMODULES=\
    sys.m\
    draw.m\

</opt/mkfiles/mkdis
```

## Debugging and Profiling

### Stack Traces

```sh
# Inside Inferno shell
stack <pid>
```

### Debug Output

Use `sys->print()` for debug output:

```limbo
sys->print("debug: value = %d\n", value);
```

### Memory Profiling

```sh
# Inside Inferno
mprof <command>
```

### Performance Profiling

```sh
# Profile CPU usage
prof -e <command>

# Profile with sampling
prof -s 100 <command>
```

### Host-Side Debugging

For the C kernel components, use GDB:

```bash
# Attach to emu process
gdb -p $(pgrep emu)

# Or start under GDB
gdb --args emu -c1 -r /usr/inferno
```

For memory analysis:

```bash
valgrind --tool=memcheck emu -c1 -r /usr/inferno "myapp.dis"
```
