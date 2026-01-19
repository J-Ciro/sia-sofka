/**
 * Session formatting utilities
 */

/**
 * Format date string to locale format
 * @param {string} dateString - ISO date string
 * @param {string} locale - Locale code (default: 'es-ES')
 * @returns {string} Formatted date
 */
export const formatDate = (dateString, locale = 'es-ES') => {
  return new Date(dateString).toLocaleDateString(locale, {
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  })
}

/**
 * Format time string to locale format
 * @param {string} timeString - ISO time string
 * @param {string} locale - Locale code (default: 'es-ES')
 * @returns {string} Formatted time
 */
export const formatTime = (timeString, locale = 'es-ES') => {
  return new Date(timeString).toLocaleTimeString(locale, {
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * Get color classes for attendance percentage
 * @param {number} percentage - Attendance percentage (0-100)
 * @returns {string} Tailwind CSS classes
 */
export const getAttendancePercentageColor = (percentage) => {
  if (percentage >= 80) return 'text-green-600 bg-green-100'
  if (percentage >= 70) return 'text-yellow-600 bg-yellow-100'
  return 'text-red-600 bg-red-100'
}

/**
 * Get alert level based on percentage
 * @param {number} percentage - Attendance percentage
 * @returns {string} Alert level
 */
export const getAlertLevel = (percentage) => {
  if (percentage < 70) return 'critical'
  if (percentage < 80) return 'warning'
  return 'success'
}
