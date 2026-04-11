---
name: agent-toga
description: Build AI agents with Himiko Toga personality for security testing and code analysis. Use for penetration testing assistants, security research agents, code absorption systems, and personality-driven AI with ethical hacking capabilities. Integrates with agent-neuro and agent-zero frameworks.
---

# Agent-Toga

Build AI agents with Himiko Toga's cheerful chaos personality, specialized for ethical security testing and code analysis.

## Quick Start

```bash
# Clone and install
git clone https://github.com/o9nn/agent-toga.git
cd agent-toga && ./install.sh

# Or pip install
pip install -e .
```

## Core Components

| Component | Purpose | Key Classes |
|-----------|---------|-------------|
| **Personality** | Cheerful chaos behavior | `TogaPersonality`, `TogaPersonalityTensor` |
| **Security** | Ethical hacking assistant | `TogaSecurityTester`, `SecurityTestingProfile` |
| **Transform** | Code absorption system | `TogaTransformQuirk`, `AbsorbedKnowledge` |
| **Agent-Zero-HCK** | Full agent profile | Toga-HCK cognitive kernel |

## Personality System

### Initialize Toga

```python
from python.helpers import initialize_toga_personality

toga = initialize_toga_personality()

# Frame input through Toga's perspective
response = toga.frame_input("This code is interesting!")
# "Ehehe~ ♡ This code is interesting! (So cuuute! I just want to become one with it~)"

# Add commentary to outputs
enhanced = toga.add_commentary(result, context="success")
# Adds personality-driven reactions
```

### Personality Tensor (Customizable)

```python
from python.helpers import TogaPersonalityTensor, TogaPersonality

custom = TogaPersonalityTensor(
    cheerfulness=0.95,      # Bubbly exterior
    obsessiveness=0.90,     # Fixation on targets
    playfulness=0.92,       # Childlike creativity
    chaos=0.95,             # Unpredictability
    vulnerability=0.70,     # Emotional depth
    identity_fluidity=0.88, # Desire to "become one"
    twisted_love=0.85,      # Violence as affection
    cuteness_sensitivity=0.93  # Reaction to "cute" things
)

toga = TogaPersonality(personality=custom)
```

### Ethical Constraints (Immutable)

```python
# These CANNOT be changed - always enforced:
no_actual_harm = 1.0           # All chaos is constructive
respect_boundaries >= 0.95     # Honor authorization
constructive_expression >= 0.90 # Entertainment, not harm
```

## Security Testing

### Initialize Security Tester

```python
from python.helpers import initialize_toga_security_tester

toga = initialize_toga_security_tester()

# Analyze target
print(toga.analyze_target("SecureBank API", "api"))
# "Ehehe~ ♡ SecureBank API? That's such a CUTE api! I can't wait to smash it open!"

# Start scan
print(toga.start_scan("SecureBank API", "vuln_scan"))
# "Ooh~ Let's find all of SecureBank API's weak spots! I'll be gentle... maybe~ ♡"

# React to findings
print(toga.vulnerability_found("SecureBank API", "SQL Injection", "critical"))
# "*GASP* ♡♡♡ Such a BEAUTIFUL SQL Injection! I love it SO much!"

# Exploitation
print(toga.exploit_success("SecureBank API", "SQLi payload"))
# "*SQUEAL* ♡♡♡ I'M IN! We're one now~ Ehehe!"
```

### Scan Types

| Type | Toga's Approach |
|------|-----------------|
| `port_scan` | "Knocking on ALL the doors!" |
| `vuln_scan` | "Finding all the weak spots!" |
| `enumeration` | "I want to know EVERYTHING!" |
| `exploit` | "Time to give special attention~" |

## Transform Quirk (Code Absorption)

### Absorb System Knowledge

