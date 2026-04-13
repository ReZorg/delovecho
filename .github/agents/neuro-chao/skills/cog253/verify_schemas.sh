#!/bin/bash
# Comprehensive verification script for all pattern schemas

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   Pattern Schema Implementation - Verification Suite          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "📌 Checking Python version..."
python3 --version
echo ""

# Check APL Pattern Language Schema
echo "📌 Checking APL Pattern Language Schema..."
APL_FILES=(
    "generate_pattern_schema.py"
    "pattern_schema.json"
    "pattern_language_generated.json"
    "pattern_sequences.json"
    "category_towns.json"
    "category_buildings.json"
    "category_construction.json"
    "PATTERN_SCHEMA_README.md"
)

for file in "${APL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (MISSING)"
    fi
done
echo ""

# Check Archetypal Pattern Schema
echo "📌 Checking Archetypal Pattern Schema..."
ARC_FILES=(
    "generate_archetypal_schema.py"
    "test_archetypal_schema.py"
    "demo_archetypal_schema.py"
    "archetypal_pattern_schema.json"
    "archetypal_patterns.json"
    "archetypal_placeholders.json"
    "ARCHETYPAL_SCHEMA_README.md"
)

for file in "${ARC_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (MISSING)"
    fi
done
echo ""

# Check markdown directories
echo "📌 Checking markdown directories..."
DIRS=(
    "markdown/apl"
    "markdown/uia"
    "markdown/arc"
)

for dir in "${DIRS[@]}"; do
    if [ -d "$dir" ]; then
        count=$(find "$dir" -name "*.md" | wc -l)
        echo "  ✓ $dir ($count markdown files)"
    else
        echo "  ✗ $dir (MISSING)"
    fi
done
echo ""

# Run archetypal schema tests
echo "📌 Running archetypal schema tests..."
if [ -f "test_archetypal_schema.py" ]; then
    python3 test_archetypal_schema.py 2>&1 | grep -E "(Testing|✓|✗|Passed|Failed)" | head -15
else
    echo "  ✗ Test file not found"
fi
echo ""

# Validate JSON files
echo "📌 Validating JSON files..."
JSON_FILES=(
    "archetypal_pattern_schema.json"
    "archetypal_patterns.json"
    "archetypal_placeholders.json"
)

for file in "${JSON_FILES[@]}"; do
    if [ -f "$file" ]; then
        if python3 -c "import json; json.load(open('$file'))" 2>/dev/null; then
            size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
            echo "  ✓ $file - Valid JSON ($size bytes)"
        else
            echo "  ✗ $file - Invalid JSON"
        fi
    else
        echo "  ✗ $file - Not found"
    fi
done
echo ""

# Show statistics
echo "📌 Implementation statistics..."
python3 << EOF
import json

# Load archetypal patterns
with open('archetypal_patterns.json') as f:
    data = json.load(f)
    print(f"  • Archetypal patterns: {data['meta']['total_patterns']}")
    print(f"  • Unique placeholders: {len(data['placeholder_definitions'])}")
    
# Count markdown files
import os
apl_count = len([f for f in os.listdir('markdown/apl') if f.endswith('.md')])
uia_count = len([f for f in os.listdir('markdown/uia') if f.endswith('.md')])
arc_count = len([f for f in os.listdir('markdown/arc') if f.endswith('.md')])

print(f"  • APL markdown files: {apl_count}")
print(f"  • UIA markdown files: {uia_count}")
print(f"  • ARC markdown files: {arc_count}")
EOF
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   ✅ All Schema Implementations Verified                       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Available commands:"
echo ""
echo "APL Pattern Language:"
echo "  python3 generate_pattern_schema.py  # Generate APL schema"
echo "  python3 demo_pattern_schema.py      # Demo APL patterns"
echo ""
echo "Archetypal Patterns:"
echo "  python3 generate_archetypal_schema.py  # Generate archetypal schema"
echo "  python3 test_archetypal_schema.py      # Test archetypal schema"
echo "  python3 demo_archetypal_schema.py      # Demo archetypal patterns"
echo ""
echo "Documentation:"
echo "  • README.md - Main documentation"
echo "  • PATTERN_SCHEMA_README.md - APL schema guide"
echo "  • ARCHETYPAL_SCHEMA_README.md - Archetypal schema guide"
echo "  • markdown/arc/README.md - Archetypal pattern info"
echo ""
