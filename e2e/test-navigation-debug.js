import { test, expect } from './tests/fixtures/auth.js';
import { SchedulePage } from './tests/pages/SchedulePage.js';

test.describe('Debug Navigation', () => {
  test('should navigate to horarios page successfully', async ({ authenticatedPage }) => {
    console.log('Starting navigation test...');
    
    // Check current URL
    const currentUrl = authenticatedPage.url();
    console.log('Current URL:', currentUrl);
    
    // Navigate to horarios
    await authenticatedPage.goto('/horarios');
    await authenticatedPage.waitForLoadState('networkidle');
    
    // Check new URL
    const newUrl = authenticatedPage.url();
    console.log('New URL:', newUrl);
    
    // Check if page title exists
    const titleVisible = await authenticatedPage.locator('h1').isVisible();
    console.log('Title visible:', titleVisible);
    
    if (titleVisible) {
      const titleText = await authenticatedPage.locator('h1').textContent();
      console.log('Title text:', titleText);
    }
    
    // Check if create button exists
    const createButtonVisible = await authenticatedPage.locator('button:has-text("Nuevo horario")').isVisible();
    console.log('Create button visible:', createButtonVisible);
    
    // Take a screenshot for debugging
    await authenticatedPage.screenshot({ path: 'debug-horarios-page.png' });
    
    expect(titleVisible).toBeTruthy();
  });
});