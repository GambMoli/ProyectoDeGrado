# run_integration_tests.ps1 -- Pruebas de integracion agrupadas por escenario
#
# Cobertura CI:
#   CI-01..05   test_auth_service.py
#   CI-06..08   test_tutor_agent_service / test_conversation_orchestrator_service
#               test_conversation_planner_service
#   CI-12..13   test_math_services.py
#   CI-14..16   test_practice_service.py
#   CI-17       test_knowledge_base_service.py
#   CI-18       test_response_composer_service.py
#   CI-19..21   test_reports_service.py
#   CI-22..23   frontend/src/api/__tests__/client.test.ts

$ROOT    = $PSScriptRoot
$BACKEND = Join-Path $ROOT "backend"
$FRONTEND= Join-Path $ROOT "frontend"
$PYTHON  = Join-Path $BACKEND ".venv\Scripts\python.exe"

$INT_TESTS = @(
    "tests/test_auth_service.py",
    "tests/test_tutor_agent_service.py",
    "tests/test_conversation_orchestrator_service.py",
    "tests/test_conversation_planner_service.py",
    "tests/test_math_services.py",
    "tests/test_practice_service.py",
    "tests/test_knowledge_base_service.py",
    "tests/test_response_composer_service.py",
    "tests/test_reports_service.py"
)

$FILTER_FLUJO    = "not (falls_back or times_out or revokes or requires_ollama or returns_none or missing or requires_valid or discards)"
$FILTER_ERROR    = "falls_back or times_out or revokes or requires_ollama"
$FILTER_INVALIDO = "returns_none or missing or requires_valid or discards"

$failed = $false

function Write-Header($text) {
    Write-Host ""
    Write-Host ("=" * 56) -ForegroundColor Cyan
    Write-Host ("  " + $text) -ForegroundColor Cyan
    Write-Host ("=" * 56) -ForegroundColor Cyan
}

function Write-CIBlock($ids) {
    Write-Host "  IDs: $ids" -ForegroundColor DarkGray
}

function Run-Pytest($label, $ids, $filter, $files) {
    Write-Host ""
    Write-Host "-------- $label --------" -ForegroundColor Yellow
    Write-CIBlock $ids
    Push-Location $BACKEND
    & $PYTHON -m pytest @files -k $filter -v --tb=short --no-header -q 2>&1
    if ($LASTEXITCODE -ne 0) { $script:failed = $true }
    Pop-Location
}

function Run-Vitest($label, $ids, $script) {
    Write-Host ""
    Write-Host "-------- $label --------" -ForegroundColor Yellow
    Write-CIBlock $ids
    Push-Location $FRONTEND
    & pnpm run $script 2>&1
    if ($LASTEXITCODE -ne 0) { $script:failed = $true }
    Pop-Location
}

# ----------------------------------------------------------
#  BACKEND
# ----------------------------------------------------------
Write-Header "BACKEND -- Integracion (pytest)"

if (-not (Test-Path $PYTHON)) {
    Write-Host "ERROR: venv no encontrado en $PYTHON" -ForegroundColor Red
    Write-Host "Ejecuta: cd backend; python -m venv .venv; .venv\Scripts\pip install -r requirements.txt" -ForegroundColor Yellow
    $failed = $true
} else {

    Run-Pytest `
        "Flujo Correcto" `
        "CI-01 CI-02 CI-04 CI-06 CI-07 CI-12 CI-14 CI-15 CI-17 CI-18 CI-19 CI-20" `
        $FILTER_FLUJO `
        $INT_TESTS

    Run-Pytest `
        "Error Controlado" `
        "CI-05 CI-08 CI-16" `
        $FILTER_ERROR `
        $INT_TESTS

    Run-Pytest `
        "Datos Invalidos" `
        "CI-03 CI-13 CI-21" `
        $FILTER_INVALIDO `
        $INT_TESTS
}

# ----------------------------------------------------------
#  FRONTEND
# ----------------------------------------------------------
Write-Header "FRONTEND -- Integracion (vitest)"

$pnpm = Get-Command pnpm -ErrorAction SilentlyContinue
if (-not $pnpm) {
    Write-Host "ERROR: pnpm no encontrado." -ForegroundColor Red
    $failed = $true
} else {
    Run-Vitest "Flujo Correcto"   "CI-22 CI-23"  "test:normal"
    Run-Vitest "Error Controlado" "CI-22"         "test:error"
    Run-Vitest "Datos Invalidos"  "CI-03 CI-22"   "test:limite"
}

# ----------------------------------------------------------
#  IDs SIN TEST DEDICADO
# ----------------------------------------------------------
Write-Header "COBERTURA -- IDs sin test dedicado"
Write-Host ""
Write-Host "  CI-09  OCR imagen valida - GeminiOCRService" -ForegroundColor DarkYellow
Write-Host "  CI-10  Pipeline OCR - MathParser - Solver" -ForegroundColor DarkYellow
Write-Host "  CI-11  Rotacion de claves Gemini agotadas" -ForegroundColor DarkYellow
Write-Host "  CI-24  Acceso cruzado entre usuarios (403/404)" -ForegroundColor DarkYellow
Write-Host ""
Write-Host "  Estos IDs requieren un archivo de prueba nuevo." -ForegroundColor DarkYellow

# ----------------------------------------------------------
#  RESUMEN
# ----------------------------------------------------------
Write-Header "RESUMEN"
if (-not $failed) {
    Write-Host "  Todas las pruebas de integracion: PASSED" -ForegroundColor Green
} else {
    Write-Host "  Algunas pruebas de integracion:   FAILED" -ForegroundColor Red
}
Write-Host ""

if ($failed) { exit 1 }
exit 0
