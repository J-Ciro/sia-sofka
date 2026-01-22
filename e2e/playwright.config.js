import { defineConfig, devices } from '@playwright/test';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export default defineConfig({
  testDir: './tests/e2e',

  fullyParallel: false,
  workers: 1, 

  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,

  // 1. ELIMINÉ launchOptions DE AQUÍ (estaba mal ubicado)

  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['list'],
    ['json', { outputFile: 'playwright-results.json' }]
  ],

  globalSetup: resolve(__dirname, './tests/global-setup.js'),
  globalTeardown: resolve(__dirname, './tests/global-teardown.js'),

  // Shared settings
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    apiURL: process.env.API_URL || 'http://localhost:8000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',

    // 2. AQUÍ ES DONDE DEBE IR
    // He eliminado la línea anterior que decía "slowMo: ... 500"
    launchOptions: {
        slowMo: 500, // 10 segundos de espera entre acciones
    },

  //  actionTimeout: 500,
  //  navigationTimeout: 500,
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    }
  ],
});