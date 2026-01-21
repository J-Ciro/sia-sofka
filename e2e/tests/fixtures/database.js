/**
 * Database fixtures for E2E tests
 * Provides database cleanup and isolation between tests
 */

import { test as base } from '@playwright/test';

/**
 * Extend base test with database cleanup fixture
 */
export const test = base.extend({
  /**
   * Database cleanup fixture
   * Automatically cleans test data before each test
   */
  cleanDatabase: async ({ request }, use) => {
    // Setup: Clean database before test
    await cleanupTestSessions(request);
    
    // Run the test
    await use();
    
    // Teardown: Optional cleanup after test
    // await cleanupTestSessions(request);
  },
});

/**
 * Clean up all test sessions from database
 * @param {import('@playwright/test').APIRequestContext} request - Playwright request context
 */
async function cleanupTestSessions(request) {
  try {
    const response = await request.get('/api/v1/attendance/sessions');
    
    if (response.ok()) {
      const sessions = await response.json();
      
      // Delete all sessions in parallel for better performance
      const deletePromises = sessions.map(session =>
        request.delete(`/api/v1/attendance/sessions/${session.id}`)
          .catch(err => console.log(`Failed to delete session ${session.id}:`, err.message))
      );
      
      await Promise.all(deletePromises);
      console.log(`✓ Cleaned up ${sessions.length} test sessions`);
    }
  } catch (error) {
    console.log('⚠ Database cleanup skipped:', error.message);
  }
}

/**
 * Seed test data into database
 * @param {import('@playwright/test').APIRequestContext} request - Playwright request context
 */
export async function seedTestData(request) {
  // This would call your backend API to seed test data
  // Implement based on your backend endpoints
  try {
    await request.post('/api/v1/test/seed-data');
    console.log('✓ Test data seeded');
  } catch (error) {
    console.log('⚠ Test data seeding skipped:', error.message);
  }
}

export { expect } from '@playwright/test';
