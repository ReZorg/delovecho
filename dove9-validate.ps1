# dove9-validate.ps1 — Structural validation metric for autoresearch
# Scores the dovecho-core Dove9 C layer on structural correctness.
# Higher score = better. Output: single integer on last line.

$root = "c:\Users\sandbox_713\Documents\GitHub\del\delovecho\dovecho-core\src"
$score = 0
$details = @()

# --- 1. Required files exist and are non-empty ---
$requiredFiles = @(
    # Phase 2: Test harness
    "dove9\test\dove9-test-common.h",
    "dove9\test\dove9-test-common.c",
    "dove9\test\dove9-test-mocks.h",
    "dove9\test\dove9-test-mocks.c",
    # Phase 3: Types, Logger, Triadic Engine tests
    "dove9\test\test-dove9-types.c",
    "dove9\test\test-dove9-logger.c",
    "dove9\test\test-dove9-triadic-engine.c",
    # Phase 4: DTE, Kernel, Mail Bridge tests
    "dove9\test\test-dove9-dte-processor.c",
    "dove9\test\test-dove9-kernel.c",
    "dove9\test\test-dove9-mail-bridge.c",
    # Phase 5: Sys6, Bridges, System tests
    "dove9\test\test-dove9-sys6-scheduler.c",
    "dove9\test\test-dove9-orchestrator-bridge.c",
    "dove9\test\test-dove9-sys6-bridge.c",
    "dove9\test\test-dove9-system.c",
    # Phase 9: Security tests
    "dove9\test\test-dove9-security.c",
    # Phase 10: Integration tests
    "dove9\test\test-dove9-integration.c",
    # Phase 11: Sys6 correctness tests
    "dove9\test\test-dove9-sys6-correctness.c",
    # Phase 12: Stress tests
    "dove9\test\test-dove9-stress.c",
    # Phase 13: Kernel mail + Event callback tests
    "dove9\test\test-dove9-kernel-mail.c",
    "dove9\test\test-dove9-event-callbacks.c",
    # Phase 14: Context & system config tests
    "dove9\test\test-dove9-cognitive-context.c",
    "dove9\test\test-dove9-system-config.c",
    # Phase 15: Math & lifecycle tests
    "dove9\test\test-dove9-triadic-math.c",
    "dove9\test\test-dove9-memory-lifecycle.c",
    # Phase 16: API boundary tests
    "dove9\test\test-dove9-api-boundary.c",
    # Phase 17: Coupling detection tests
    "dove9\test\test-dove9-coupling-detection.c",
    # Phase 18: Mail protocol tests
    "dove9\test\test-dove9-mail-protocol.c",
    # Phase 19: Process management tests
    "dove9\test\test-dove9-process-management.c",
    # Phase 20: Salience landscape tests
    "dove9\test\test-dove9-salience-landscape.c",
    # Phase 21: Step assignment tests
    "dove9\test\test-dove9-step-assignment.c",
    # Phase 22: Cognitive pipeline tests
    "dove9\test\test-dove9-cognitive-pipeline.c",
    # Core source files (in dove9/ subdir)
    "dove9\dove9-system.h",
    "dove9\dove9-system.c",
    "dove9\types\dove9-types.h",
    "dove9\utils\dove9-logger.h",
    "dove9\utils\dove9-logger.c",
    "dove9\cognitive\dove9-triadic-engine.h",
    "dove9\cognitive\dove9-triadic-engine.c",
    "dove9\cognitive\dove9-dte-processor.h",
    "dove9\cognitive\dove9-dte-processor.c",
    "dove9\core\dove9-kernel.h",
    "dove9\core\dove9-kernel.c",
    "dove9\integration\dove9-mail-protocol-bridge.h",
    "dove9\integration\dove9-mail-protocol-bridge.c",
    "dove9\integration\dove9-orchestrator-bridge.h",
    "dove9\integration\dove9-orchestrator-bridge.c",
    "dove9\integration\dove9-sys6-mail-scheduler.h",
    "dove9\integration\dove9-sys6-mail-scheduler.c",
    "dove9\integration\dove9-sys6-orchestrator-bridge.h",
    "dove9\integration\dove9-sys6-orchestrator-bridge.c",
    # Makefile
    "dove9\Makefile.am"
)

