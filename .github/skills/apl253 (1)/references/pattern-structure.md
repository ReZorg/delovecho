# Pattern Structure Reference

## Directory Layout

```
patterns/apl0/
├── dim{0-5}.md          # Dimension descriptions
└── dim{0-5}/
    └── cat{1-3}/        # Categories (Towns/Buildings/Construction)
        └── seq{01-36}/  # 36 Sequences
            ├── apl{NNN}.md           # Pattern content
            └── apl{NNN}/
                ├── broader.md        # Parent patterns (context)
                └── narrower.md       # Child patterns (detail)
```

## Dimensions (6 Perspectives)

| Code | Name | Description |
|------|------|-------------|
| dim0 | Archetypal | Abstract patterns with domain-specific placeholders |
| dim1 | Template | Generic template patterns |
| dim2 | Physical | Spatial, material, architectural |
| dim3 | Social | Organizational, community |
| dim4 | Conceptual | Knowledge, theoretical |
| dim5 | Interpersonal | Awareness, consciousness |

## Categories (3 Scales)

| Code | Name | Pattern Range | Count |
|------|------|---------------|-------|
| cat1 | Towns | 1-94 | 94 |
| cat2 | Buildings | 95-204 | 110 |
| cat3 | Construction | 205-253 | 49 |

## Pattern File Format

```markdown
---
name: apl{NNN}
description: "{ID} - {PATTERN NAME}"
---

# {PATTERN NAME}

## Problem
{Problem description}

## Solution
{Solution description}

## Related Patterns
- apl{NNN}: {Name}
```

## Broader/Narrower Files

**broader.md** - Patterns providing context (apply before):
```markdown
---
name: broader
description: Broader Patterns for apl{NNN}
---
# BROADER Instructions
These patterns provide context and are typically applied before this pattern:
- apl{NNN}
```

**narrower.md** - Patterns providing detail (apply after):
```markdown
---
name: narrower
description: Narrower Patterns for apl{NNN}
---
# NARROWER Instructions
These patterns provide detail and are typically applied after this pattern:
- apl{NNN}
```

## Key Statistics

- Total patterns: 253
- Total broader edges: 1,167
- Total narrower edges: 1,270
- Root patterns (no broader): 5 (1, 18, 24, 95, 253)
- Leaf patterns (no narrower): 9
- Max depth: 6 levels
