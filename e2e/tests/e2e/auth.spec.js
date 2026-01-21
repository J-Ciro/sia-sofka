import { test, expect } from '../fixtures/auth.js';

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should redirect to login page when not authenticated', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveURL(/.*login/);
  });

  test('should login successfully as Admin', async ({ page }) => {
    await page.goto('/login');

    // Fill login form
    await page.fill('input[name="email"]', 'admin@sofka.edu.co');
    await page.fill('input[name="password"]', 'admin123');

    // Submit form
    await page.click('button[type="submit"]');

    // Wait for navigation

    await page.waitForURL('**/');

    // Verify we're on dashboard (root)
    await expect(page).toHaveURL('http://localhost:3000/');

    // Verify user info is displayed
    await expect(page.locator('text=Admin')).toBeVisible();
  });

  test('should show error message on invalid credentials', async ({ page }) => {
    await page.goto('/login');

    await page.fill('input[name="email"]', 'invalid@test.com');
    await page.fill('input[name="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');

    // Should stay on login page
    await expect(page).toHaveURL(/.*login/);

    // Should show error message
    await expect(page.locator('text=/error|invalid|incorrect/i')).toBeVisible();
  });

  test('should logout successfully', async ({ authenticatedPage }) => {
    // Click logout button
    await authenticatedPage.click('button:has-text("Cerrar Sesión"), button:has-text("Logout")');

    // Should redirect to login
    await authenticatedPage.waitForURL('**/login');
    await expect(authenticatedPage).toHaveURL(/.*login/);
  });

  test('should validate required fields', async ({ page }) => {
    await page.goto('/login');

    // Try to submit empty form
    await page.click('button[type="submit"]');

    // Form validation should prevent submission
    await expect(page).toHaveURL(/.*login/);
  });
});
