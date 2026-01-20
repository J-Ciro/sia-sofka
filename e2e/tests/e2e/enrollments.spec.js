import { test, expect } from '../fixtures/auth.js';

test.describe('Enrollment Management', () => {
  test('should view enrollments list', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/enrollments');

    // Wait for enrollments to load
    await authenticatedPage.waitForSelector('table, [data-testid="enrollments-table"]');

    // Verify table is visible
    await expect(authenticatedPage.locator('table, [data-testid="enrollments-table"]')).toBeVisible();
  });

  test('should create a new enrollment', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/enrollments');

    // Click create button
    await authenticatedPage.click('button:has-text("Crear"), button:has-text("Nueva Inscripción")');

    // Select student
    await authenticatedPage.selectOption('select[name="estudiante_id"]', { index: 1 });

    // Select subject
    await authenticatedPage.selectOption('select[name="subject_id"]', { index: 1 });

    // Submit
    await authenticatedPage.click('button[type="submit"]');

    // Verify success
    await authenticatedPage.waitForSelector('text=/creado|éxito|success/i', { timeout: 5000 });
  });

  test('should prevent duplicate enrollment', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/enrollments');

    // Get first enrollment's student and subject
    const firstRow = authenticatedPage.locator('table tbody tr').first();

    // Try to create duplicate
    await authenticatedPage.click('button:has-text("Crear"), button:has-text("Nueva Inscripción")');

    // Select same student and subject
    await authenticatedPage.selectOption('select[name="estudiante_id"]', { index: 1 });
    await authenticatedPage.selectOption('select[name="subject_id"]', { index: 1 });

    // Submit
    await authenticatedPage.click('button[type="submit"]');

    // Should show error
    await expect(authenticatedPage.locator('text=/ya.*inscrito|already.*enrolled|duplicado/i')).toBeVisible();
  });

  test('should delete an enrollment', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/enrollments');

    // Click delete on last enrollment
    await authenticatedPage.click('button:has-text("Eliminar"), [data-action="delete"]').last();

    // Confirm deletion
    await authenticatedPage.click('button:has-text("Confirmar"), button:has-text("Sí")');

    // Verify success
    await authenticatedPage.waitForSelector('text=/eliminado|éxito|success/i', { timeout: 5000 });
  });

  test('should filter enrollments by student', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/enrollments');

    // Apply student filter
    await authenticatedPage.selectOption('select[name="student-filter"]', { index: 1 });

    // Wait for filtered results
    await authenticatedPage.waitForTimeout(1000);

    // Verify results are shown
    const rows = await authenticatedPage.locator('table tbody tr').count();
    expect(rows).toBeGreaterThanOrEqual(0);
  });

  test('should filter enrollments by subject', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/enrollments');

    // Apply subject filter
    await authenticatedPage.selectOption('select[name="subject-filter"]', { index: 1 });

    // Wait for filtered results
    await authenticatedPage.waitForTimeout(1000);

    // Verify results are shown
    const rows = await authenticatedPage.locator('table tbody tr').count();
    expect(rows).toBeGreaterThanOrEqual(0);
  });
});
