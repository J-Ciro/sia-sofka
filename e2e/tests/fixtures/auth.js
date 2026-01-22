import { test as base } from '@playwright/test';
import { test as dbTest } from './database.js';

/**
 * Test fixtures for SIA SOFKA
 * Provides reusable setup and teardown logic with authentication
 * 
 * Best Practices:
 * - Fixtures are composable and reusable
 * - Each fixture has a single responsibility
 * - Automatic cleanup after tests
 * - Type-safe with JSDoc comments
 */

/**
 * Test credentials for different user roles
 * 
 * IMPORTANT: These users must exist in the database
 * Run backend seed script if needed: python create_admin.py
 */
export const TEST_USERS = {
  admin: {
    email: 'admin@sofka.edu.co',
    password: 'admin123',
    role: 'Admin'
  },
  profesor: {
    email: 'juan@mail.com', // Using existing user from DB
    password: 'juan123',
    role: 'Profesor'
  },
  estudiante: {
    email: 'sara@mail.com', // Using existing user from DB
    password: 'sara123',
    role: 'Estudiante'
  },
};

/**
 * Login helper function
 * @param {import('@playwright/test').Page} page - Playwright page object
 * @param {string} email - User email
 * @param {string} password - User password
 */
async function login(page, email, password) {
  await page.goto('/login');
  
  // Wait for login page to load
  await page.waitForLoadState('networkidle');
  
  // Fill credentials using more specific selectors
  const emailInput = page.getByRole('textbox', { name: /correo electrónico/i });
  const passwordInput = page.getByRole('textbox', { name: /contraseña/i });
  
  await emailInput.fill(email);
  await passwordInput.fill(password);
  
  // Click login button
  const loginButton = page.getByRole('button', { name: /iniciar sesión/i });
  await loginButton.click();
  
  // Wait for navigation to complete - expect successful login
  try {
    await page.waitForURL('/', { timeout: 15000 });
    
    // Verify we're on dashboard by looking for the dashboard content
    await page.waitForSelector('h1:has-text("Dashboard")', { timeout: 10000 });
    
    console.log(`✅ Login successful for ${email}`);
  } catch (error) {
    // Check if there's an error message on the login page
    const errorVisible = await page.getByText(/error al iniciar sesión/i).isVisible().catch(() => false);
    if (errorVisible) {
      const errorText = await page.getByText(/error al iniciar sesión/i).textContent();
      throw new Error(`Login failed: ${errorText}`);
    }
    
    // If no error message but still failed, throw the original error
    throw new Error(`Login failed for ${email}: ${error.message}`);
  }
}

/**
 * Extend base test with authentication and database fixtures
 */
export const test = dbTest.extend({
  /**
   * Auto-login as Admin
   * @type {import('@playwright/test').Page}
   */
  authenticatedPage: async ({ page, cleanDatabase }, use) => {
    await login(page, TEST_USERS.admin.email, TEST_USERS.admin.password);
    await use(page);
  },

  /**
   * Login as Profesor with database cleanup
   * @type {import('@playwright/test').Page}
   */
  profesorPage: async ({ page, cleanDatabase }, use) => {
    await login(page, TEST_USERS.profesor.email, TEST_USERS.profesor.password);
    await use(page);
  },

  /**
   * Login as Estudiante with database cleanup
   * @type {import('@playwright/test').Page}
   */
  estudiantePage: async ({ page, cleanDatabase }, use) => {
    await login(page, TEST_USERS.estudiante.email, TEST_USERS.estudiante.password);
    await use(page);
  },
});

export { expect } from '@playwright/test';

/**
 * Test data builders for creating test objects
 */
export const testDataBuilder = {
  /**
   * Build a session data object
   * @param {Object} overrides - Properties to override
   * @returns {Object} Session data
   */
  session: (overrides = {}) => ({
    subject_id: 1,
    fecha: new Date().toISOString().split('T')[0],
    hora_inicio: '08:00',
    hora_fin: '09:00',
    descripcion: 'Test Session',
    ...overrides
  }),

  /**
   * Build a subject data object
   * @param {Object} overrides - Properties to override
   * @returns {Object} Subject data
   */
  subject: (overrides = {}) => ({
    nombre: 'Matematicas',
    codigo_institucional: 'MAT301',
    creditos: 4,
    descripcion: 'Test Subject',
    ...overrides
  }),

  /**
   * Build a user data object
   * @param {Object} overrides - Properties to override
   * @returns {Object} User data
   */
  user: (overrides = {}) => ({
    email: `test${Date.now()}@test.com`,
    nombre: 'Test',
    apellido: 'User',
    password: 'password123',
    role: 'Estudiante',
    ...overrides
  }),
};

/**
 * API helpers for common operations
 */
export const apiHelpers = {
  /**
   * Wait for API response matching pattern
   * @param {import('@playwright/test').Page} page - Playwright page
   * @param {string} urlPattern - URL pattern to match
   * @param {number} status - Expected status code
   */
  waitForResponse: async (page, urlPattern, status = 200) => {
    return page.waitForResponse(
      response => response.url().includes(urlPattern) && response.status() === status,
      { timeout: 10000 }
    );
  },

  /**
   * Make authenticated API request
   * @param {import('@playwright/test').APIRequestContext} request - Request context
   * @param {string} method - HTTP method
   * @param {string} url - API endpoint
   * @param {Object} data - Request data
   */
  makeRequest: async (request, method, url, data = null) => {
    const options = {
      headers: {
        'Content-Type': 'application/json',
      },
    };

    if (data) {
      options.data = data;
    }

    return request[method.toLowerCase()](url, options);
  },
};