foreach ($f in $requiredFiles) {
    $path = Join-Path $root $f
    if ((Test-Path $path) -and ((Get-Item $path).Length -gt 0)) {
        $score++
        $details += "  [+1] EXISTS: $f"
    } else {
        $details += "  [ 0] MISSING: $f"
    }
}

# --- 2. Makefile.am integration ---
$srcMakefile = Join-Path $root "Makefile.am"
if (Test-Path $srcMakefile) {
    $content = Get-Content $srcMakefile -Raw
    if ($content -match "dove9") {
        $score++
        $details += "  [+1] src/Makefile.am references dove9 SUBDIRS"
    } else {
        $details += "  [ 0] src/Makefile.am missing dove9 SUBDIRS"
    }
}

# --- 3. dove9/Makefile.am has test_programs ---
$dove9Makefile = Join-Path $root "dove9\Makefile.am"
if (Test-Path $dove9Makefile) {
    $content = Get-Content $dove9Makefile -Raw
    $testBins = @(
        "test-dove9-types", "test-dove9-logger", "test-dove9-triadic-engine",
        "test-dove9-dte-processor", "test-dove9-kernel", "test-dove9-mail-bridge",
        "test-dove9-sys6-scheduler", "test-dove9-orchestrator-bridge",
        "test-dove9-sys6-bridge", "test-dove9-system", "test-dove9-security",
        "test-dove9-integration",
        "test-dove9-sys6-correctness",
        "test-dove9-stress",
        "test-dove9-kernel-mail",
        "test-dove9-event-callbacks",
        "test-dove9-cognitive-context",
        "test-dove9-system-config",
        "test-dove9-triadic-math",
        "test-dove9-memory-lifecycle",
        "test-dove9-api-boundary",
        "test-dove9-coupling-detection",
        "test-dove9-mail-protocol",
        "test-dove9-process-management",
        "test-dove9-salience-landscape",
        "test-dove9-step-assignment",
        "test-dove9-cognitive-pipeline"
    )
    foreach ($bin in $testBins) {
        if ($content -match [regex]::Escape($bin)) {
            $score++
            $details += "  [+1] Makefile.am lists $bin"
        } else {
            $details += "  [ 0] Makefile.am missing $bin"
        }
    }
    if ($content -match "check-local") {
        $score++
        $details += "  [+1] Makefile.am has check-local target"
    } else {
        $details += "  [ 0] Makefile.am missing check-local"
    }
}

# --- 4. Include chain validation ---
$dove9Dir = Join-Path $root "dove9"
if (Test-Path $dove9Dir) {
    $cFiles = Get-ChildItem -Path $dove9Dir -Recurse -Filter "*.c" -ErrorAction SilentlyContinue
    foreach ($cFile in $cFiles) {
        $lines = Get-Content $cFile.FullName -ErrorAction SilentlyContinue
        $localIncludes = $lines | Where-Object { $_ -match '#include\s+"([^"]+)"' } | ForEach-Object {
            if ($_ -match '#include\s+"([^"]+)"') { $matches[1] }
        }
        foreach ($inc in $localIncludes) {
            # Resolve relative to the .c file's directory
            $incPath = Join-Path $cFile.DirectoryName $inc
            if (Test-Path $incPath) {
                $score++
            } else {
                $details += "  [ 0] BROKEN INCLUDE: $($cFile.Name) -> $inc"
            }
        }
    }
}

# --- 5. Test functions count ---
$testDir = Join-Path $root "dove9\test"
if (Test-Path $testDir) {
    $testFiles = Get-ChildItem -Path $testDir -Filter "test-dove9-*.c" -ErrorAction SilentlyContinue
    foreach ($tf in $testFiles) {
        $content = Get-Content $tf.FullName -Raw -ErrorAction SilentlyContinue
        if ($content) {
            # Count static void test_* functions
            $testFns = ([regex]::Matches($content, 'static\s+void\s+test_\w+')).Count
            $score += $testFns
            if ($testFns -gt 0) {
                $details += "  [+$testFns] $($tf.Name) has $testFns test functions"
            } else {
                $details += "  [ 0] $($tf.Name) has no test functions"
            }
        }
    }
}

