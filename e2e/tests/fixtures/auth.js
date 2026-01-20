import { test as base } from '@playwright/test';

/**
 * Test fixtures for SIA SOFKA
 * Provides reusable setup and teardown logic
 */

// Extend basic test by providing authentication fixtures
export const test = base.extend({
  // Auto-login as Admin
  authenticatedPage: async ({ page }, use) => {
    await page.goto('/login');
    await page.fill('input[name="email"]', 'admin@sofka.edu.co');
    await page.fill('input[name="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');
    await use(page);
  },

  // Login as Profesor
  profesorPage: async ({ page }, use) => {
    await page.goto('/login');
    await page.fill('input[name="email"]', 'profesor@sofka.edu.co');
    await page.fill('input[name="password"]', 'profesor123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');
    await use(page);
  },

  // Login as Estudiante
  estudiantePage: async ({ page }, use) => {
    await page.goto('/login');
    await page.fill('input[name="email"]', 'estudiante@sofka.edu.co');
    await page.fill('input[name="password"]', 'estudiante123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');
    await use(page);
  },
});

export { expect } from '@playwright/test';

/**
 * Helper function to create test data
 */
export const testData = {
  admin: {
    email: 'admin@sofka.edu.co',
    password: 'admin123',
  },
  profesor: {
    email: 'profesor@sofka.edu.co',
    password: 'profesor123',
    nombre: 'Carlos',
    apellido: 'Ramírez',
    codigo_institucional: 'PROF001',
  },
  estudiante: {
    email: 'estudiante@sofka.edu.co',
    password: 'estudiante123',
    nombre: 'Ana',
    apellido: 'García',
    codigo_institucional: 'EST001',
  },
  subject: {
    nombre: 'Matemáticas Avanzadas',
    codigo_institucional: 'MAT301',
    numero_creditos: 4,
    horario: 'Lunes y Miércoles 8:00-10:00',
  },
};

/**
 * Helper function to wait for API response
 */
export async function waitForApiResponse(page, urlPattern) {
  return page.waitForResponse(response =>
    response.url().includes(urlPattern) && response.status() === 200
  );
}

/**
 * Helper function to clear all data (for test isolation)
 */
export async function clearTestData(page) {
  // This would call your backend API to clear test data
  // Implement based on your backend endpoints
  await page.request.delete('/api/v1/test/clear-data');
}
