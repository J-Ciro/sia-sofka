import path from 'path'
import { fileURLToPath } from 'url'
import { test, expect } from '../fixtures/auth.js'
import { BulkImportPage } from '../pages/BulkImportPage.js'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// Test fixtures - archivos de prueba para diferentes escenarios
const testFiles = {
  valid: path.resolve(__dirname, '../fixtures/estudiantes_validos.xlsx'),
  partial: path.resolve(__dirname, '../fixtures/estudiantes_parcial.xlsx'),
  empty: path.resolve(__dirname, '../fixtures/estudiantes_vacio.xlsx'),
  invalidHeaders: path.resolve(__dirname, '../fixtures/estudiantes_headers_invalidos.xlsx'),
  corrupted: path.resolve(__dirname, '../fixtures/estudiantes_corrupto.xlsx'),
  invalidData: path.resolve(__dirname, '../fixtures/estudiantes_datos_invalidos.xlsx'),
  duplicateEmails: path.resolve(__dirname, '../fixtures/estudiantes_emails_duplicados.xlsx'),
  invalidFile: path.resolve(__dirname, '../fixtures/invalid.txt'),
}

/**
 * Suite de pruebas E2E para Importación/Exportación Masiva de Excel
 * 
 * Cubre las siguientes Historias de Usuario:
 * - HU-01: Descargar Plantilla de Excel
 * - HU-02: Importar Usuarios desde Excel  
 * - HU-03: Validar Datos del Excel Antes de Importar
 * - HU-04: Ver Reporte Detallado de Importación
 * - HU-05: Exportar Usuarios a Excel
 * - HU-06: Validar Límite de Filas en Importación
 * - HU-07: Manejo de Contraseñas en Importación
 * - HU-08: Validar Formato de Archivo
 */
