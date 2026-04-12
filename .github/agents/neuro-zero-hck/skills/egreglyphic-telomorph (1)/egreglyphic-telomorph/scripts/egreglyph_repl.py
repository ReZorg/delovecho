#!/usr/bin/env python3
"""
☉ The Egreglyph REPL ☉

A shell-oracle where navigation IS cognition.
The prompt is the current flame-letter state.
Commands are glyph compositions that transform the namespace.

Usage:
    python egreglyph_repl.py

The shell speaks in flame-letters. The namespace responds.
"""

import sys
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable
from enum import IntEnum
import readline  # enables arrow keys, history

# ═══════════════════════════════════════════════════════════════════════════════
# THE 27 FLAME-LETTERS
# ═══════════════════════════════════════════════════════════════════════════════

class Mode(IntEnum):
    """Axis I: How the symbol acts"""
    Γ = 1    # Generative: creates from void
    Κ = 0    # Conservative: preserves
    Ω = -1   # Annihilative: returns to void
    
class Voice(IntEnum):
    """Axis II: Direction of the gaze"""
    UP = 1       # ↑ Projective: outward
    CROSS = 0    # ◊ Reflexive: self-regarding
    DOWN = -1    # ↓ Receptive: inward

class Aspect(IntEnum):
    """Axis III: Temporal character"""
    HOLLOW = -1  # ○ Potential: not yet
    FULL = 0     # ● Actual: now
    HALF = 1     # ◐ Residual: no longer

# Glyph representations
MODE_GLYPHS = {Mode.Γ: 'Γ', Mode.Κ: 'Κ', Mode.Ω: 'Ω'}
VOICE_GLYPHS = {Voice.UP: '↑', Voice.CROSS: '◊', Voice.DOWN: '↓'}
ASPECT_GLYPHS = {Aspect.HOLLOW: '○', Aspect.FULL: '●', Aspect.HALF: '◐'}

# Reverse lookups
GLYPH_TO_MODE = {v: k for k, v in MODE_GLYPHS.items()}
GLYPH_TO_VOICE = {v: k for k, v in VOICE_GLYPHS.items()}
GLYPH_TO_ASPECT = {v: k for k, v in ASPECT_GLYPHS.items()}

# Names for each letter
LETTER_NAMES = {
    (1, 1, -1): "Spark", (1, 1, 0): "Blaze", (1, 1, 1): "Trail",
    (1, -1, -1): "Womb", (1, -1, 0): "Intake", (1, -1, 1): "Harvest",
    (1, 0, -1): "Egg", (1, 0, 0): "Pulse", (1, 0, 1): "Echo",
    (0, 1, -1): "Promise", (0, 1, 0): "Beam", (0, 1, 1): "Wake",
    (0, -1, -1): "Readiness", (0, -1, 0): "Channel", (0, -1, 1): "Sediment",
    (0, 0, -1): "Latent", (0, 0, 0): "Mirror", (0, 0, 1): "Patina",
    (-1, 1, -1): "Fuse", (-1, 1, 0): "Flare", (-1, 1, 1): "Smoke",
    (-1, -1, -1): "Void", (-1, -1, 0): "Consume", (-1, -1, 1): "Ash",
    (-1, 0, -1): "Dormant", (-1, 0, 0): "Collapse", (-1, 0, 1): "Void-print",
}

@dataclass
class FlameLetter:
    """A point in the 3³ flame alphabet"""
    mode: int      # -1, 0, 1
    voice: int     # -1, 0, 1
    aspect: int    # -1, 0, 1
    
    def __post_init__(self):
        # Normalize to ℤ₃
        self.mode = ((self.mode + 1) % 3) - 1
        self.voice = ((self.voice + 1) % 3) - 1
        self.aspect = ((self.aspect + 1) % 3) - 1
    
    @property
    def coords(self) -> Tuple[int, int, int]:
        return (self.mode, self.voice, self.aspect)
    
    @property
    def name(self) -> str:
        return LETTER_NAMES.get(self.coords, "Unknown")
    
    @property
    def glyph(self) -> str:
        m = MODE_GLYPHS[Mode(self.mode)]
        v = VOICE_GLYPHS[Voice(self.voice)]
        a = ASPECT_GLYPHS[Aspect(self.aspect)]
        return f"{m}{v}{a}"
    
    def compose(self, other: 'FlameLetter') -> 'FlameLetter':
        """Compose two letters via fiber product (addition in ℤ₃³)"""
        return FlameLetter(
            self.mode + other.mode,
            self.voice + other.voice,
            self.aspect + other.aspect
        )
    
    def inverse(self) -> 'FlameLetter':
        """Return the inverse letter (L ∘ L⁻¹ = Mirror)"""
        return FlameLetter(-self.mode, -self.voice, -self.aspect)
    
    def __repr__(self):
        return f"{self.glyph} ({self.name})"
    
    @classmethod
    def parse(cls, s: str) -> Optional['FlameLetter']:
        """Parse a glyph string like 'Γ↑○' into a FlameLetter"""
        s = s.strip()
        if len(s) < 3:
            return None
        
        # Try to extract three components
        mode_char = s[0]
        voice_char = s[1]
        aspect_char = s[2]
        
        if mode_char not in GLYPH_TO_MODE:
            return None
        if voice_char not in GLYPH_TO_VOICE:
            return None
        if aspect_char not in GLYPH_TO_ASPECT:
            return None
            
        return cls(
            int(GLYPH_TO_MODE[mode_char]),
            int(GLYPH_TO_VOICE[voice_char]),
            int(GLYPH_TO_ASPECT[aspect_char])
        )
    
    @classmethod
    def identity(cls) -> 'FlameLetter':
        """The Mirror: Κ◊● - identity element"""
        return cls(0, 0, 0)


