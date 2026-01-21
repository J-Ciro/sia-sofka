import path from 'path'
import { fileURLToPath } from 'url'
import { test, expect } from '../fixtures/auth.js'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const fixtureValid = path.resolve(__dirname, '../fixtures/estudiantes_validos.xlsx')

test.describe('Bulk Import/Export Excel (Admin)', () => {
  test('Admin abre Importar Excel y ve Descargar plantilla y Exportar', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/users')
    await authenticatedPage.click('button:has-text("Importar Excel")')
    await expect(authenticatedPage.locator('text=Importar / Exportar Excel')).toBeVisible()
    await expect(authenticatedPage.locator('text=Descargar plantilla')).toBeVisible()
    await expect(authenticatedPage.locator('text=Exportar usuarios')).toBeVisible()
  })

  test('Admin descarga plantilla al hacer clic en Descargar plantilla', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/users')
    await authenticatedPage.click('button:has-text("Importar Excel")')
    const [download] = await Promise.all([
      authenticatedPage.waitForEvent('download'),
      authenticatedPage.click('button:has-text("Descargar plantilla")'),
    ])
    expect(download.suggestedFilename()).toMatch(/plantilla.*\.xlsx$/i)
  })

  test('Admin exporta usuarios al hacer clic en Exportar usuarios', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/users')
    await authenticatedPage.click('button:has-text("Importar Excel")')
    const [download] = await Promise.all([
      authenticatedPage.waitForEvent('download'),
      authenticatedPage.click('button:has-text("Exportar usuarios")'),
    ])
    expect(download.suggestedFilename()).toMatch(/\.xlsx$/i)
  })

  test('Admin importa Excel válido y ve resultado', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/users')
    await authenticatedPage.click('button:has-text("Importar Excel")')
    await authenticatedPage.setInputFiles('input[type="file"][accept=".xlsx"]', fixtureValid)
    await authenticatedPage.click('button:has-text("Importar"):not(:has-text("Exportar"))')
    await expect(authenticatedPage.locator('text=Resultado')).toBeVisible({ timeout: 10000 })
    await expect(authenticatedPage.locator('text=creados')).toBeVisible()
  })
})