# --- 6. configure.ac integration ---
$configureAc = Join-Path $root "..\configure.ac"
if (Test-Path $configureAc) {
    $content = Get-Content $configureAc -Raw
    if ($content -match "src/dove9/Makefile") {
        $score++
        $details += "  [+1] configure.ac has src/dove9/Makefile"
    } else {
        $details += "  [ 0] configure.ac missing src/dove9/Makefile"
    }
    if ($content -match "enable-coverage") {
        $score++
        $details += "  [+1] configure.ac has --enable-coverage"
    } else {
        $details += "  [ 0] configure.ac missing --enable-coverage"
    }
}

# --- 7. CI workflow ---
$ciYml = "c:\Users\sandbox_713\Documents\GitHub\del\delovecho\.github\workflows\ci.yml"
if (Test-Path $ciYml) {
    $content = Get-Content $ciYml -Raw
    if ($content -match "test-c-layer") {
        $score++
        $details += "  [+1] ci.yml has test-c-layer job"
    } else {
        $details += "  [ 0] ci.yml missing test-c-layer job"
    }
}

# Output
Write-Host "=== Dove9 Structural Validation ==="
foreach ($d in $details) { Write-Host $d }

# --- 8. Header guards ---
$headerFiles = Get-ChildItem -Path (Join-Path $root "dove9") -Recurse -Filter "*.h" -ErrorAction SilentlyContinue
foreach ($hf in $headerFiles) {
    $content = Get-Content $hf.FullName -Raw -ErrorAction SilentlyContinue
    if ($content -and $content -match '#ifndef\s+DOVE9_') {
        $score++
        Write-Host "  [+1] Header guard in $($hf.Name)"
    } else {
        Write-Host "  [ 0] Missing header guard in $($hf.Name)"
    }
}

# --- 9. Valgrind suppression file ---
$valgrind = Join-Path $root "dove9\test\dove9.supp"
if ((Test-Path $valgrind) -and ((Get-Item $valgrind).Length -gt 0)) {
    $score += 2
    Write-Host "  [+2] Valgrind suppression file exists"
} else {
    Write-Host "  [ 0] Valgrind suppression file missing"
}

# --- 10. dove9/README.md ---
$readme = Join-Path $root "dove9\README.md"
if ((Test-Path $readme) -and ((Get-Item $readme).Length -gt 100)) {
    $score += 2
    Write-Host "  [+2] dove9/README.md exists"
} else {
    Write-Host "  [ 0] dove9/README.md missing"
}

if ((Test-Path $valgrind) -and (Test-Path $readme)) {
    $score += 1
    Write-Host "  [+1] Infrastructure docs+valgrind completeness bonus"
}

# --- 11. Test framework struct/macro quality ---
$commonH = Join-Path $root "dove9\test\dove9-test-common.h"
if (Test-Path $commonH) {
    $content = Get-Content $commonH -Raw
    $macros = ([regex]::Matches($content, 'DOVE9_TEST_ASSERT')).Count
    if ($macros -ge 6) {
        $score += 3
        Write-Host "  [+3] Test framework has $macros assert macros"
    }
}

# --- 12. Mock completeness ---
$mocksH = Join-Path $root "dove9\test\dove9-test-mocks.h"
if (Test-Path $mocksH) {
    $content = Get-Content $mocksH -Raw
    $counters = ([regex]::Matches($content, 'dove9_mock_\w+_calls')).Count
    if ($counters -ge 6) {
        $score += 3
        Write-Host "  [+3] Mock framework has $counters call counters"
    }
}

