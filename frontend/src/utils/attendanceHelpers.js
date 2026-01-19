/**
 * Attendance utility functions following SOLID principles
 */

export const AttendanceStatus = {
  PRESENTE: 'PRESENTE',
  AUSENTE: 'AUSENTE',
  TARDANZA: 'TARDANZA'
}

/**
 * Get the next attendance state in the cycle
 * @param {string} currentState - Current attendance state
 * @returns {string} Next state in the cycle
 */
export const getNextAttendanceState = (currentState) => {
  const stateCycle = [
    AttendanceStatus.PRESENTE,
    AttendanceStatus.AUSENTE,
    AttendanceStatus.TARDANZA
  ]
  
  const currentIndex = stateCycle.indexOf(currentState)
  const nextIndex = (currentIndex + 1) % stateCycle.length
  return stateCycle[nextIndex]
}

/**
 * Count students by attendance status
 * @param {Object} attendanceMap - Map of student IDs to attendance states
 * @returns {Object} Counts for each status
 */
export const countByStatus = (attendanceMap) => {
  const counts = {
    [AttendanceStatus.PRESENTE]: 0,
    [AttendanceStatus.AUSENTE]: 0,
    [AttendanceStatus.TARDANZA]: 0
  }
  
  Object.values(attendanceMap).forEach(estado => {
    if (counts[estado] !== undefined) {
      counts[estado]++
    }
  })
  
  return counts
}

/**
 * Get Tailwind CSS classes for attendance status
 * @param {string} estado - Attendance state
 * @returns {string} CSS classes
 */
export const getAttendanceColorClasses = (estado) => {
  const colorMap = {
    [AttendanceStatus.PRESENTE]: 'bg-green-50 border-green-500 text-green-700 hover:bg-green-100',
    [AttendanceStatus.AUSENTE]: 'bg-red-50 border-red-500 text-red-700 hover:bg-red-100',
    [AttendanceStatus.TARDANZA]: 'bg-yellow-50 border-yellow-500 text-yellow-700 hover:bg-yellow-100'
  }
  
  return colorMap[estado] || 'bg-gray-50 border-gray-300 text-gray-700'
}

/**
 * Initialize attendance map with default state for all students
 * @param {Array} students - Array of student objects
 * @param {string} defaultState - Default attendance state
 * @returns {Object} Initial attendance map
 */
export const initializeAttendanceMap = (students, defaultState = AttendanceStatus.AUSENTE) => {
  const attendanceMap = {}
  students.forEach(student => {
    attendanceMap[student.id] = defaultState
  })
  return attendanceMap
}

/**
 * Format session data for API submission
 * @param {Object} attendanceMap - Map of student IDs to attendance states
 * @returns {Array} Array of attendance updates
 */
export const formatAttendanceForSubmission = (attendanceMap) => {
  return Object.entries(attendanceMap).map(([estudianteId, estado]) => ({
    estudiante_id: parseInt(estudianteId),
    estado
  }))
}
