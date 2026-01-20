# 🚀 Quick Start - Playwright Tests

Los tests E2E viven en la carpeta **`e2e/`** en la raíz del proyecto (fuera de `frontend/` y `backend/`).

## Instalación Rápida

```powershell
# Desde la raíz del proyecto
.\e2e\install-playwright.ps1

# O manualmente:
cd e2e
npm install
npx playwright install
```

## Ejecutar Tests

```powershell
cd e2e

# Modo UI (recomendado para desarrollo)
npm run test:e2e:ui

# Headless (para CI/CD)
npm run test:e2e

# Con navegador visible
npm run test:e2e:headed

# Ver reporte
npm run test:e2e:report
```

## Requisitos Previos

1. **Backend corriendo** en `http://localhost:8000`
2. **Frontend corriendo** en `http://localhost:5173`

### Iniciar Backend

```powershell
cd backend
docker-compose up
```

### Iniciar Frontend

```powershell
cd frontend
npm run dev
```

## Tests Incluidos

✅ **46 tests E2E** cubriendo:

- 🔐 Autenticación (login/logout)
- 👥 Gestión de usuarios (CRUD)
- 📚 Gestión de materias (CRUD)
- 📊 Gestión de notas (CRUD)
- 📝 Inscripciones (CRUD)
- 🧭 Navegación y permisos

## Estructura

```
e2e/
├── playwright.config.js          # Configuración
├── package.json
├── tests/
│   ├── e2e/                      # Tests
│   │   ├── auth.spec.js
│   │   ├── users.spec.js
│   │   ├── subjects.spec.js
│   │   ├── grades.spec.js
│   │   ├── enrollments.spec.js
│   │   └── navigation.spec.js
│   └── fixtures/
│       └── auth.js               # Helpers
├── install-playwright.ps1
└── PLAYWRIGHT_GUIDE.md           # Documentación completa
```

## Troubleshooting

### No encuentra selectores?

```powershell
cd e2e
npm run test:e2e:codegen
```

### Tests fallan?

```powershell
cd e2e
npm run test:e2e:debug
```

### Ver qué pasó?

```powershell
cd e2e
npm run test:e2e:report
```

## Siguiente Paso

📖 Lee la [Guía Completa](PLAYWRIGHT_GUIDE.md) para:
- Escribir nuevos tests
- Mejores prácticas
- CI/CD
- Troubleshooting avanzado

## CI/CD

Los tests se ejecutan automáticamente en:
- ✅ Push a `main` o `develop`
- ✅ Pull Requests

Ver configuración en `.github/workflows/playwright.yml`

---

**¿Preguntas?** Consulta [PLAYWRIGHT_GUIDE.md](PLAYWRIGHT_GUIDE.md)