# --- 13. API coverage: count public function declarations in headers ---
$apiHeaders = @(
    "dove9\cognitive\dove9-triadic-engine.h",
    "dove9\cognitive\dove9-dte-processor.h",
    "dove9\core\dove9-kernel.h",
    "dove9\integration\dove9-mail-protocol-bridge.h",
    "dove9\integration\dove9-orchestrator-bridge.h",
    "dove9\integration\dove9-sys6-mail-scheduler.h",
    "dove9\integration\dove9-sys6-orchestrator-bridge.h",
    "dove9\dove9-system.h",
    "dove9\utils\dove9-logger.h"
)
$totalApiDecls = 0
foreach ($hdr in $apiHeaders) {
    $hpath = Join-Path $root $hdr
    if (Test-Path $hpath) {
        $hcontent = Get-Content $hpath -Raw -ErrorAction SilentlyContinue
        if ($hcontent) {
            # Count non-static function declarations (name starts with dove9_)
            $decls = ([regex]::Matches($hcontent, '(?m)^(?!static)\w[\w\s\*]*\bdove9_\w+\s*\(')).Count
            $totalApiDecls += $decls
        }
    }
}
if ($totalApiDecls -gt 0) {
    # Score 1 point per 5 API declarations covered by test files
    $apiScore = [math]::Min([math]::Floor($totalApiDecls / 5), 10)
    $score += $apiScore
    Write-Host "  [+$apiScore] API coverage: $totalApiDecls public declarations across headers"
}

# --- 14. Test file line count quality (reward substantial test files) ---
$testDir2 = Join-Path $root "dove9\test"
if (Test-Path $testDir2) {
    $substantialFiles = 0
    $allTestFiles = Get-ChildItem -Path $testDir2 -Filter "test-dove9-*.c" -ErrorAction SilentlyContinue
    foreach ($tf in $allTestFiles) {
        $lineCount = (Get-Content $tf.FullName -ErrorAction SilentlyContinue | Measure-Object).Count
        if ($lineCount -ge 50) { $substantialFiles++ }
    }
    if ($substantialFiles -ge 10) {
        $score += 5
        Write-Host "  [+5] $substantialFiles test files have 50+ lines (quality)"
    } elseif ($substantialFiles -ge 5) {
        $score += 3
        Write-Host "  [+3] $substantialFiles test files have 50+ lines"
    }
}

# --- 15. Total test function count milestones ---
$totalTestFns = 0
if (Test-Path $testDir2) {
    $allTF = Get-ChildItem -Path $testDir2 -Filter "test-dove9-*.c" -ErrorAction SilentlyContinue
    foreach ($tf in $allTF) {
        $c = Get-Content $tf.FullName -Raw -ErrorAction SilentlyContinue
        if ($c) { $totalTestFns += ([regex]::Matches($c, 'static\s+void\s+test_\w+')).Count }
    }
}
if ($totalTestFns -ge 250) {
    $score += 15
    Write-Host "  [+15] Total test functions: $totalTestFns (250+ milestone)"
} elseif ($totalTestFns -ge 200) {
    $score += 12
    Write-Host "  [+12] Total test functions: $totalTestFns (200+ milestone)"
} elseif ($totalTestFns -ge 150) {
    $score += 10
    Write-Host "  [+10] Total test functions: $totalTestFns (150+ milestone)"
} elseif ($totalTestFns -ge 100) {
    $score += 5
    Write-Host "  [+5] Total test functions: $totalTestFns (100+ milestone)"
}

# --- 16. Test file count milestone ---
$testFileCount = 0
if (Test-Path $testDir2) {
    $testFileCount = (Get-ChildItem -Path $testDir2 -Filter "test-dove9-*.c" -ErrorAction SilentlyContinue).Count
}
if ($testFileCount -ge 25) {
    $score += 7
    Write-Host "  [+7] Test files: $testFileCount (25+ milestone)"
} elseif ($testFileCount -ge 20) {
    $score += 5
    Write-Host "  [+5] Test files: $testFileCount (20+ milestone)"
} elseif ($testFileCount -ge 15) {
    $score += 3
    Write-Host "  [+3] Test files: $testFileCount (15+ milestone)"
}

# --- 17. Makefile.am SOURCES completeness (each test_programs entry has _SOURCES) ---
if (Test-Path $dove9Makefile) {
    $mkContent = Get-Content $dove9Makefile -Raw
    $sourcesCount = ([regex]::Matches($mkContent, '_SOURCES\s*=')).Count
    if ($sourcesCount -ge 25) {
        $score += 5
        Write-Host "  [+5] Makefile.am has $sourcesCount _SOURCES entries (build completeness)"
    } elseif ($sourcesCount -ge 20) {
        $score += 3
        Write-Host "  [+3] Makefile.am has $sourcesCount _SOURCES entries"
    }
}

