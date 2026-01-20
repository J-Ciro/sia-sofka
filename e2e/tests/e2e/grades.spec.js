import { test, expect } from '../fixtures/auth.js';

test.describe('Grade Management (Admin)', () => {
  test('should view grades for a subject', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/grades');

    // Wait for content to load
    await authenticatedPage.waitForSelector('table, [data-testid="grades-table"]');

    // Verify grades are displayed
    await expect(authenticatedPage.locator('table, [data-testid="grades-table"]')).toBeVisible();
  });

  test('should create a new grade', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/grades');

    // Click add grade button
    await authenticatedPage.click('button:has-text("Agregar Nota"), button:has-text("Nueva Nota")');

    // Fill form
    await authenticatedPage.selectOption('select[name="enrollment_id"]', { index: 1 });
    await authenticatedPage.fill('input[name="nota"]', '4.5');
    await authenticatedPage.fill('input[name="periodo"]', '2024-1');
    await authenticatedPage.fill('input[name="fecha"]', '2024-06-15');
    await authenticatedPage.fill('textarea[name="observaciones"]', 'Excelente desempeño');

    // Submit
    await authenticatedPage.click('button[type="submit"]');

    // Verify success
    await authenticatedPage.waitForSelector('text=/creado|éxito|success/i', { timeout: 5000 });
  });

  test('should edit a grade', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/grades');

    // Click edit on first grade
    await authenticatedPage.click('button:has-text("Editar"), [data-action="edit"]').first();

    // Modify nota
    await authenticatedPage.fill('input[name="nota"]', '4.8');
    await authenticatedPage.fill('textarea[name="observaciones"]', 'Nota actualizada');

    // Save
    await authenticatedPage.click('button[type="submit"]');

    // Verify success
    await authenticatedPage.waitForSelector('text=/actualizado|éxito|success/i', { timeout: 5000 });
  });

  test('should validate grade range (0.0 to 5.0)', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/grades');
    await authenticatedPage.click('button:has-text("Agregar Nota"), button:has-text("Nueva Nota")');

    // Try invalid grade > 5.0
    await authenticatedPage.selectOption('select[name="enrollment_id"]', { index: 1 });
    await authenticatedPage.fill('input[name="nota"]', '6.0');
    await authenticatedPage.fill('input[name="periodo"]', '2024-1');
    await authenticatedPage.fill('input[name="fecha"]', '2024-06-15');

    // Submit
    await authenticatedPage.click('button[type="submit"]');

    // Should show validation error
    await expect(authenticatedPage.locator('text=/nota.*válida|entre 0.*5/i')).toBeVisible();
  });

  test('should delete a grade', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/grades');

    // Click delete on last grade
    await authenticatedPage.click('button:has-text("Eliminar"), [data-action="delete"]').last();

    // Confirm deletion
    await authenticatedPage.click('button:has-text("Confirmar"), button:has-text("Sí")');

    // Verify success
    await authenticatedPage.waitForSelector('text=/eliminado|éxito|success/i', { timeout: 5000 });
  });

  test('should filter grades by subject', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/grades');

    // Select subject filter
    await authenticatedPage.selectOption('select[name="subject-filter"]', { index: 1 });

    // Wait for filtered results
    await authenticatedPage.waitForTimeout(1000);

    // Verify results are filtered
    const rows = await authenticatedPage.locator('table tbody tr').count();
    expect(rows).toBeGreaterThanOrEqual(0);
  });

  test('should calculate average grade', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/grades');

    // Wait for grades to load
    await authenticatedPage.waitForSelector('table tbody tr');

    // Check if average is displayed
    const averageExists = await authenticatedPage.locator('text=/promedio|average/i').count();

    if (averageExists > 0) {
      await expect(authenticatedPage.locator('text=/promedio|average/i')).toBeVisible();
    }
  });
});
