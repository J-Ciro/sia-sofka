#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Script para ejecutar tests E2E específicos del sistema de horarios y calendario
    
.DESCRIPTION
    Este script facilita la ejecución de tests E2E para las historias de usuario
    del sistema de horarios y calendario (HU-01 a HU-10).
    
    Basado en:
    - .github/historias-usuario/hu-horarios-calendario.md
    - .github/plan/feature-horarios-calendario-1.md
    
.PARAMETER TestType
    Tipo de test a ejecutar: all, hu01, hu02, hu03, hu04, hu05, hu06, hu07, hu08, hu09, hu10, edge
    
.PARAMETER Mode
    Modo de ejecución: headless, headed, ui, debug
    
.PARAMETER Browser
    Navegador a usar: chromium, firefox, webkit
    
.EXAMPLE
    .\run-schedule-tests.ps1 -TestType all -Mode headless
    Ejecuta todos los tests de horarios en modo headless
    
.EXAMPLE
    .\run-schedule-tests.ps1 -TestType hu01 -Mode ui
    Ejecuta solo los tests de HU-01 (Crear Horario) con interfaz visual
    
.EXAMPLE
    .\run-schedule-tests.ps1 -TestType edge -Mode debug
    Ejecuta solo los edge cases en modo debug
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("all", "hu01", "hu02", "hu03", "hu04", "hu05", "hu06", "hu07", "hu08", "hu09", "hu10", "edge", "conflicts", "calendar", "filters")]
    [string]$TestType = "all",
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("headless", "headed", "ui", "debug")]
    [string]$Mode = "headless",
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("chromium", "firefox", "webkit")]
    [string]$Browser = "chromium"
)

# Colores para output
$Green = "`e[32m"
$Yellow = "`e[33m"
$Red = "`e[31m"
$Blue = "`e[34m"
$Reset = "`e[0m"

function Write-ColorOutput {
    param($Message, $Color)
    Write-Host "$Color$Message$Reset"
}

function Show-Header {
    Write-ColorOutput "🗓️  SIA SOFKA - Tests E2E de Horarios y Calendario" $Blue
    Write-ColorOutput "=================================================" $Blue
    Write-ColorOutput "Tipo de Test: $TestType" $Yellow
    Write-ColorOutput "Modo: $Mode" $Yellow
    Write-ColorOutput "Navegador: $Browser" $Yellow
    Write-ColorOutput "" $Reset
}