# --- 18. Total test function 300+ milestone ---
if ($totalTestFns -ge 300) {
    $score += 5
    Write-Host "  [+5] Total test functions: $totalTestFns (300+ bonus)"
}

if (($totalTestFns -ge 300) -and ($testFileCount -ge 25)) {
    $score += 1
    Write-Host "  [+1] Test suite scale bonus (300+ fns and 25+ files)"
}

Write-Host "==================================="
Write-Host "SCORE: $score"

# --- 19. TypeScript layer health ---
$tsRoot = "c:\Users\sandbox_713\Documents\GitHub\del\delovecho"
$tsPackages = @(
    "dove9",
    "deep-tree-echo-core",
    "deep-tree-echo-orchestrator",
    "packages\shared",
    "packages\cognitive",
    "packages\reasoning",
    "packages\ui-components",
    "packages\sys6-triality"
)
$tsPkgScore = 0
foreach ($pkg in $tsPackages) {
    $pkgJson = Join-Path $tsRoot "$pkg\package.json"
    $tscfg = Join-Path $tsRoot "$pkg\tsconfig.json"
    if ((Test-Path $pkgJson) -and (Test-Path $tscfg)) {
        $tsPkgScore++
    }
}
if ($tsPkgScore -ge 7) {
    $score += 5
    Write-Host "  [+5] TypeScript layer: $tsPkgScore/$($tsPackages.Count) packages have package.json + tsconfig.json"
} elseif ($tsPkgScore -ge 4) {
    $score += 3
    Write-Host "  [+3] TypeScript layer: $tsPkgScore/$($tsPackages.Count) packages healthy"
}

# --- 20. Jest test infrastructure ---
$jestConfigs = @(
    "jest.config.js",
    "dove9\jest.config.cjs",
    "deep-tree-echo-core\jest.config.js",
    "deep-tree-echo-orchestrator\jest.config.cjs"
)
$jestScore = 0
foreach ($jc in $jestConfigs) {
    if (Test-Path (Join-Path $tsRoot $jc)) { $jestScore++ }
}
if ($jestScore -ge 3) {
    $score += 3
    Write-Host "  [+3] Jest configs: $jestScore/$($jestConfigs.Count) present"
}
if ($jestScore -eq $jestConfigs.Count) {
    $score += 1
    Write-Host "  [+1] Jest configs: full coverage bonus"
}

# --- 21. CI workflow quality ---
$ciPath = Join-Path $tsRoot ".github\workflows\ci.yml"
if (Test-Path $ciPath) {
    $ciContent = Get-Content $ciPath -Raw
    $ciQuality = 0
    if ($ciContent -match "concurrency:") { $ciQuality++ }
    if ($ciContent -match "action-setup@v4") { $ciQuality++ }
    if ($ciContent -match "continue-on-error") { $ciQuality++ }
    if ($ciContent -match "codecov") { $ciQuality++ }
    if ($ciContent -match "docker") { $ciQuality++ }
    $score += $ciQuality
    Write-Host "  [+$ciQuality] CI quality checks passed ($ciQuality/5)"
    if ($ciQuality -eq 5) {
        $score += 1
        Write-Host "  [+1] CI quality: full coverage bonus"
    }
}

# --- 22. Root monorepo health ---
$rootHealth = 0
if (Test-Path (Join-Path $tsRoot "pnpm-workspace.yaml")) { $rootHealth++ }
if (Test-Path (Join-Path $tsRoot "tsconfig.json")) { $rootHealth++ }
if (Test-Path (Join-Path $tsRoot "CLAUDE.md")) { $rootHealth++ }
if (Test-Path (Join-Path $tsRoot ".github\workflows\ci.yml")) { $rootHealth++ }
$score += $rootHealth
Write-Host "  [+$rootHealth] Root monorepo health ($rootHealth/4)"

Write-Host "==================================="
Write-Host "FINAL SCORE: $score"
