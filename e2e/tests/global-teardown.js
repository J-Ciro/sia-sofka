/**
 * Global teardown for Playwright tests
 * Runs once after all tests complete
 */

export default async function globalTeardown() {
  console.log('\n🧹 Cleaning up test environment...\n');
  
  // Optional: Clean up test database or leave it for inspection
  // For now, we'll leave the test database intact for debugging
  
  console.log(' Teardown complete!\n');
}