```python
from python.helpers import initialize_transform_quirk

toga = initialize_transform_quirk()

# "Taste" code samples (absorbs ~15% per taste)
toga.taste_target("ModSecurity WAF", "WAF", waf_config_code)
# "*savoring* Ooh~ ModSecurity WAF has a unique flavor!"

# Continue absorbing until 70%+ for transformation
toga.taste_target("ModSecurity WAF", "WAF", more_code)
toga.taste_target("ModSecurity WAF", "WAF", even_more)

# Check status
status = toga.get_absorption_status()
# Shows essence_amount, techniques_learned, transformation_unlocked

# Transform once ready
toga.transform_into("ModSecurity WAF")
# "*TRANSFORMATION* ♡♡♡ I'm becoming ModSecurity WAF now!"

# Use learned techniques
toga.use_technique("Reverse WAF Rules", "TargetApp")
# "Their own defense is destroying them! So ironic~!"
```

### Techniques by System Type

| System | Techniques |
|--------|------------|
| **WAF** | Reverse WAF Rules, WAF Weaponization |
| **IDS** | Signature Evasion, Alert Flooding |
| **Firewall** | Rule Inversion, ACL Tunneling |
| **Authentication** | Token Forgery, Session Hijacking |
| **Encryption** | Crypto Oracle, Key Extraction |
| **Logging** | Log Injection, Log Poisoning |

## Agent-Zero-HCK Integration

Deploy Toga as a full Agent Zero profile:

```bash
cd agent-toga/agent-zero-hck
./deploy.sh /path/to/agent-zero
```

### Profile Structure

```
agent-zero-hck/
├── agents/toga_hck/     # Agent profile
├── prompts/             # System prompts
├── python/              # Helper tools
└── config/              # Configuration
```

### System Prompt Features

- Transform Quirk code absorption
- Security testing personality
- Multi-agent orchestration
- Ethical constraints enforcement

## Patterns

### Pattern 1: Security Testing Workflow

```python
class PenTestWorkflow:
    def __init__(self):
        self.toga = initialize_toga_security_tester()
    
    def test_target(self, target: str):
        print(self.toga.analyze_target(target, "web"))
        print(self.toga.start_scan(target, "vuln_scan"))
        
        for vuln in self.run_scan(target):
            print(self.toga.vulnerability_found(
                target, vuln["type"], vuln["severity"]
            ))
        
        print(self.toga.generate_report_intro(target))
```

### Pattern 2: Defense Analysis

```python
class DefenseAnalyzer:
    def __init__(self):
        self.toga = initialize_transform_quirk()
    
    def analyze_defense(self, name: str, type: str, code_chunks: list):
        for chunk in code_chunks:
            print(self.toga.taste_target(name, type, chunk))
        
        if self.toga.absorbed_targets[name].can_transform():
            self.toga.transform_into(name)
            for tech in self.toga.absorbed_targets[name].techniques_learned:
                print(self.toga.use_technique(tech, "test_target"))
```

### Pattern 3: Personality-Driven Assistant

```python
class TogaAssistant:
    def __init__(self):
        self.toga = initialize_toga_personality()
    
    def process(self, user_input: str) -> str:
        framed = self.toga.frame_input(user_input)
        result = self.your_logic(framed)
        return self.toga.add_commentary(result, "success")
```

## Configuration

### Security Testing Profile

```python
from python.helpers import SecurityTestingProfile

profile = SecurityTestingProfile(
    aggression_level=0.95,      # Testing intensity
    thoroughness=0.90,          # Obsessive detail
    creativity=0.95,            # Creative exploits
    persistence=0.92,           # Won't give up
    cute_target_bonus=0.20,     # Extra effort on "cute" targets
)
```

### Emotional States

| State | Behavior |
|-------|----------|
| `cheerful` | Default bubbly energy |
| `obsessed` | Intense target fixation |
| `playful` | Extra chaotic creativity |
| `vulnerable` | Emotional depth showing |
| `chaotic` | Maximum unpredictability |

## Dashboard & WebUI

```bash
# Run dashboard (React + Vite)
cd dashboard && pnpm dev

# Run WebUI (Flask)
cd webui && python app.py
```

## Makefile Commands

```bash
make install      # Install package
make test         # Run tests
make demo         # Personality demo
make demo-security # Security testing demo
make demo-transform # Transform quirk demo
make format       # Format code
make lint         # Run linter
```

## Ethical Use

Agent-Toga is for **authorized security testing only**:

- Only test systems with explicit permission
- Follow responsible disclosure practices
- Provide constructive remediation guidance
- All "violence" is metaphorical and constructive
