/**
 * Date and time helpers for tests
 * Provides consistent date/time generation for test data
 */

/**
 * Get a unique date for testing
 * Uses current timestamp to ensure uniqueness across test runs
 * @param {number} testNumber - Test number for additional offset
 * @returns {string} Date in YYYY-MM-DD format
 */
export function getTestDate(testNumber = 0) {
  const now = new Date();
  // Use past dates to avoid conflicts and ensure we're not using future dates
  // Go back in time based on test number to ensure uniqueness
  const daysBack = Math.floor(testNumber / 5) + 1; // Group every 5 tests on same day, but go back at least 1 day
  const date = new Date(now.getTime() - (daysBack * 86400000));
  return date.toISOString().split('T')[0];
}

/**
 * Get a unique time slot for testing
 * Uses current time and test number to ensure uniqueness
 * @param {number} testNumber - Test number for hour offset
 * @returns {{startTime: string, endTime: string}} Time slot in HH:MM format
 */
export function getTestTimeSlot(testNumber = 0) {
  const now = new Date();
  const timestamp = now.getTime();
  
  // Create highly unique time slots using timestamp and test number
  // This ensures each test run gets different times
  const uniqueMinutes = (timestamp + testNumber * 1000) % (12 * 60); // 12 hours worth of minutes
  const startMinutes = 360 + uniqueMinutes; // Start from 6:00 AM (360 minutes from midnight)
  
  const startHour = Math.floor(startMinutes / 60) % 24;
  const startMinute = startMinutes % 60;
  
  // Ensure end time is exactly 30 minutes after start time
  const endMinutes = startMinutes + 30;
  const endHour = Math.floor(endMinutes / 60) % 24;
  const endMinute = endMinutes % 60;
  
  return {
    startTime: `${String(startHour).padStart(2, '0')}:${String(startMinute).padStart(2, '0')}`,
    endTime: `${String(endHour).padStart(2, '0')}:${String(endMinute).padStart(2, '0')}`
  };
}

/**
 * Get a future date (for validation tests)
 * @param {number} daysAhead - Number of days in the future
 * @returns {string} Date in YYYY-MM-DD format
 */
export function getFutureDate(daysAhead = 1) {
  const date = new Date();
  date.setDate(date.getDate() + daysAhead);
  return date.toISOString().split('T')[0];
}

/**
 * Get a past date
 * @param {number} daysAgo - Number of days in the past
 * @returns {string} Date in YYYY-MM-DD format
 */
export function getPastDate(daysAgo = 1) {
  const date = new Date();
  date.setDate(date.getDate() - daysAgo);
  return date.toISOString().split('T')[0];
}

/**
 * Get today's date
 * @returns {string} Date in YYYY-MM-DD format
 */
export function getToday() {
  return new Date().toISOString().split('T')[0];
}

/**
 * Format time for display
 * @param {string} time - Time in HH:MM format
 * @returns {string} Formatted time
 */
export function formatTime(time) {
  return time;
}

/**
 * Check if date is in the past
 * @param {string} dateStr - Date in YYYY-MM-DD format
 * @returns {boolean}
 */
export function isDateInPast(dateStr) {
  const date = new Date(dateStr);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return date < today;
}

/**
 * Check if date is in the future
 * @param {string} dateStr - Date in YYYY-MM-DD format
 * @returns {boolean}
 */
export function isDateInFuture(dateStr) {
  const date = new Date(dateStr);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return date > today;
}
