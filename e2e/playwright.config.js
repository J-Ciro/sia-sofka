import { defineConfig, devices } from '@playwright/test';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

/**
 * Playwright Configuration for SIA SOFKA E2E Tests
 * 
 * Best Practices:
 * - Sequential execution (workers: 1) for database isolation
 * - Global setup/teardown for environment preparation
 * - Automatic cleanup between tests via fixtures
 * - No external scripts - everything via API
 * 
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './tests/e2e',

  // Sequential execution for database isolation
  fullyParallel: false,
  workers: 1, // CRITICAL: Must be 1 for database isolation

  // Fail the build on CI if you accidentally left test.only
  forbidOnly: !!process.env.CI,

  // Retry on CI only
  retries: process.env.CI ? 2 : 0,

  // Reporter
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['list'],
    ['json', { outputFile: 'playwright-results.json' }]
  ],

  // Global setup - runs once before all tests
  globalSetup: resolve(__dirname, './tests/global-setup.js'),
  
  // Global teardown - runs once after all tests
  globalTeardown: resolve(__dirname, './tests/global-teardown.js'),

  // Shared settings
  use: {
    // Base URL: frontend
    baseURL: process.env.BASE_URL || 'http://localhost:3000',

    // API endpoint: backend
    apiURL: process.env.API_URL || 'http://localhost:8000',

    // Collect trace when retrying
    trace: 'on-first-retry',

    // Screenshot on failure
    screenshot: 'only-on-failure',

    // Video on failure
    video: 'retain-on-failure',

    // Timeouts
    actionTimeout: 10000,
    navigationTimeout: 30000,
  },

  // Browser configuration
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    }
  ],

  // Optional: Auto-start servers (commented out - start manually)
  // webServer: [
  //   {
  //     command: 'cd ../backend && uvicorn app.main:app --reload',
  //     url: 'http://localhost:8000',
  //     reuseExistingServer: !process.env.CI,
  //     timeout: 120000,
  //   },
  //   {
  //     command: 'cd ../frontend && npm run dev',
  //     url: 'http://localhost:3000',
  //     reuseExistingServer: !process.env.CI,
  //     timeout: 120000,
  //   }
  // ],
});
