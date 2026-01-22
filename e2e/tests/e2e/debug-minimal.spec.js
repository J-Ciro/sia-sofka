import { test, expect } from '../fixtures/auth.js';
import { SchedulePageMinimal } from '../pages/SchedulePageMinimal.js';

test.describe('Debug Minimal', () => {
  test('should import minimal SchedulePage correctly', async ({ authenticatedPage }) => {
    console.log('Testing minimal SchedulePage import...');
    
    const schedulePage = new SchedulePageMinimal(authenticatedPage);
    console.log('SchedulePageMinimal created successfully');
    
    // Test if goto method exists
    console.log('goto method exists:', typeof schedulePage.goto === 'function');
    
    // Try to call goto
    try {
      await schedulePage.goto();
      console.log('goto() called successfully');
    } catch (error) {
      console.log('Error calling goto():', error.message);
    }
    
    expect(typeof schedulePage.goto).toBe('function');
  });
});