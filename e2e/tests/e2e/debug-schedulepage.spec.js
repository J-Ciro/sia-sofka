import { test, expect } from '../fixtures/auth.js';
import { SchedulePage } from '../pages/SchedulePage.js';

test.describe('Debug SchedulePage', () => {
  test('should import SchedulePage correctly', async ({ authenticatedPage }) => {
    console.log('Testing SchedulePage import...');
    
    const schedulePage = new SchedulePage(authenticatedPage);
    console.log('SchedulePage created successfully');
    
    // Test if goto method exists
    console.log('goto method exists:', typeof schedulePage.goto === 'function');
    console.log('createHorario method exists:', typeof schedulePage.createHorario === 'function');
    
    // Try to call goto
    try {
      await schedulePage.goto();
      console.log('goto() called successfully');
    } catch (error) {
      console.log('Error calling goto():', error.message);
    }
    
    expect(typeof schedulePage.goto).toBe('function');
    expect(typeof schedulePage.createHorario).toBe('function');
  });
});