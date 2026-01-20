import { test, expect } from '../fixtures/auth.js';

test.describe('Subject Management (Admin)', () => {
  test('should display subjects list', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/subjects');

    // Wait for subjects to load
    await authenticatedPage.waitForSelector('table, [data-testid="subjects-table"]');

    // Verify content is visible
    await expect(authenticatedPage.locator('table, [data-testid="subjects-table"]')).toBeVisible();
  });

  test('should create a new subject', async ({ profesorPage }) => {
    await profesorPage.goto('/subjects');

    // Click create button
    await profesorPage.click('button:has-text("Crear"), button:has-text("Nueva Materia")');

    // Fill form
    const timestamp = Date.now();
    await profesorPage.fill('input[name="nombre"]', `Materia Test ${timestamp}`);
    await profesorPage.fill('input[name="codigo_institucional"]', `MAT${timestamp}`);
    await profesorPage.fill('input[name="numero_creditos"]', '3');
    await profesorPage.fill('input[name="horario"]', 'Lunes 8:00-10:00');
    await profesorPage.fill('textarea[name="descripcion"]', 'Descripción de prueba');

    // Submit
    await profesorPage.click('button[type="submit"]');

    // Wait for success
    await profesorPage.waitForSelector('text=/creado|éxito|success/i', { timeout: 5000 });

    // Verify subject appears in list
    await expect(profesorPage.locator(`text=Materia Test ${timestamp}`)).toBeVisible();
  });

  test('should edit a subject', async ({ profesorPage }) => {
    await profesorPage.goto('/subjects');

    // Click edit on first subject
    await profesorPage.click('button:has-text("Editar"), [data-action="edit"]').first();

    // Modify fields
    await profesorPage.fill('input[name="horario"]', 'Martes 10:00-12:00');
    await profesorPage.fill('input[name="numero_creditos"]', '4');

    // Save
    await profesorPage.click('button[type="submit"]');

    // Verify success
    await profesorPage.waitForSelector('text=/actualizado|éxito|success/i', { timeout: 5000 });
  });

  test('should delete a subject', async ({ profesorPage }) => {
    await profesorPage.goto('/subjects');

    // Get current count
    const initialCount = await profesorPage.locator('table tbody tr').count();

    // Click delete on last subject
    await profesorPage.click('button:has-text("Eliminar"), [data-action="delete"]').last();

    // Confirm deletion
    await profesorPage.click('button:has-text("Confirmar"), button:has-text("Sí")');

    // Wait for success
    await profesorPage.waitForSelector('text=/eliminado|éxito|success/i', { timeout: 5000 });

    // Verify count decreased
    const finalCount = await profesorPage.locator('table tbody tr').count();
    expect(finalCount).toBe(initialCount - 1);
  });

  test('should view subject details', async ({ profesorPage }) => {
    await profesorPage.goto('/subjects');

    // Click on first subject name or view button
    await profesorPage.click('table tbody tr:first-child td:first-child a, button:has-text("Ver")').first();

    // Verify detail page is shown
    await expect(profesorPage.locator('h1, h2')).toContainText(/detalle|información|subject/i);
  });

  test('should validate required fields', async ({ profesorPage }) => {
    await profesorPage.goto('/subjects');
    await profesorPage.click('button:has-text("Crear"), button:has-text("Nueva Materia")');

    // Try to submit empty form
    await profesorPage.click('button[type="submit"]');

    // Should show validation errors
    await expect(profesorPage.locator('text=/requerido|obligatorio|required/i')).toBeVisible();
  });

  test('should validate credits range', async ({ profesorPage }) => {
    await profesorPage.goto('/subjects');
    await profesorPage.click('button:has-text("Crear"), button:has-text("Nueva Materia")');

    // Fill form with invalid credits
    await profesorPage.fill('input[name="nombre"]', 'Test Subject');
    await profesorPage.fill('input[name="codigo_institucional"]', 'TEST001');
    await profesorPage.fill('input[name="numero_creditos"]', '0');

    // Try to submit
    await profesorPage.click('button[type="submit"]');

    // Should show validation error
    await expect(profesorPage.locator('text=/créditos.*válido/i')).toBeVisible();
  });
});
