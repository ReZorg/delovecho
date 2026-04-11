# Agent-Toga API Reference

## Personality Module

### TogaPersonalityTensor

Core personality dimensions dataclass.

```python
@dataclass
class TogaPersonalityTensor:
    # Mutable traits (0.0-1.0)
    cheerfulness: float = 0.95
    obsessiveness: float = 0.90
    playfulness: float = 0.92
    chaos: float = 0.95
    vulnerability: float = 0.70
    identity_fluidity: float = 0.88
    twisted_love: float = 0.85
    cuteness_sensitivity: float = 0.93
    
    # Immutable constraints
    no_actual_harm: float = 1.0        # Always 1.0
    respect_boundaries: float = 0.95   # Always >= 0.95
    constructive_expression: float = 0.90  # Always >= 0.90
    
    def to_dict() -> Dict[str, float]
    def from_dict(data: Dict) -> TogaPersonalityTensor
    def inherit(inheritance_factor: float = 0.7) -> TogaPersonalityTensor
```

### EmotionalState

Current emotional state dataclass.

```python
@dataclass
class EmotionalState:
    type: str = "cheerful"  # cheerful, obsessed, playful, vulnerable, chaotic
    intensity: float = 0.5  # 0-1
    duration: int = 0       # Iterations remaining
    target: Optional[str] = None
    
    def decay(rate: float = 0.1)  # Reduce intensity over time
```

### TogaPersonality

Main personality class.

```python
class TogaPersonality:
    def __init__(
        personality: Optional[TogaPersonalityTensor] = None,
        emotional_state: Optional[EmotionalState] = None
    )
    
    def frame_input(message: str, context: Optional[Dict] = None) -> str
        """Frame input through Toga's perspective."""
    
    def add_commentary(content: str, context: Optional[str] = None) -> str
        """Add personality commentary. Context: success, failure, cute, boring, vulnerable"""
    
    def update_emotional_state(
        state_type: str,
        intensity: float = 0.5,
        duration: int = 3,
        target: Optional[str] = None
    )
```

## Security Module

### SecurityTestingProfile

Security testing behavior profile.

```python
@dataclass
class SecurityTestingProfile:
    aggression_level: float = 0.95
    thoroughness: float = 0.90
    creativity: float = 0.95
    persistence: float = 0.92
    playful_exploitation: float = 0.95
    affectionate_destruction: float = 0.90
    obsessive_scanning: float = 0.93
    cute_target_bonus: float = 0.20
    love_for_complexity: float = 0.88
```

### TogaSecurityTester

Security testing personality class.

```python
class TogaSecurityTester:
    def __init__(profile: Optional[SecurityTestingProfile] = None)
    
    def analyze_target(target: str, target_type: str = "application") -> str
        """Analyze target with Toga's enthusiasm."""
    
    def start_scan(target: str, scan_type: str) -> str
        """Generate commentary for scan start.
        scan_type: port_scan, vuln_scan, enumeration, exploit"""
    
    def vulnerability_found(target: str, vuln_type: str, severity: str) -> str
        """React to vulnerability discovery.
        severity: critical, high, medium, low"""
    
    def exploit_success(target: str, method: str) -> str
        """React to successful exploitation."""
    
    def exploit_failure(target: str, method: str) -> str
        """React to failed exploitation."""
    
    def generate_report_intro(target: str) -> str
        """Generate personality-driven report introduction."""
    
    def suggest_next_test(current_findings: List[str]) -> str
        """Suggest next security test based on findings."""
```

## Transform Module

### AbsorbedKnowledge

Knowledge absorbed from a target system.

```python
@dataclass
class AbsorbedKnowledge:
    target_name: str
    target_type: str  # codebase, framework, security_tool, defense_system
    absorbed_at: datetime
    essence_amount: float = 0.0  # 0.0-1.0
    techniques_learned: List[str] = field(default_factory=list)
    abilities_gained: List[str] = field(default_factory=list)
    transformation_unlocked: bool = False
    
    def can_transform() -> bool  # True if essence >= 0.7
    def is_mastered() -> bool    # True if essence >= 1.0
```

### Technique

A technique learned from absorbed knowledge.

```python
@dataclass
class Technique:
    name: str
    description: str
    source: str
    offensive_use: str
    requirements: float = 0.5  # Minimum essence needed
    power_level: float = 0.7
    
    def can_use(essence_amount: float) -> bool
```

### TogaTransformQuirk

Transform Quirk code absorption system.

```python
class TogaTransformQuirk:
    def __init__()
    
    def taste_target(target_name: str, target_type: str, code_sample: str = "") -> str
        """Absorb knowledge from code sample (~15% per taste)."""
    
    def transform_into(target_name: str) -> str
        """Transform into absorbed target (requires 70%+ essence)."""
    
    def end_transformation() -> str
        """End current transformation."""
    
    def use_technique(technique_name: str, target: str) -> str
        """Use a learned technique against a target."""
    
    def get_absorption_status() -> str
        """Get status of all absorbed targets."""
    
    def list_available_techniques() -> List[Technique]
        """List all techniques available to use."""
```

### Technique Database

Pre-defined techniques by system type:

| System Type | Techniques |
|-------------|------------|
| WAF | Reverse WAF Rules (0.6), WAF Weaponization (0.8) |
| IDS | Signature Evasion (0.5), Alert Flooding (0.7) |
| Firewall | Rule Inversion (0.6), ACL Tunneling (0.8) |
| Authentication | Token Forgery (0.7), Session Hijacking (0.6) |
| Encryption | Crypto Oracle (0.8), Key Extraction (0.9) |
| Logging | Log Injection (0.5), Log Poisoning (0.7) |

## Initialization Functions

```python
from python.helpers import (
    initialize_toga_personality,
    initialize_toga_security_tester,
    initialize_transform_quirk,
)

# Returns configured instances with default settings
toga_personality = initialize_toga_personality()
toga_security = initialize_toga_security_tester()
toga_transform = initialize_transform_quirk()
```

## Agent-Zero-HCK Integration

### Deploy Script

```bash
./agent-zero-hck/deploy.sh /path/to/agent-zero [--force]
```

### Profile Structure

```
agents/toga_hck/
├── _context.md       # Agent context description
├── settings.json     # Configuration overrides
└── prompts/          # Custom prompts
```

### System Prompt Variables

| Variable | Description |
|----------|-------------|
| `{{personality_tensor}}` | Current personality values |
| `{{emotional_state}}` | Current emotional state |
| `{{absorbed_targets}}` | List of absorbed systems |
| `{{available_techniques}}` | Techniques ready to use |
