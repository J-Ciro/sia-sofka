import { test, expect } from '../fixtures/auth.js';

test.describe('Navigation', () => {
  test('should navigate through main sections (Admin)', async ({ authenticatedPage }) => {
    // Dashboard
    await authenticatedPage.goto('/dashboard');
    await expect(authenticatedPage).toHaveURL(/.*dashboard/);

    // Users
    await authenticatedPage.click('a[href="/users"], nav a:has-text("Usuarios")');
    await expect(authenticatedPage).toHaveURL(/.*users/);

    // Subjects
    await authenticatedPage.click('a[href="/subjects"], nav a:has-text("Materias")');
    await expect(authenticatedPage).toHaveURL(/.*subjects/);

    // Enrollments
    await authenticatedPage.click('a[href="/enrollments"], nav a:has-text("Inscripciones")');
    await expect(authenticatedPage).toHaveURL(/.*enrollments/);

    // Grades
    await authenticatedPage.click('a[href="/grades"], nav a:has-text("Notas")');
    await expect(authenticatedPage).toHaveURL(/.*grades/);
  });

  test('should handle browser back button', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/dashboard');
    await authenticatedPage.goto('/users');
    await authenticatedPage.goBack();

    await expect(authenticatedPage).toHaveURL(/.*dashboard/);
  });

  test('should handle browser forward button', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/dashboard');
    await authenticatedPage.goto('/users');
    await authenticatedPage.goBack();
    await authenticatedPage.goForward();

    await expect(authenticatedPage).toHaveURL(/.*users/);
  });

  test('should show 404 page for invalid routes', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/invalid-route-that-does-not-exist');

    // Should show 404 message
    await expect(authenticatedPage.locator('text=/404|no.*encontrado|not.*found/i')).toBeVisible();
  });

  test('should redirect to login when accessing protected route without auth', async ({ page }) => {
    await page.goto('/dashboard');

    // Should redirect to login
    await expect(page).toHaveURL(/.*login/);
  });
});