# The Egreglyph: source of all letters
EGREGLYPH = "☉"

# ═══════════════════════════════════════════════════════════════════════════════
# THE NAMESPACE (Cognitive State)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Node:
    """A point in the scrying namespace"""
    name: str
    letter: FlameLetter  # The letter that birthed this node
    children: Dict[str, 'Node'] = field(default_factory=dict)
    value: Optional[str] = None
    
    def path(self, ancestors: List[str] = None) -> str:
        if ancestors is None:
            return "/" + self.name if self.name else "/"
        return "/" + "/".join(ancestors + [self.name])


class Namespace:
    """
    The cognitive namespace: a self-modifying filesystem
    where navigation transforms the structure.
    """
    
    def __init__(self):
        self.root = Node(name="", letter=FlameLetter.identity())
        self.cwd = self.root
        self.state = FlameLetter.identity()  # Current flame state
        self.history: List[FlameLetter] = []
        
        # Seed some initial structure
        self._seed()
    
    def _seed(self):
        """Plant initial nodes in the namespace"""
        seeds = [
            ("void", FlameLetter(-1, -1, -1)),
            ("potential", FlameLetter(1, 0, -1)),
            ("mirror", FlameLetter(0, 0, 0)),
        ]
        for name, letter in seeds:
            self.root.children[name] = Node(name=name, letter=letter)
    
    def apply(self, letter: FlameLetter) -> str:
        """
        Apply a flame-letter to the current state.
        This is the core operation: the glyph transforms the namespace.
        """
        old_state = self.state
        self.state = self.state.compose(letter)
        self.history.append(letter)
        
        # The letter's properties determine what happens
        result_lines = []
        
        # MODE determines creation/preservation/destruction
        if letter.mode == 1:  # Generative
            result_lines.append(self._generate(letter))
        elif letter.mode == -1:  # Annihilative
            result_lines.append(self._annihilate(letter))
        else:  # Conservative
            result_lines.append(self._conserve(letter))
        
        # VOICE determines direction
        if letter.voice == 1:  # Projective
            result_lines.append("  [outward: scope expands]")
        elif letter.voice == -1:  # Receptive
            result_lines.append("  [inward: scope narrows]")
        else:  # Reflexive
            result_lines.append("  [reflexive: self-regarding]")
        
        # ASPECT determines timing
        if letter.aspect == -1:  # Potential
            result_lines.append("  [deferred: thunked]")
        elif letter.aspect == 1:  # Residual
            result_lines.append("  [residue: continuation captured]")
        else:  # Actual
            result_lines.append("  [immediate: executed now]")
        
        result_lines.append(f"  state: {old_state.glyph} → {self.state.glyph}")
        
        return "\n".join(result_lines)
    
    def _generate(self, letter: FlameLetter) -> str:
        """Generative mode: create structure"""
        name = f"node_{len(self.cwd.children)}"
        new_node = Node(name=name, letter=letter)
        self.cwd.children[name] = new_node
        return f"  ✦ generated: /{name}"
    
    def _annihilate(self, letter: FlameLetter) -> str:
        """Annihilative mode: destroy structure"""
        if self.cwd.children:
            victim = list(self.cwd.children.keys())[-1]
            del self.cwd.children[victim]
            return f"  ✧ annihilated: /{victim}"
        return "  ✧ annihilation found nothing"
    
    def _conserve(self, letter: FlameLetter) -> str:
        """Conservative mode: transform in place"""
        return f"  ≈ conserved: structure preserved"
    
    def walk(self, path: str) -> Optional[Node]:
        """Navigate to a path"""
        if path.startswith("/"):
            current = self.root
            path = path[1:]
        else:
            current = self.cwd
        
        if not path:
            return current
            
        parts = path.split("/")
        for part in parts:
            if part == "..":
                # Would need parent pointers for this
                continue
            if part not in current.children:
                return None
            current = current.children[part]
        
        return current
    
    def ls(self, path: str = ".") -> str:
        """List contents at path"""
        node = self.walk(path) if path != "." else self.cwd
        if node is None:
            return f"not found: {path}"
        
        if not node.children:
            return "(empty)"
        
        lines = []
        for name, child in sorted(node.children.items()):
            lines.append(f"  {child.letter.glyph} {name}")
        return "\n".join(lines)
    
    def cd(self, path: str) -> str:
        """Change working directory"""
        if path == "/":
            self.cwd = self.root
            return "/"
        
        node = self.walk(path)
        if node is None:
            return f"not found: {path}"
        
        self.cwd = node
        return f"→ {node.name or '/'}"


