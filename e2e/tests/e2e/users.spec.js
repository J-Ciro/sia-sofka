import { test, expect } from '../fixtures/auth.js';

test.describe('User Management (Admin)', () => {
  test.use({ storageState: 'auth/admin.json' });

  test('should display users list', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/users');

    // Wait for users to load
    await authenticatedPage.waitForSelector('table, [data-testid="users-table"]');

    // Verify table is visible
    await expect(authenticatedPage.locator('table')).toBeVisible();
  });

  test('should create a new Profesor user', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/users');

    // Click create user button
    await authenticatedPage.click('button:has-text("Crear"), button:has-text("Nuevo Usuario")');

    // Fill form
    await authenticatedPage.fill('input[name="nombre"]', 'Juan');
    await authenticatedPage.fill('input[name="apellido"]', 'Pérez');
    await authenticatedPage.fill('input[name="email"]', `profesor${Date.now()}@test.com`);
    await authenticatedPage.fill('input[name="codigo_institucional"]', `PROF${Date.now()}`);
    await authenticatedPage.fill('input[name="password"]', 'Test123456');

    // Select role
    await authenticatedPage.selectOption('select[name="role"]', 'Profesor');

    // Additional Profesor fields
    await authenticatedPage.fill('input[name="area_ensenanza"]', 'Matemáticas');
    await authenticatedPage.fill('input[name="fecha_nacimiento"]', '1985-05-15');

    // Submit
    await authenticatedPage.click('button[type="submit"]');

    // Wait for success message or redirect
    await authenticatedPage.waitForSelector('text=/creado|éxito|success/i', { timeout: 5000 });

    // Verify user appears in list
    await expect(authenticatedPage.locator('text=Juan')).toBeVisible();
  });

  test('should create a new Estudiante user', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/users');

    await authenticatedPage.click('button:has-text("Crear"), button:has-text("Nuevo Usuario")');

    // Fill form
    await authenticatedPage.fill('input[name="nombre"]', 'María');
    await authenticatedPage.fill('input[name="apellido"]', 'González');
    await authenticatedPage.fill('input[name="email"]', `estudiante${Date.now()}@test.com`);
    await authenticatedPage.fill('input[name="codigo_institucional"]', `EST${Date.now()}`);
    await authenticatedPage.fill('input[name="password"]', 'Test123456');

    // Select role
    await authenticatedPage.selectOption('select[name="role"]', 'Estudiante');

    // Additional Estudiante fields
    await authenticatedPage.fill('input[name="programa_academico"]', 'Ingeniería de Sistemas');
    await authenticatedPage.fill('input[name="ciudad_residencia"]', 'Bogotá');
    await authenticatedPage.fill('input[name="fecha_nacimiento"]', '2000-03-20');

    // Submit
    await authenticatedPage.click('button[type="submit"]');

    // Wait for success
    await authenticatedPage.waitForSelector('text=/creado|éxito|success/i', { timeout: 5000 });

    // Verify user appears in list
    await expect(authenticatedPage.locator('text=María')).toBeVisible();
  });

  test('should edit an existing user', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/users');

    // Click edit on first user
    await authenticatedPage.click('button:has-text("Editar"), [data-action="edit"]').first();

    // Modify name
    await authenticatedPage.fill('input[name="nombre"]', 'Nombre Editado');

    // Save
    await authenticatedPage.click('button[type="submit"]');

    // Verify success
    await authenticatedPage.waitForSelector('text=/actualizado|éxito|success/i', { timeout: 5000 });
  });

  test('should delete a user', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/users');

    // Click delete on last user
    const deleteButton = authenticatedPage.locator('button:has-text("Eliminar"), [data-action="delete"]').last();
    await deleteButton.click();

    // Confirm deletion
    await authenticatedPage.click('button:has-text("Confirmar"), button:has-text("Sí")');

    // Wait for success message
    await authenticatedPage.waitForSelector('text=/eliminado|éxito|success/i', { timeout: 5000 });
  });

  test('should filter users by role', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/users');

    // Filter by Profesor
    await authenticatedPage.selectOption('select[name="role-filter"]', 'Profesor');

    // Wait for filtered results
    await authenticatedPage.waitForTimeout(1000);

    // Verify only profesores are shown
    const rows = await authenticatedPage.locator('table tbody tr').count();
    expect(rows).toBeGreaterThan(0);
  });

  test('should search users by name', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/users');

    // Enter search term
    await authenticatedPage.fill('input[type="search"], input[placeholder*="Buscar"]', 'Admin');

    // Wait for search results
    await authenticatedPage.waitForTimeout(500);

    // Verify results contain search term
    await expect(authenticatedPage.locator('text=Admin')).toBeVisible();
  });

  test('should validate email format', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/users');
    await authenticatedPage.click('button:has-text("Crear"), button:has-text("Nuevo Usuario")');

    // Enter invalid email
    await authenticatedPage.fill('input[name="email"]', 'invalid-email');
    await authenticatedPage.fill('input[name="nombre"]', 'Test');
    await authenticatedPage.fill('input[name="apellido"]', 'User');

    // Try to submit
    await authenticatedPage.click('button[type="submit"]');

    // Should show validation error
    await expect(authenticatedPage.locator('text=/email.*inválido|invalid.*email/i')).toBeVisible();
  });
});