function Get-TestCommand {
    param($TestPattern, $TestMode, $TestBrowser)
    
    $baseCommand = "npx playwright test schedules.spec.js"
    
    # Agregar patrón de test específico
    if ($TestPattern -ne "all") {
        $baseCommand += " -g `"$TestPattern`""
    }
    
    # Agregar configuración de modo
    switch ($TestMode) {
        "headed" { $baseCommand += " --headed" }
        "ui" { $baseCommand += " --ui" }
        "debug" { $baseCommand += " --debug" }
    }
    
    # Agregar navegador específico
    if ($TestBrowser -ne "chromium") {
        $baseCommand += " --project=$TestBrowser"
    }
    
    return $baseCommand
}

function Get-TestPattern {
    param($Type)
    
    switch ($Type) {
        "hu01" { return "HU-01: Crear Horario de Clase" }
        "hu02" { return "HU-02: Validar Conflictos de Salón" }
        "hu03" { return "HU-03: Validar Conflictos de Profesor" }
        "hu04" { return "HU-04: Editar Horario Existente" }
        "hu05" { return "HU-05: Eliminar Horario" }
        "hu06" { return "HU-06: Visualizar Calendario Semanal" }
        "hu07" { return "HU-07: Filtrar Horarios en Calendario" }
        "hu08" { return "HU-08: Ver Detalle de Horario desde Calendario" }
        "hu09" { return "HU-09: Exportar Horarios a PDF" }
        "hu10" { return "HU-10: Notificar Cambios de Horario" }
        "edge" { return "Edge Cases y Validaciones Críticas" }
        "conflicts" { return "Validar Conflictos" }
        "calendar" { return "Calendario" }
        "filters" { return "Filtrar" }
        default { return "all" }
    }
}

function Show-TestInfo {
    param($Type)
    
    Write-ColorOutput "📋 Información del Test:" $Blue
    
    switch ($Type) {
        "hu01" {
            Write-ColorOutput "• HU-01: Crear Horario de Clase" $Green
            Write-ColorOutput "  - Escenario 1: Crear horario exitosamente sin conflictos" $Reset
            Write-ColorOutput "  - Escenario 2: Validación de hora fin posterior a hora inicio" $Reset
            Write-ColorOutput "  - Escenario 3: Validación de duración mínima y máxima" $Reset
        }
        "hu02" {
            Write-ColorOutput "• HU-02: Validar Conflictos de Salón" $Green
            Write-ColorOutput "  - Escenario 1: Detectar conflicto de salón" $Reset
            Write-ColorOutput "  - Escenario 2: Horarios consecutivos sin conflicto" $Reset
            Write-ColorOutput "  - Escenario 3: Salones diferentes sin conflicto" $Reset
        }
        "hu06" {
            Write-ColorOutput "• HU-06: Visualizar Calendario Semanal" $Green
            Write-ColorOutput "  - Escenario 1: Ver calendario con horarios" $Reset
            Write-ColorOutput "  - Escenario 2: Clases superpuestas visualmente distinguibles" $Reset
            Write-ColorOutput "  - Escenario 3: Navegación entre semanas" $Reset
        }
        "edge" {
            Write-ColorOutput "• Edge Cases y Validaciones Críticas" $Green
            Write-ColorOutput "  - Validación de horario límite (23:59)" $Reset
            Write-ColorOutput "  - Validación de horario límite (00:00)" $Reset
            Write-ColorOutput "  - Performance con muchos horarios" $Reset
            Write-ColorOutput "  - Validación de campos obligatorios" $Reset
        }
        "all" {
            Write-ColorOutput "• Ejecutando TODOS los tests de horarios (HU-01 a HU-10 + Edge Cases)" $Green
            Write-ColorOutput "  - Total: ~40 tests individuales" $Reset
            Write-ColorOutput "  - Tiempo estimado: 15-25 minutos" $Reset
        }
    }
    Write-ColorOutput "" $Reset
}

function Check-Prerequisites {
    Write-ColorOutput "🔍 Verificando prerequisitos..." $Yellow
    
    # Verificar que estamos en el directorio correcto
    if (-not (Test-Path "package.json")) {
        Write-ColorOutput "❌ Error: No se encontró package.json. Ejecute desde el directorio e2e/" $Red
        exit 1
    }
    
    # Verificar que existe el archivo de tests
    if (-not (Test-Path "tests/e2e/schedules.spec.js")) {
        Write-ColorOutput "❌ Error: No se encontró schedules.spec.js" $Red
        exit 1
    }
    
    # Verificar que existe el Page Object
    if (-not (Test-Path "tests/pages/SchedulePage.js")) {
        Write-ColorOutput "❌ Error: No se encontró SchedulePage.js" $Red
        exit 1
    }
    
    Write-ColorOutput "✅ Prerequisitos verificados" $Green
    Write-ColorOutput "" $Reset
}

function Show-PostTestInfo {
    Write-ColorOutput "" $Reset
    Write-ColorOutput "📊 Información Post-Test:" $Blue
    Write-ColorOutput "• Reporte HTML: ./playwright-report/index.html" $Reset
    Write-ColorOutput "• Resultados JSON: ./playwright-results.json" $Reset
    Write-ColorOutput "• Screenshots (si hay fallos): ./test-results/" $Reset
    Write-ColorOutput "" $Reset
    
    Write-ColorOutput "🔧 Comandos útiles:" $Blue
    Write-ColorOutput "• Ver reporte: npx playwright show-report" $Reset
    Write-ColorOutput "• Ejecutar test específico: npx playwright test schedules.spec.js -g 'nombre del test'" $Reset
    Write-ColorOutput "• Modo debug: npx playwright test schedules.spec.js --debug" $Reset
    Write-ColorOutput "• Generar código: npx playwright codegen http://localhost:3000" $Reset
    Write-ColorOutput "" $Reset
    
    Write-ColorOutput "📚 Documentación:" $Blue
    Write-ColorOutput "• HU Mapping: ./tests/docs/schedule-hu-test-mapping.md" $Reset
    Write-ColorOutput "• Historias Usuario: ../.github/historias-usuario/hu-horarios-calendario.md" $Reset
    Write-ColorOutput "• Plan Implementación: ../.github/plan/feature-horarios-calendario-1.md" $Reset
}

# Función principal
function Main {
    Show-Header
    Check-Prerequisites
    Show-TestInfo $TestType
    
    $testPattern = Get-TestPattern $TestType
    $command = Get-TestCommand $testPattern $Mode $Browser
    
    Write-ColorOutput "🚀 Ejecutando comando:" $Yellow
    Write-ColorOutput "$command" $Reset
    Write-ColorOutput "" $Reset
    
    # Ejecutar el comando
    try {
        Invoke-Expression $command
        $exitCode = $LASTEXITCODE
        
        if ($exitCode -eq 0) {
            Write-ColorOutput "✅ Tests completados exitosamente!" $Green
        } else {
            Write-ColorOutput "❌ Algunos tests fallaron (código de salida: $exitCode)" $Red
        }
    }
    catch {
        Write-ColorOutput "❌ Error ejecutando tests: $_" $Red
        $exitCode = 1
    }
    
    Show-PostTestInfo
    exit $exitCode
}

# Mostrar ayuda si se solicita
if ($args -contains "--help" -or $args -contains "-h") {
    Write-ColorOutput "🗓️  SIA SOFKA - Tests E2E de Horarios y Calendario" $Blue
    Write-ColorOutput "=================================================" $Blue
    Write-ColorOutput "" $Reset
    Write-ColorOutput "Uso: .\run-schedule-tests.ps1 [-TestType <tipo>] [-Mode <modo>] [-Browser <navegador>]" $Reset
    Write-ColorOutput "" $Reset
    Write-ColorOutput "Tipos de Test:" $Yellow
    Write-ColorOutput "  all      - Todos los tests (por defecto)" $Reset
    Write-ColorOutput "  hu01     - HU-01: Crear Horario de Clase" $Reset
    Write-ColorOutput "  hu02     - HU-02: Validar Conflictos de Salón" $Reset
    Write-ColorOutput "  hu03     - HU-03: Validar Conflictos de Profesor" $Reset
    Write-ColorOutput "  hu04     - HU-04: Editar Horario Existente" $Reset
    Write-ColorOutput "  hu05     - HU-05: Eliminar Horario" $Reset
    Write-ColorOutput "  hu06     - HU-06: Visualizar Calendario Semanal" $Reset
    Write-ColorOutput "  hu07     - HU-07: Filtrar Horarios en Calendario" $Reset
    Write-ColorOutput "  hu08     - HU-08: Ver Detalle de Horario desde Calendario" $Reset
    Write-ColorOutput "  hu09     - HU-09: Exportar Horarios a PDF" $Reset
    Write-ColorOutput "  hu10     - HU-10: Notificar Cambios de Horario" $Reset
    Write-ColorOutput "  edge     - Edge Cases y Validaciones Críticas" $Reset
    Write-ColorOutput "  conflicts- Tests de conflictos (HU-02 + HU-03)" $Reset
    Write-ColorOutput "  calendar - Tests de calendario (HU-06 + HU-07 + HU-08)" $Reset
    Write-ColorOutput "  filters  - Tests de filtros (HU-07)" $Reset
    Write-ColorOutput "" $Reset
    Write-ColorOutput "Modos:" $Yellow
    Write-ColorOutput "  headless - Sin interfaz gráfica (por defecto)" $Reset
    Write-ColorOutput "  headed   - Con interfaz gráfica" $Reset
    Write-ColorOutput "  ui       - Interfaz de Playwright" $Reset
    Write-ColorOutput "  debug    - Modo debug paso a paso" $Reset
    Write-ColorOutput "" $Reset
    Write-ColorOutput "Navegadores:" $Yellow
    Write-ColorOutput "  chromium - Google Chrome (por defecto)" $Reset
    Write-ColorOutput "  firefox  - Mozilla Firefox" $Reset
    Write-ColorOutput "  webkit   - Safari" $Reset
    Write-ColorOutput "" $Reset
    Write-ColorOutput "Ejemplos:" $Yellow
    Write-ColorOutput "  .\run-schedule-tests.ps1" $Reset
    Write-ColorOutput "  .\run-schedule-tests.ps1 -TestType hu01 -Mode ui" $Reset
    Write-ColorOutput "  .\run-schedule-tests.ps1 -TestType conflicts -Mode headed" $Reset
    Write-ColorOutput "  .\run-schedule-tests.ps1 -TestType all -Mode headless -Browser firefox" $Reset
    exit 0
}

# Ejecutar función principal
Main