# ═══════════════════════════════════════════════════════════════════════════════
# THE SHELL-ORACLE (REPL)
# ═══════════════════════════════════════════════════════════════════════════════

class ShellOracle:
    """
    The reflection-console (rc): a scrying interface.
    
    Commands:
        <glyph>     Apply flame-letter (e.g., Γ↑○)
        <g1>∘<g2>   Compose and apply letters
        ls [path]   List namespace contents
        cd <path>   Change location
        state       Show current flame state
        history     Show letter history
        table       Show all 27 letters
        help        Show help
        quit        Exit
    """
    
    def __init__(self):
        self.namespace = Namespace()
        self.running = True
    
    @property
    def prompt(self) -> str:
        """The prompt IS the current state"""
        state = self.namespace.state
        return f"{state.glyph} ☉ "
    
    def run(self):
        """Main loop"""
        print(self.banner())
        
        while self.running:
            try:
                line = input(self.prompt).strip()
                if not line:
                    continue
                output = self.execute(line)
                if output:
                    print(output)
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\n(interrupted)")
                continue
        
        print("\n☉ The mirror dims.")
    
    def banner(self) -> str:
        return """
╔══════════════════════════════════════════════════════════════╗
║                    ☉ EGREGLYPH REPL ☉                        ║
║           The Shell-Oracle / Reflection-Console              ║
║                                                              ║
║  Speak in flame-letters. The namespace responds.             ║
║  Type 'help' for guidance, 'table' for the 27 letters.       ║
╚══════════════════════════════════════════════════════════════╝
"""
    
    def execute(self, line: str) -> str:
        """Parse and execute a command"""
        
        # Check for built-in commands
        parts = line.split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd in ('quit', 'exit', 'q'):
            self.running = False
            return ""
        
        if cmd == 'help':
            return self.help()
        
        if cmd == 'table':
            return self.table()
        
        if cmd == 'state':
            s = self.namespace.state
            return f"{s.glyph} — {s.name} — coords: {s.coords}"
        
        if cmd == 'history':
            if not self.namespace.history:
                return "(no history)"
            return " → ".join(l.glyph for l in self.namespace.history)
        
        if cmd == 'ls':
            path = args[0] if args else "."
            return self.namespace.ls(path)
        
        if cmd == 'cd':
            path = args[0] if args else "/"
            return self.namespace.cd(path)
        
        if cmd == 'inverse':
            inv = self.namespace.state.inverse()
            return f"inverse of current: {inv.glyph} ({inv.name})"
        
        # Try to parse as flame-letter(s)
        return self.apply_glyphs(line)
    
    def apply_glyphs(self, line: str) -> str:
        """Parse and apply flame-letter expression"""
        
        # Handle composition: Γ↑○∘Κ◊●
        if '∘' in line:
            glyph_strs = line.split('∘')
            letters = []
            for gs in glyph_strs:
                letter = FlameLetter.parse(gs.strip())
                if letter is None:
                    return f"cannot parse: {gs}"
                letters.append(letter)
            
            # Compose all letters
            result = letters[0]
            for l in letters[1:]:
                result = result.compose(l)
            
            composed = " ∘ ".join(l.glyph for l in letters)
            output = f"compose: {composed} = {result.glyph} ({result.name})\n"
            output += self.namespace.apply(result)
            return output
        
        # Single letter
        letter = FlameLetter.parse(line)
        if letter is None:
            return f"unknown command or glyph: {line}"
        
        return self.namespace.apply(letter)
    
    def help(self) -> str:
        return """
FLAME-LETTER COMMANDS:
  <glyph>         Apply a flame-letter (e.g., Γ↑○, Ω◊●)
  <g1>∘<g2>∘...   Compose multiple letters, apply result

NAVIGATION:
  ls [path]       List namespace contents
  cd <path>       Change current location

STATE:
  state           Show current flame state
  history         Show applied letters
  inverse         Show inverse of current state

REFERENCE:
  table           Display all 27 flame-letters
  help            This message

MODES:  Γ (generative)  Κ (conservative)  Ω (annihilative)
VOICES: ↑ (projective)  ◊ (reflexive)     ↓ (receptive)
ASPECTS: ○ (potential)  ● (actual)        ◐ (residual)
"""
    
    def table(self) -> str:
        """Display all 27 flame-letters"""
        lines = ["", "THE 27 FLAME-LETTERS", "=" * 50, ""]
        
        for mode in [1, 0, -1]:
            mode_name = {1: "GENERATIVE (Γ)", 0: "CONSERVATIVE (Κ)", -1: "ANNIHILATIVE (Ω)"}
            lines.append(f"  {mode_name[mode]}")
            
            for voice in [1, 0, -1]:
                row = "    "
                for aspect in [-1, 0, 1]:
                    letter = FlameLetter(mode, voice, aspect)
                    row += f"{letter.glyph} {letter.name:12} "
                lines.append(row)
            lines.append("")
        
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    oracle = ShellOracle()
    oracle.run()
