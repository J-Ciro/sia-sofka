# 🎭 Playwright Testing Guide - SIA SOFKA

Los tests E2E están en la carpeta **`e2e/`** en la raíz del proyecto.

## 📋 Tabla de Contenido

1. [Instalación](#instalación)
2. [Configuración](#configuración)
3. [Ejecutar Tests](#ejecutar-tests)
4. [Estructura de Tests](#estructura-de-tests)
5. [Escribir Tests](#escribir-tests)
6. [CI/CD](#cicd)
7. [Troubleshooting](#troubleshooting)

## 📦 Instalación

### 1. Instalar dependencias

```powershell
cd e2e
npm install
```

### 2. Instalar Navegadores

```powershell
cd e2e
npx playwright install
```

O desde la raíz: `.\e2e\install-playwright.ps1`

Esto instalará:
- ✅ Chromium (Chrome/Edge)
- ✅ Firefox
- ✅ WebKit (Safari)

### 3. Verificar Instalación

```powershell
cd e2e
npx playwright --version
```

## ⚙️ Configuración

### Archivo de Configuración: `e2e/playwright.config.js`

- **Base URL**: http://localhost:5173 (frontend Vite)
- **API URL**: http://localhost:8000 (backend FastAPI)
- **Timeout**: 30 segundos
- **Retries**: 2 (solo en CI)
- **Screenshots**: Solo en fallos
- **Videos**: Solo en fallos

### Variables de Entorno

```powershell
$env:BASE_URL="http://localhost:5173"
$env:API_URL="http://localhost:8000"
cd e2e
npm run test:e2e
```

## 🚀 Ejecutar Tests

### Comandos (desde `e2e/`)

```powershell
cd e2e

# Headless
npm run test:e2e

# UI (recomendado para desarrollo)
npm run test:e2e:ui

# Navegador visible
npm run test:e2e:headed

# Test específico
npm run test:e2e auth.spec.js

# Modo debug
npm run test:e2e:debug

# Reporte HTML
npm run test:e2e:report

# Codegen
npm run test:e2e:codegen
# O: npx playwright codegen http://localhost:5173
```

### Navegadores específicos

```powershell
cd e2e
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
npx playwright test --project="Mobile Chrome"
```

### Filtros

```powershell
cd e2e
npx playwright test -g "should login"
npx playwright test tests/e2e/auth.spec.js
npx playwright test tests/e2e/
```

## 📁 Estructura

```
e2e/
├── playwright.config.js
├── package.json
├── tests/
│   ├── e2e/
│   │   ├── auth.spec.js
│   │   ├── users.spec.js
│   │   ├── subjects.spec.js
│   │   ├── grades.spec.js
│   │   ├── enrollments.spec.js
│   │   └── navigation.spec.js
│   └── fixtures/
│       └── auth.js
├── playwright-report/        # generado
└── test-results/             # generado
```

## ✍️ Escribir Tests

### Anatomía

```javascript
import { test, expect } from '../fixtures/auth.js';

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should do something', async ({ page }) => {
    await page.goto('/users');
    await page.click('button:has-text("Crear")');
    await page.fill('input[name="nombre"]', 'Juan');
    await page.click('button[type="submit"]');
    await expect(page.locator('text=Juan')).toBeVisible();
  });
});
```

### Fixtures

- **`authenticatedPage`**: Admin autenticado
- **`profesorPage`**: Profesor autenticado
- **`estudiantePage`**: Estudiante autenticado

## 🔄 CI/CD

El workflow `.github/workflows/playwright.yml`:

- Instala dependencias en `e2e/`
- Ejecuta `npx playwright install --with-deps chromium` en `e2e/`
- Ejecuta `npm run test:e2e -- --project=chromium` desde `e2e/`
- Sube `e2e/playwright-report/` y `e2e/test-results/` como artifacts

## 🐛 Troubleshooting

### Tests fallan aleatoriamente

Aumentar `actionTimeout` en `playwright.config.js` o en el test.

### No encuentra selectores

```powershell
cd e2e
npm run test:e2e:debug
# o
npm run test:e2e:codegen
```

### Backend/Frontend no están corriendo

```powershell
# Terminal 1 - Backend
cd backend && uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend && npm run dev

# Terminal 3 - Tests
cd e2e && npm run test:e2e
```

## 📊 Reportes

```powershell
cd e2e
npm run test:e2e:report
```

## 📝 Tests incluidos

1. **auth.spec.js** – Login, logout, validaciones
2. **users.spec.js** – CRUD usuarios, filtros, búsqueda
3. **subjects.spec.js** – CRUD materias, validaciones
4. **grades.spec.js** – CRUD notas, rango 0–5
5. **enrollments.spec.js** – CRUD inscripciones, duplicados, filtros
6. **navigation.spec.js** – Navegación, permisos, 404

**Total: 46 tests E2E**

---

- [Playwright Docs](https://playwright.dev)
- [Best Practices](https://playwright.dev/docs/best-practices)
