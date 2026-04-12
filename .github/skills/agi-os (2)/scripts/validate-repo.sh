#!/bin/bash
# AGI-OS Repository Health Validator
# Run from the agi-os repo root to check for common issues
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

check_pass() { echo -e "  ${GREEN}✓${NC} $1"; }
check_fail() { echo -e "  ${RED}✗${NC} $1"; ERRORS=$((ERRORS + 1)); }
check_warn() { echo -e "  ${YELLOW}⚠${NC} $1"; WARNINGS=$((WARNINGS + 1)); }

echo -e "${BLUE}AGI-OS Repository Health Check${NC}"
echo -e "${BLUE}==============================${NC}"
echo ""

# 1. Check critical files exist
echo -e "${BLUE}[1/6] Critical files${NC}"
for f in CMakeLists.txt build-agi-os.sh BUILD-DEPENDENCY-ORDER.md; do
    if [ -f "$f" ]; then
        check_pass "$f exists"
    else
        check_fail "$f missing"
    fi
done

# 2. Check MIG locations
echo -e "${BLUE}[2/6] MIG build dependency${NC}"
for d in build-tools/mig core/microkernel/cognumach/mig core/microkernel/mig; do
    if [ -d "$d" ]; then
        check_pass "$d exists"
    else
        check_warn "$d missing"
    fi
done

# 3. Check core subsystems
echo -e "${BLUE}[3/6] Core subsystems${NC}"
for d in core/microkernel/cognumach core/os/hurdcog core/cognition/foundation/cogutil core/cognition/foundation/atomspace core/integration/cognitive-grip; do
    if [ -d "$d" ]; then
        check_pass "$d exists"
    else
        check_fail "$d missing"
    fi
done

# 4. Check for truncated bash scripts
echo -e "${BLUE}[4/6] Truncated shell scripts${NC}"
TRUNCATED=$(grep -rl 'while \[\[ \$\s*$' --include='*.sh' . 2>/dev/null | grep -v '.git/' | grep -v 'fix-truncated' | wc -l)
if [ "$TRUNCATED" -eq 0 ]; then
    check_pass "No truncated bash expressions found"
else
    check_fail "$TRUNCATED files with truncated bash expressions"
fi

# 5. Debian packaging validation
echo -e "${BLUE}[5/6] Debian packaging${NC}"
if [ -d "infrastructure/packaging/debian" ]; then
    TOTAL=$(ls -d infrastructure/packaging/debian/*/ 2>/dev/null | wc -l)
    VALID=0
    for pkg_dir in infrastructure/packaging/debian/*/; do
        pkg=$(basename "$pkg_dir")
        all_ok=true
        for f in control rules changelog compat copyright; do
            [ ! -f "${pkg_dir}debian/$f" ] && all_ok=false
        done
        [ ! -f "${pkg_dir}debian/source/format" ] && all_ok=false
        $all_ok && VALID=$((VALID + 1))
    done
    if [ "$VALID" -eq "$TOTAL" ]; then
        check_pass "All $TOTAL Debian packages valid"
    else
        check_fail "$VALID/$TOTAL Debian packages valid"
    fi
else
    check_warn "No Debian packaging directory found"
fi

# 6. CMakeLists.txt syntax check
echo -e "${BLUE}[6/6] CMake configuration${NC}"
if grep -q "BUILD_COGUTIL" CMakeLists.txt && grep -q "BUILD_ATOMSPACE" CMakeLists.txt; then
    check_pass "Root CMakeLists.txt has OCC build options"
else
    check_fail "Root CMakeLists.txt missing OCC build options"
fi
if grep -q "BUILD_COGNUMACH" CMakeLists.txt && grep -q "BUILD_HURDCOG" CMakeLists.txt; then
    check_pass "Root CMakeLists.txt has kernel/OS build options"
else
    check_fail "Root CMakeLists.txt missing kernel/OS build options"
fi

# Summary
echo ""
echo -e "${BLUE}==============================${NC}"
if [ "$ERRORS" -eq 0 ]; then
    echo -e "${GREEN}Health check passed${NC} ($WARNINGS warnings)"
else
    echo -e "${RED}Health check failed${NC} ($ERRORS errors, $WARNINGS warnings)"
fi