test.describe('🔄 Importación/Exportación Masiva de Excel (Administrador)', () => {
  let bulkImportPage

  test.beforeEach(async ({ authenticatedPage }) => {
    // Inicializar Page Object Model
    bulkImportPage = new BulkImportPage(authenticatedPage)
    
    // Navegar a la página de usuarios y preparar estado limpio
    await bulkImportPage.goto()
    
    // Limpiar estado pero preservar autenticación
    await authenticatedPage.evaluate(() => {
      const keysToKeep = ['token', 'user']
      const storage = { ...localStorage }
      localStorage.clear()
      keysToKeep.forEach(key => {
        if (storage[key]) {
          localStorage.setItem(key, storage[key])
        }
      })
      sessionStorage.clear()
    })
  })

  /**
   * 🎯 CASOS EXITOSOS - Happy Path
   * Cubren las funcionalidades principales cuando todo funciona correctamente
   */
  test.describe('✅ Casos Exitosos - Happy Path', () => {
    
    test('HU-01: Debe mostrar modal con todos los elementos de UI requeridos', async ({ authenticatedPage }) => {
      // Abrir el modal de importación
      await bulkImportPage.openImportModal()
      
      // Verificar todos los elementos del modal
      await bulkImportPage.verifyModalElements()
    })

    test('HU-01: Debe descargar plantilla de Excel exitosamente', async ({ authenticatedPage }) => {
      // Configurar interceptor para simular descarga exitosa
      let downloadTriggered = false
      await authenticatedPage.route('**/api/v1/users/template', async route => {
        if (route.request().method() === 'GET') {
          downloadTriggered = true
          await route.fulfill({
            status: 200,
            headers: {
              'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
              'Content-Disposition': 'attachment; filename=plantilla_estudiantes.xlsx'
            },
            body: Buffer.from('mock excel content')
          })
        } else {
          await route.continue()
        }
      })
      
      // Abrir modal y descargar plantilla
      await bulkImportPage.openImportModal()
      await bulkImportPage.downloadTemplate()
      
      // Verificación
      expect(downloadTriggered).toBe(true)
    })

    test('HU-05: Debe exportar usuarios a Excel exitosamente', async ({ authenticatedPage }) => {
      // Configurar interceptor para simular exportación exitosa
      let exportTriggered = false
      await authenticatedPage.route('**/api/v1/users/export*', async route => {
        if (route.request().method() === 'GET') {
          exportTriggered = true
          await route.fulfill({
            status: 200,
            headers: {
              'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
              'Content-Disposition': 'attachment; filename=usuarios.xlsx'
            },
            body: Buffer.from('mock excel content')
          })
        } else {
          await route.continue()
        }
      })
      
      // Abrir modal y exportar usuarios
      await bulkImportPage.openImportModal()
      await bulkImportPage.exportUsers()
      
      // Verificación
      expect(exportTriggered).toBe(true)
    })

    test('HU-02: Debe importar archivo Excel válido exitosamente', async ({ authenticatedPage }) => {
      // Configurar interceptor para simular respuesta exitosa
      await authenticatedPage.route('**/api/v1/users/bulk-import', async route => {
        if (route.request().method() === 'POST') {
          await route.fulfill({
            status: 200,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              created: 2,
              updated: 0,
              errors: []
            })
          })
        } else {
          await route.continue()
        }
      })
      
      // Ejecutar flujo de importación
      await bulkImportPage.openImportModal()
      await bulkImportPage.uploadFile(testFiles.valid)
      await bulkImportPage.verifyImportButtonEnabled()
      
      const responsePromise = authenticatedPage.waitForResponse('**/api/v1/users/bulk-import')
      await bulkImportPage.clickImport()
      const response = await responsePromise
      
      // Verify response was successful
      expect(response.status()).toBe(200)
      
      // Wait for UI to update after response
      await authenticatedPage.waitForTimeout(1000)
      
      // Verificar resultados
      await bulkImportPage.verifySuccessResult(2, 0)
    })
  })

  /**
   * ⚠️ MANEJO DE ERRORES - Casos de Falla
   * Cubren escenarios donde el sistema debe manejar errores graciosamente
   */
  test.describe('⚠️ Manejo de Errores - Casos de Falla', () => {
    
    test('HU-01: Debe manejar falla en descarga de plantilla', async ({ authenticatedPage }) => {
      // Configurar interceptor para simular falla de red con mensaje específico
      await authenticatedPage.route('**/api/v1/users/template', route => {
        if (route.request().method() === 'GET') {
          route.fulfill({
            status: 500,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ detail: 'Error generando plantilla: Error interno del servidor' })
          })
        } else {
          route.continue()
        }
      })
      
      // Ejecutar flujo con error
      await bulkImportPage.openImportModal()
      
      // Wait for response and UI update
      const responsePromise = authenticatedPage.waitForResponse('**/api/v1/users/template').catch(() => null)
      await bulkImportPage.downloadTemplate()
      await responsePromise
      
      // Wait for error message to appear in UI
      await authenticatedPage.waitForTimeout(1000)
      
      // Verificar mensaje de error específico
      await bulkImportPage.verifyErrorMessage('Error generando plantilla')
    })

    test('HU-05: Debe manejar falla en exportación', async ({ authenticatedPage }) => {
      // Configurar interceptor para simular error del servidor con mensaje específico
      await authenticatedPage.route('**/api/v1/users/export*', route => {
        if (route.request().method() === 'GET') {
          route.fulfill({
            status: 500,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ detail: 'Error en operación de base de datos durante consulta de usuarios' })
          })
        } else {
          route.continue()
        }
      })
      
      // Ejecutar flujo con error
      await bulkImportPage.openImportModal()
      
      // Wait for response and UI update
      const responsePromise = authenticatedPage.waitForResponse('**/api/v1/users/export*').catch(() => null)
      await bulkImportPage.exportUsers()
      await responsePromise
      
      // Wait for error message to appear in UI
      await authenticatedPage.waitForTimeout(1000)
      
      // Verificar mensaje de error específico
      await bulkImportPage.verifyErrorMessage('Error en operación de base de datos durante consulta')
    })

    test('HU-08: Debe rechazar archivo con formato no válido', async ({ authenticatedPage }) => {
      test.setTimeout(60000); // Increase timeout for this test
      // Configurar interceptor para simular error de validación con mensaje específico
      await authenticatedPage.route('**/api/v1/users/bulk-import', async route => {
        if (route.request().method() === 'POST') {
          await route.fulfill({
            status: 400,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ detail: "Archivo 'invalid.txt' no es válido. Solo se aceptan archivos .xlsx" })
          })
        } else {
          await route.continue()
        }
      })
      
      // Ejecutar flujo con archivo inválido
      await bulkImportPage.openImportModal()
      await bulkImportPage.uploadFile(testFiles.invalidFile)
      
      const responsePromise = authenticatedPage.waitForResponse('**/api/v1/users/bulk-import', { timeout: 10000 })
      await bulkImportPage.clickImport()
      const response = await responsePromise
      
      // Verify response was error
      expect(response.status()).toBe(400)
      
      // Wait for error message to appear in UI
      await authenticatedPage.waitForTimeout(1500)
      
      // Verificar rechazo por formato con mensaje específico
      await bulkImportPage.verifyErrorMessage('Solo se aceptan archivos .xlsx')
    })

    test('HU-08: Debe rechazar archivo Excel vacío', async ({ authenticatedPage }) => {
      test.setTimeout(60000); // Increase timeout for this test
      // Configurar interceptor para simular archivo vacío con mensaje específico
      await authenticatedPage.route('**/api/v1/users/bulk-import', async route => {
        if (route.request().method() === 'POST') {
          await route.fulfill({
            status: 400,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ detail: 'El archivo está vacío o no contiene datos para importar' })
          })
        } else {
          await route.continue()
        }
      })
      
      // Ejecutar flujo con archivo vacío
      await bulkImportPage.openImportModal()
      await bulkImportPage.uploadFile(testFiles.empty)
      
      const responsePromise = authenticatedPage.waitForResponse('**/api/v1/users/bulk-import', { timeout: 10000 })
      await bulkImportPage.clickImport()
      const response = await responsePromise
      
      // Verify response was error
      expect(response.status()).toBe(400)
      
      // Wait for error message to appear in UI
      await authenticatedPage.waitForTimeout(1500)
      
      await bulkImportPage.verifyErrorMessage('El archivo está vacío o no contiene datos para importar')
    })

    test('HU-08: Debe rechazar archivo Excel corrupto', async ({ authenticatedPage }) => {
      test.setTimeout(60000); // Increase timeout for this test
      // Configurar interceptor para simular archivo corrupto con mensaje específico
      await authenticatedPage.route('**/api/v1/users/bulk-import', async route => {
        if (route.request().method() === 'POST') {
          await route.fulfill({
            status: 400,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ detail: 'El archivo está corrupto o no se puede leer. Verifique que sea un archivo Excel válido' })
          })
        } else {
          await route.continue()
        }
      })
      
      // Ejecutar flujo con archivo corrupto
      await bulkImportPage.openImportModal()
      await bulkImportPage.uploadFile(testFiles.corrupted)
      
      const responsePromise = authenticatedPage.waitForResponse('**/api/v1/users/bulk-import', { timeout: 10000 })
      await bulkImportPage.clickImport()
      const response = await responsePromise
      
      // Verify response was error
      expect(response.status()).toBe(400)
      
      // Wait for error message to appear in UI
      await authenticatedPage.waitForTimeout(1500)
      
      await bulkImportPage.verifyErrorMessage('El archivo está corrupto o no se puede leer')
    })

    test('HU-03: Debe rechazar archivo con encabezados inválidos', async ({ authenticatedPage }) => {
      test.setTimeout(60000); // Increase timeout for this test
      // Configurar interceptor para simular encabezados inválidos con mensaje específico
      await authenticatedPage.route('**/api/v1/users/bulk-import', async route => {
        if (route.request().method() === 'POST') {
          await route.fulfill({
            status: 400,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ detail: 'Faltan las siguientes columnas obligatorias: email, password, apellido' })
          })
        } else {
          await route.continue()
        }
      })
      
      // Ejecutar flujo con encabezados inválidos
      await bulkImportPage.openImportModal()
      await bulkImportPage.uploadFile(testFiles.invalidHeaders)
      
      const responsePromise = authenticatedPage.waitForResponse('**/api/v1/users/bulk-import', { timeout: 10000 })
      await bulkImportPage.clickImport()
      const response = await responsePromise
      
      // Verify response was error
      expect(response.status()).toBe(400)
      
      // Wait for error message to appear in UI
      await authenticatedPage.waitForTimeout(1500)
      
      await bulkImportPage.verifyErrorMessage('Faltan las siguientes columnas obligatorias')
    })

    test('HU-03: Debe mostrar errores de validación de datos', async ({ authenticatedPage }) => {
      // Configurar interceptor para simular errores de validación
      await authenticatedPage.route('**/api/v1/users/bulk-import', async route => {
        if (route.request().method() === 'POST') {
          await route.fulfill({
            status: 400,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              created: 0,
              updated: 0,
              errors: [
                { row: 2, field: 'email', message: 'Email inválido', value: 'invalid-email' },
                { row: 3, field: 'fecha_nacimiento', message: 'Fecha inválida', value: '2050-01-01' }
              ]
            })
          })
        } else {
          await route.continue()
        }
      })
      
      // Ejecutar flujo de validación
      await bulkImportPage.openImportModal()
      await bulkImportPage.uploadFile(testFiles.invalidData)
      
      const responsePromise = authenticatedPage.waitForResponse('**/api/v1/users/bulk-import')
      await bulkImportPage.clickImport()
      await responsePromise
      
      // Wait for UI to update after response
      await authenticatedPage.waitForTimeout(1000)
      
      // Verificar errores específicos
      await bulkImportPage.verifyValidationErrors(['Email inválido'])
    })

    test('HU-03: Debe detectar emails duplicados en el archivo', async ({ authenticatedPage }) => {
      // Configurar interceptor para simular detección de duplicados
      await authenticatedPage.route('**/api/v1/users/bulk-import', async route => {
        if (route.request().method() === 'POST') {
          await route.fulfill({
            status: 400,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              created: 0,
              updated: 0,
              errors: [
                { row: 2, field: 'email', message: 'Email duplicado dentro del mismo archivo', value: 'duplicate@test.com' },
                { row: 3, field: 'email', message: 'Email duplicado dentro del mismo archivo', value: 'duplicate@test.com' }
              ]
            })
          })
        } else {
          await route.continue()
        }
      })
      
      // Ejecutar flujo de detección de duplicados
      await bulkImportPage.openImportModal()
      await bulkImportPage.uploadFile(testFiles.duplicateEmails)
      
      const responsePromise = authenticatedPage.waitForResponse('**/api/v1/users/bulk-import')
      await bulkImportPage.clickImport()
      await responsePromise
      
      // Wait for UI to update after response
      await authenticatedPage.waitForTimeout(1000)
      
      // Verificar detección de duplicados
      await bulkImportPage.verifyValidationErrors(['Email duplicado'])
    })

    test('HU-04: Debe mostrar éxito parcial con datos mixtos', async ({ authenticatedPage }) => {
      // Configurar interceptor para simular éxito parcial
      await authenticatedPage.route('**/api/v1/users/bulk-import', async route => {
        if (route.request().method() === 'POST') {
          await route.fulfill({
            status: 200,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              created: 1,
              updated: 0,
              errors: [
                { row: 3, field: 'email', message: 'Email inválido', value: 'invalid-email' }
              ]
            })
          })
        } else {
          await route.continue()
        }
      })
      
      // Ejecutar flujo de importación parcial
      await bulkImportPage.openImportModal()
      await bulkImportPage.uploadFile(testFiles.partial)
      
      const responsePromise = authenticatedPage.waitForResponse('**/api/v1/users/bulk-import')
      await bulkImportPage.clickImport()
      await responsePromise
      
      // Wait for UI to update after response
      await authenticatedPage.waitForTimeout(1000)
      
      // Verificar éxito parcial
      await bulkImportPage.verifyPartialSuccess(1, 1)
    })

    test('HU-08: Debe manejar error del servidor durante importación', async ({ authenticatedPage }) => {
      // Configurar interceptor para simular error del servidor
      await authenticatedPage.route('**/api/v1/users/bulk-import', route => {
        if (route.request().method() === 'POST') {
          route.fulfill({
            status: 500,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ detail: 'Internal server error' })
          })
        } else {
          route.continue()
        }
      })
      
      // Ejecutar flujo con error del servidor
      await bulkImportPage.openImportModal()
      await bulkImportPage.uploadFile(testFiles.valid)
      
      const responsePromise = authenticatedPage.waitForResponse('**/api/v1/users/bulk-import')
      await bulkImportPage.clickImport()
      await responsePromise
      
      // Wait for error message to appear in UI
      await authenticatedPage.waitForTimeout(1000)
      
      // Verificar mensaje de error (debe existir algún mensaje de error)
      await bulkImportPage.verifyErrorMessage('Internal server error')
    })

    test('HU-06: Debe mostrar estado de procesamiento durante timeout', async ({ authenticatedPage }) => {
      // Configurar interceptor para simular timeout (nunca responde)
      await authenticatedPage.route('**/api/v1/users/bulk-import', () => {
        return new Promise(() => {}) // Never resolves
      })
      
      // Ejecutar flujo hasta timeout
      await bulkImportPage.openImportModal()
      await bulkImportPage.uploadFile(testFiles.valid)
      await bulkImportPage.clickImport()
      
      // Verificar estado de procesamiento
      await bulkImportPage.verifyProcessingState()
    })
  })

  /**
   * 🎨 VALIDACIÓN DE INTERFAZ DE USUARIO
   * Pruebas enfocadas en la interacción y comportamiento de la UI
   */
  test.describe('🎨 Validación de Interfaz de Usuario', () => {
    
    test('HU-02: Botón Importar debe estar deshabilitado sin archivo', async ({ authenticatedPage }) => {
      // Abrir modal y verificar estado inicial del botón
      await bulkImportPage.openImportModal()
      await bulkImportPage.verifyImportButtonDisabled()
    })

    test('HU-02: Botón Importar debe habilitarse después de seleccionar archivo', async ({ authenticatedPage }) => {
      // Abrir modal y seleccionar archivo
      await bulkImportPage.openImportModal()
      await bulkImportPage.uploadFile(testFiles.valid)
      
      // Verificar habilitación del botón
      await bulkImportPage.verifyImportButtonEnabled()
    })

    test('HU-01: Modal debe cerrarse con botón X', async ({ authenticatedPage }) => {
      // Abrir modal y cerrar con X
      await bulkImportPage.openImportModal()
      await bulkImportPage.closeModalWithX()
      
      // Verificar cierre
      await bulkImportPage.verifyModalClosed()
    })

    test('HU-01: Modal debe cerrarse con botón Cerrar', async ({ authenticatedPage }) => {
      // Abrir modal y cerrar con botón Cerrar
      await bulkImportPage.openImportModal()
      await bulkImportPage.closeModalWithButton()
      
      // Verificar cierre
      await bulkImportPage.verifyModalClosed()
    })

    test('HU-02: Debe reiniciar selección de archivo al reabrir modal', async ({ authenticatedPage }) => {
      // Abrir modal y seleccionar archivo
      await bulkImportPage.openImportModal()
      await bulkImportPage.uploadFile(testFiles.valid)
      
      // Cerrar modal
      await bulkImportPage.closeModalWithButton()
      
      // Reabrir modal
      await bulkImportPage.openImportModal()
      
      // Verificar estado reiniciado
      await bulkImportPage.verifyImportButtonDisabled()
    })
  })

  /**
   * 🔬 CASOS LÍMITE Y CONDICIONES ESPECIALES
   * Pruebas de escenarios extremos y condiciones de borde
   */
  test.describe('🔬 Casos Límite y Condiciones Especiales', () => {
    
    test('HU-06: Debe rechazar archivo que excede límite de tamaño', async ({ authenticatedPage }) => {
      // Configurar interceptor para simular archivo muy grande con mensaje específico
      await authenticatedPage.route('**/api/v1/users/bulk-import', route => {
        if (route.request().method() === 'POST') {
          route.fulfill({
            status: 400,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ detail: 'El archivo (7.2 MB) supera el límite máximo de 5 MB' })
          })
        } else {
          route.continue()
        }
      })
      
      // Ejecutar flujo con archivo grande
      await bulkImportPage.openImportModal()
      await bulkImportPage.uploadFile(testFiles.valid) // Simular archivo grande
      
      const responsePromise = authenticatedPage.waitForResponse('**/api/v1/users/bulk-import', { timeout: 10000 })
      await bulkImportPage.clickImport()
      const response = await responsePromise
      
      // Verify response was error
      expect(response.status()).toBe(400)
      
      // Wait for error message to appear in UI
      await authenticatedPage.waitForTimeout(1500)
      
      await bulkImportPage.verifyErrorMessage('El archivo (7.2 MB) supera el límite máximo de 5 MB')
    })

    test('HU-06: Debe rechazar archivo con demasiadas filas', async ({ authenticatedPage }) => {
      test.setTimeout(60000); // Increase timeout for this test
      // Configurar interceptor para simular archivo con muchas filas
      await authenticatedPage.route('**/api/v1/users/bulk-import', route => {
        if (route.request().method() === 'POST') {
          route.fulfill({
            status: 400,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ detail: 'El archivo contiene 1500 filas, pero el límite máximo es 1000 filas por importación' })
          })
        } else {
          route.continue()
        }
      })
      
      // Ejecutar flujo con archivo con muchas filas
      await bulkImportPage.openImportModal()
      await bulkImportPage.uploadFile(testFiles.valid) // Simular archivo con muchas filas
      
      const responsePromise = authenticatedPage.waitForResponse('**/api/v1/users/bulk-import', { timeout: 10000 })
      await bulkImportPage.clickImport()
      const response = await responsePromise
      
      // Verify response was error
      expect(response.status()).toBe(400)
      
      // Wait for error message to appear in UI
      await authenticatedPage.waitForTimeout(1500)
      
      await bulkImportPage.verifyErrorMessage('El archivo contiene 1500 filas, pero el límite máximo es 1000')
    })

    test('HU-08: Debe manejar error del servidor durante importación (duplicate)', async ({ authenticatedPage }) => {
      // Configurar interceptor para simular error del servidor con mensaje específico
      await authenticatedPage.route('**/api/v1/users/bulk-import', route => {
        if (route.request().method() === 'POST') {
          route.fulfill({
            status: 500,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ detail: 'Error en operación de base de datos durante importación masiva' })
          })
        } else {
          route.continue()
        }
      })
      
      // Ejecutar flujo con error del servidor
      await bulkImportPage.openImportModal()
      await bulkImportPage.uploadFile(testFiles.valid)
      
      const responsePromise = authenticatedPage.waitForResponse('**/api/v1/users/bulk-import')
      await bulkImportPage.clickImport()
      await responsePromise
      
      // Wait for error message to appear in UI
      await authenticatedPage.waitForTimeout(1000)
      
      await bulkImportPage.verifyErrorMessage('Error en operación de base de datos durante importación')
    })
  })
})