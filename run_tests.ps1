# run_tests.ps1 — Ejecuta todas las pruebas unitarias organizadas por tipo

$ROOT    = $PSScriptRoot
$BACKEND = Join-Path $ROOT "backend"
$FRONTEND= Join-Path $ROOT "frontend"
$PYTHON  = Join-Path $BACKEND ".venv\Scripts\python.exe"

$UNIT_TESTS = @(
    "tests/test_security.py",
    "tests/test_expression_normalizer.py",
    "tests/test_llm_text.py",
    "tests/test_math_parser_functions.py",
    "tests/test_extract_student_answer.py",
    "tests/test_math_answer_functions.py",
    "tests/test_practice_state.py"
)

$failed = $false

function Write-Header($text) {
    Write-Host ""
    Write-Host ("=" * 48) -ForegroundColor Cyan
    Write-Host ("  " + $text) -ForegroundColor Cyan
    Write-Host ("=" * 48) -ForegroundColor Cyan
}

function Run-Pytest($label, $filter, $files) {
    Write-Host ""
    Write-Host "-------- $label --------" -ForegroundColor Yellow
    Push-Location $BACKEND
    & $PYTHON -m pytest @files -k $filter -v --tb=short --no-header -q 2>&1
    if ($LASTEXITCODE -ne 0) { $script:failed = $true }
    Pop-Location
}

function Run-Vitest($label, $script) {
    Write-Host ""
    Write-Host "-------- $label --------" -ForegroundColor Yellow
    Push-Location $FRONTEND
    & pnpm run $script 2>&1
    if ($LASTEXITCODE -ne 0) { $script:failed = $true }
    Pop-Location
}

# ══════════════════════════════════════════════════
#  BACKEND
# ══════════════════════════════════════════════════
Write-Header "BACKEND  (pytest)"

if (-not (Test-Path $PYTHON)) {
    Write-Host "ERROR: venv no encontrado en $PYTHON" -ForegroundColor Red
    Write-Host "Ejecuta: cd backend && python -m venv .venv && .venv\Scripts\pip install -r requirements.txt" -ForegroundColor Yellow
    $failed = $true
} else {
    Run-Pytest "Casos Normales"  "TestNormal"  $UNIT_TESTS
    Run-Pytest "Casos Limite"    "TestLimite"  $UNIT_TESTS
    Run-Pytest "Casos Erroneos"  "TestError"   $UNIT_TESTS
}

# ══════════════════════════════════════════════════
#  FRONTEND
# ══════════════════════════════════════════════════
Write-Header "FRONTEND  (vitest)"

$pnpm = Get-Command pnpm -ErrorAction SilentlyContinue
if (-not $pnpm) {
    Write-Host "ERROR: pnpm no encontrado." -ForegroundColor Red
    $failed = $true
} else {
    Run-Vitest "Casos Normales"  "test:normal"
    Run-Vitest "Casos Limite"    "test:limite"
    Run-Vitest "Casos Erroneos"  "test:error"
}

# ══════════════════════════════════════════════════
#  RESUMEN
# ══════════════════════════════════════════════════
Write-Header "RESUMEN"
if (-not $failed) {
    Write-Host "  Todas las pruebas: PASSED" -ForegroundColor Green
} else {
    Write-Host "  Algunas pruebas:   FAILED" -ForegroundColor Red
}
Write-Host ""

if ($failed) { exit 1 }
exit 0
