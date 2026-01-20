# 🎭 Implementación de Playwright - Comando de Instalación
# Ejecutar desde la raíz del proyecto: .\e2e\install-playwright.ps1

$E2ERoot = if ($PSScriptRoot) { $PSScriptRoot } else { "e2e" }
Set-Location $E2ERoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🎭 INSTALACIÓN DE PLAYWRIGHT (E2E)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Instalar dependencias (incluye @playwright/test)
Write-Host "📦 Paso 1: Instalando dependencias (npm install)..." -ForegroundColor Yellow
npm install

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencias instaladas correctamente" -ForegroundColor Green
} else {
    Write-Host "❌ Error instalando dependencias" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 2. Instalar navegadores
Write-Host "🌐 Paso 2: Instalando navegadores (Chrome, Firefox, Safari)..." -ForegroundColor Yellow
npx playwright install

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Navegadores instalados correctamente" -ForegroundColor Green
} else {
    Write-Host "❌ Error instalando navegadores" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ INSTALACIÓN COMPLETADA" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📊 Estructura E2E (e2e/):" -ForegroundColor Cyan
Write-Host "  ✓ playwright.config.js" -ForegroundColor Green
Write-Host "  ✓ tests/e2e/auth.spec.js" -ForegroundColor Green
Write-Host "  ✓ tests/e2e/users.spec.js" -ForegroundColor Green
Write-Host "  ✓ tests/e2e/subjects.spec.js" -ForegroundColor Green
Write-Host "  ✓ tests/e2e/grades.spec.js" -ForegroundColor Green
Write-Host "  ✓ tests/e2e/enrollments.spec.js" -ForegroundColor Green
Write-Host "  ✓ tests/e2e/navigation.spec.js" -ForegroundColor Green
Write-Host "  ✓ tests/fixtures/auth.js" -ForegroundColor Green
Write-Host "  ✓ PLAYWRIGHT_GUIDE.md" -ForegroundColor Green
Write-Host ""

Write-Host "🚀 Comandos (desde la carpeta e2e/):" -ForegroundColor Cyan
Write-Host "  npm run test:e2e          # Ejecutar todos los tests" -ForegroundColor White
Write-Host "  npm run test:e2e:ui       # Modo UI (recomendado)" -ForegroundColor White
Write-Host "  npm run test:e2e:headed   # Ver navegador" -ForegroundColor White
Write-Host "  npm run test:e2e:debug    # Modo debug" -ForegroundColor White
Write-Host "  npm run test:e2e:report   # Ver reporte HTML" -ForegroundColor White
Write-Host "  npm run test:e2e:codegen  # Grabar tests automáticamente" -ForegroundColor White
Write-Host ""

Write-Host "📝 Próximos pasos:" -ForegroundColor Cyan
Write-Host "  1. Asegúrate que el backend esté corriendo (puerto 8000)" -ForegroundColor Yellow
Write-Host "  2. Asegúrate que el frontend esté corriendo (puerto 5173)" -ForegroundColor Yellow
Write-Host "  3. Desde e2e/: npm run test:e2e:ui" -ForegroundColor Yellow
Write-Host ""

Write-Host "📖 Documentación completa en: e2e/PLAYWRIGHT_GUIDE.md" -ForegroundColor Cyan
Write-Host ""
