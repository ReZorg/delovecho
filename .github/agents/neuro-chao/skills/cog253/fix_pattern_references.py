#!/usr/bin/env python3
"""
Fix incorrect references to pattern 12612250 in markdown files.
These references use the wrong pattern names, so we need to fix them.
"""

import re

# Mapping of wrong references to correct pattern IDs based on the names
corrections = {
    'markdown/uia/12612490.md': [
        ('[Unalienating internal boundaries](12612250)', '[Unalienating internal boundaries](12612350)')
    ],
    'markdown/uia/12612400.md': [
        ('[Unalienating internal boundaries](12612250)', '[Unalienating internal boundaries](12612350)')
    ],
    'markdown/uia/12612370.md': [
        ('[Distortion resistant boundaries](12612250)', '[Distortion resistant boundaries](12612180)')
    ],
    'markdown/uia/12612080.md': [
        ('[Distortion resistant boundaries](12612250)', '[Distortion resistant boundaries](12612180)')
    ],
    'markdown/uia/12612270.md': [
        ('[Partially contained interfaces](12612250)', '[Partially contained interfaces](12611190)')
    ],
    'markdown/uia/12612220.md': [
        ('[Displaceable frameworks](12612250)', '[Displaceable frameworks](12612360)')
    ],
    'markdown/uia/12612310.md': [
        ('[Progressive framework definition](12612250)', '[Progressive framework definition](12612080)')
    ],
    'markdown/uia/12612060.md': [
        ('[Appropriate construction elements](12612250)', '[Appropriate construction elements](12612070)')
    ],
    'markdown/uia/12611960.md': [
        ('[Connectedness in isolation](12612250)', '[Connectedness in isolation](12612370)')
    ],
    'markdown/uia/12612240.md': [
        ('[Symbols of integration](12612250)', '[Symbols of integration](12612490)')
    ],
    'markdown/uia/12612230.md': [
        ('[Tolerance at level interfaces](12612250)', '[Tolerance at level interfaces](12612400)')
    ],
    'markdown/uia/12612210.md': [
        ('[Zones of intermediate insight](12612250)', '[Zones of intermediate insight](12612230)')
    ],
    'markdown/uia/12612390.md': [
        ('[Overview of external contexts](12612250)', '[Overview of external contexts](12610240)')
    ],
    'markdown/uia/12612360.md': [
        ('[Overview of external contexts](12612250)', '[Overview of external contexts](12610240)')
    ],
}

print("Fixing incorrect pattern references...")
for filepath, replacements in corrections.items():
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        modified = False
        for old, new in replacements:
            if old in content:
                content = content.replace(old, new)
                modified = True
                print(f"✓ {filepath}: {old} -> {new}")
        
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
    except Exception as e:
        print(f"✗ Error processing {filepath}: {e}")

print("\nDone!")
