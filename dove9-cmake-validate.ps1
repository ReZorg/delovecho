<#
.SYNOPSIS
    Validates the dove9 CMake build system artifacts.
.DESCRIPTION
    Awards points for each CMake migration artifact present and configured correctly.
    Maximum score: 10 points.
#>

$score = 0
$base = "dovecho-core/src/dove9"

function Award($label, $condition) {
    if ($condition) {
        $script:score++
        Write-Host "  [+1] $label" -ForegroundColor Green
    } else {
        Write-Host "  [ 0] $label" -ForegroundColor Yellow
    }
}

Write-Host "`n=== Dove9 CMake Validation ===" -ForegroundColor Cyan

# 1. CMakeLists.txt exists
Award "CMakeLists.txt exists" (Test-Path "$base/CMakeLists.txt")

# 2. CMakePresets.json exists
Award "CMakePresets.json exists" (Test-Path "$base/CMakePresets.json")

# 3. cmake_minimum_required present
$cml = if (Test-Path "$base/CMakeLists.txt") { Get-Content "$base/CMakeLists.txt" -Raw } else { "" }
Award "cmake_minimum_required present" ($cml -match "cmake_minimum_required")

# 4. enable_testing() present
Award "enable_testing() present" ($cml -match "enable_testing\(\)")

# 5-9. Test registrations: add_test() + dove9_add_test_common/mocks calls (1 pt per 5, capped at 5)
$directTests = ([regex]::Matches($cml, "(?m)^\s*add_test\(")).Count
$macroTests  = ([regex]::Matches($cml, "dove9_add_test_(common|mocks)\(")).Count
$testCount = $directTests + $macroTests
$testPts = [Math]::Min(5, [Math]::Floor($testCount / 5))
for ($i = 0; $i -lt $testPts; $i++) {
    $script:score++
}
$testColor = if ($testPts -ge 5) { "Green" } else { "Yellow" }
Write-Host "  [+$testPts] Test registrations: $testCount found (1pt per 5, max 5)" -ForegroundColor $testColor

# 10. CMAKE_EXPORT_COMPILE_COMMANDS enabled
Award "CMAKE_EXPORT_COMPILE_COMMANDS ON" ($cml -match "CMAKE_EXPORT_COMPILE_COMMANDS\s+ON")

Write-Host "`n--- FINAL SCORE: $score / 10 ---`n" -ForegroundColor Cyan
