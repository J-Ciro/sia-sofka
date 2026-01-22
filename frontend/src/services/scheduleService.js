/**
 * Schedule Service
 * Handles schedule management operations including date-specific and weekly recurring schedules
 */

import api from './api'

export const scheduleService = {
  /**
   * Get weekly schedules (existing functionality)
   * @param {Object} params - Query parameters
   * @returns {Promise<Array>} Weekly schedules
   */
  getWeekly: async (params = {}) => {
    const response = await api.get('/schedules/weekly', { params })
    return response.data
  },

  /**
   * Get schedules by date range - Enhanced for Task 11.1
   * Supports both date-specific and weekly recurring schedules
   * @param {string} startDate - Start date in YYYY-MM-DD format
   * @param {string} endDate - End date in YYYY-MM-DD format
   * @param {Object} options - Additional options
   * @param {number} options.user_id - Admin: filter by user ID
   * @param {string} options.role - Admin: filter by user role
   * @returns {Promise<Array>} Schedules within the date range
   */
  getByDateRange: async (startDate, endDate, options = {}) => {
    try {
      const params = {
        start_date: startDate,
        end_date: endDate,
      }

      // Add admin filtering options if provided
      if (options.user_id !== undefined) {
        params.user_id = options.user_id
      }
      if (options.role) {
        params.role = options.role
      }

      const response = await api.get('/schedules/date-range', { params })
      return response.data || []
    } catch (error) {
      console.error('Error fetching schedules by date range:', error)
      throw error
    }
  },

  /**
   * Create a new schedule - Enhanced for Task 11.1
   * Supports both weekly recurring and date-specific schedules
   * @param {Object} data - Schedule data
   * @param {number} data.subject_id - Subject ID
   * @param {number} data.classroom_id - Classroom ID
   * @param {number} data.dia_semana - Day of week (1-6)
   * @param {string} data.hora_inicio - Start time (HH:MM)
   * @param {string} data.hora_fin - End time (HH:MM)
   * @param {string} [data.fecha_especifica] - Specific date (YYYY-MM-DD) for date-specific schedules
   * @returns {Promise<Object>} Created schedule
   */
  create: async (data) => {
    try {
      const response = await api.post('/schedules', data)
      return response.data
    } catch (error) {
      console.error('Error creating schedule:', error)
      throw error
    }
  },

  /**
   * Update an existing schedule - Enhanced for Task 11.1
   * Supports updating date-specific information
   * @param {number} id - Schedule ID
   * @param {Object} data - Updated schedule data
   * @returns {Promise<Object>} Updated schedule
   */
  update: async (id, data) => {
    try {
      const response = await api.put(`/schedules/${id}`, data)
      return response.data
    } catch (error) {
      console.error('Error updating schedule:', error)
      throw error
    }
  },

  /**
   * Move schedule to new date and time - Enhanced for Task 11.1
   * Optimized for drag-and-drop operations
   * @param {number} id - Schedule ID
   * @param {string} newDate - New date in YYYY-MM-DD format
   * @param {string} newStartTime - New start time in HH:MM format
   * @param {string} newEndTime - New end time in HH:MM format
   * @returns {Promise<Object>} Updated schedule
   */
  move: async (id, newDate, newStartTime, newEndTime) => {
    try {
      const response = await api.patch(`/schedules/${id}/move`, null, {
        params: {
          new_date: newDate,
          new_start_time: newStartTime,
          new_end_time: newEndTime
        }
      })
      return response.data
    } catch (error) {
      console.error('Error moving schedule:', error)
      throw error
    }
  },

  /**
   * Bulk move operation for multiple schedules
   * Useful for complex drag-and-drop scenarios
   * @param {Array} moves - Array of move operations
   * @param {number} moves[].id - Schedule ID
   * @param {string} moves[].newDate - New date
   * @param {string} moves[].newStartTime - New start time
   * @param {string} moves[].newEndTime - New end time
   * @returns {Promise<Array>} Results of move operations
   */
  bulkMove: async (moves) => {
    try {
      const results = await Promise.allSettled(
        moves.map(({ id, newDate, newStartTime, newEndTime }) =>
          scheduleService.move(id, newDate, newStartTime, newEndTime)
        )
      )
      
      const successful = []
      const failed = []
      
      results.forEach((result, index) => {
        if (result.status === 'fulfilled') {
          successful.push({ index, data: result.value })
        } else {
          failed.push({ index, error: result.reason })
        }
      })
      
      return { successful, failed }
    } catch (error) {
      console.error('Error in bulk move operation:', error)
      throw error
    }
  },

  /**
   * Delete a schedule
   * @param {number} id - Schedule ID
   * @returns {Promise<void>}
   */
  delete: async (id) => {
    try {
      await api.delete(`/schedules/${id}`)
    } catch (error) {
      console.error('Error deleting schedule:', error)
      throw error
    }
  },

  /**
   * Get schedules by classroom - Enhanced for Task 11.1
   * Returns both weekly recurring and date-specific schedules
   * @param {number} classroomId - Classroom ID
   * @param {Object} options - Additional options
   * @param {string} [options.startDate] - Filter from this date
   * @param {string} [options.endDate] - Filter to this date
   * @returns {Promise<Array>} Classroom schedules
   */
  getByClassroom: async (classroomId, options = {}) => {
    try {
      const params = {}
      if (options.startDate) params.start_date = options.startDate
      if (options.endDate) params.end_date = options.endDate

      const response = await api.get(`/schedules/classroom/${classroomId}`, { params })
      return response.data || []
    } catch (error) {
      console.error('Error fetching classroom schedules:', error)
      throw error
    }
  },

  /**
   * Get schedules for a specific date
   * Convenience method for single-date queries
   * @param {string} date - Date in YYYY-MM-DD format
   * @param {Object} options - Additional options
   * @returns {Promise<Array>} Schedules for the specific date
   */
  getByDate: async (date, options = {}) => {
    return scheduleService.getByDateRange(date, date, options)
  },

  /**
   * Get schedules for current week
   * Convenience method for weekly calendar views
   * @param {Date} [referenceDate] - Reference date for the week (defaults to today)
   * @param {Object} options - Additional options
   * @returns {Promise<Array>} Schedules for the current week
   */
  getCurrentWeek: async (referenceDate = new Date(), options = {}) => {
    try {
      // Calculate start and end of week (Monday to Sunday)
      const startOfWeek = new Date(referenceDate)
      const day = startOfWeek.getDay()
      const diff = startOfWeek.getDate() - day + (day === 0 ? -6 : 1) // Adjust for Sunday
      startOfWeek.setDate(diff)
      
      const endOfWeek = new Date(startOfWeek)
      endOfWeek.setDate(startOfWeek.getDate() + 6)
      
      const startDate = startOfWeek.toISOString().split('T')[0]
      const endDate = endOfWeek.toISOString().split('T')[0]
      
      return scheduleService.getByDateRange(startDate, endDate, options)
    } catch (error) {
      console.error('Error fetching current week schedules:', error)
      throw error
    }
  },

  /**
   * Get schedules for current month
   * Convenience method for monthly calendar views
   * @param {Date} [referenceDate] - Reference date for the month (defaults to today)
   * @param {Object} options - Additional options
   * @returns {Promise<Array>} Schedules for the current month
   */
  getCurrentMonth: async (referenceDate = new Date(), options = {}) => {
    try {
      const year = referenceDate.getFullYear()
      const month = referenceDate.getMonth()
      
      const startOfMonth = new Date(year, month, 1)
      const endOfMonth = new Date(year, month + 1, 0)
      
      const startDate = startOfMonth.toISOString().split('T')[0]
      const endDate = endOfMonth.toISOString().split('T')[0]
      
      return scheduleService.getByDateRange(startDate, endDate, options)
    } catch (error) {
      console.error('Error fetching current month schedules:', error)
      throw error
    }
  },

  /**
   * Validate schedule conflicts before creation/update
   * Client-side validation helper
   * @param {Object} scheduleData - Schedule data to validate
   * @param {number} [excludeId] - Schedule ID to exclude from conflict check
   * @returns {Promise<Object>} Validation result with conflicts if any
   */
  validateConflicts: async (scheduleData, excludeId = null) => {
    try {
      // This would typically be handled by the backend during create/update
      // But we can provide client-side validation by checking existing schedules
      const { subject_id, classroom_id, dia_semana, hora_inicio, hora_fin, fecha_especifica } = scheduleData
      
      // Get existing schedules for the same day/date
      let existingSchedules = []
      
      if (fecha_especifica) {
        // Check for date-specific conflicts
        existingSchedules = await scheduleService.getByDate(fecha_especifica)
      } else {
        // Check for weekly recurring conflicts
        // This would require a more complex query - for now, let the backend handle it
        return { valid: true, conflicts: [] }
      }
      
      // Filter schedules that might conflict
      const conflicts = existingSchedules.filter(schedule => {
        if (excludeId && schedule.id === excludeId) return false
        
        // Check classroom conflicts
        if (schedule.classroom_id === classroom_id) {
          return scheduleService._timeOverlaps(
            hora_inicio, hora_fin,
            schedule.hora_inicio, schedule.hora_fin
          )
        }
        
        // Check professor conflicts (same subject implies same professor)
        if (schedule.subject_id === subject_id) {
          return scheduleService._timeOverlaps(
            hora_inicio, hora_fin,
            schedule.hora_inicio, schedule.hora_fin
          )
        }
        
        return false
      })
      
      return {
        valid: conflicts.length === 0,
        conflicts: conflicts
      }
    } catch (error) {
      console.error('Error validating schedule conflicts:', error)
      // Return valid=true to let backend handle validation
      return { valid: true, conflicts: [] }
    }
  },

  /**
   * Helper method to check if two time ranges overlap
   * @private
   * @param {string} start1 - Start time 1 (HH:MM)
   * @param {string} end1 - End time 1 (HH:MM)
   * @param {string} start2 - Start time 2 (HH:MM)
   * @param {string} end2 - End time 2 (HH:MM)
   * @returns {boolean} True if times overlap
   */
  _timeOverlaps: (start1, end1, start2, end2) => {
    const toMinutes = (timeStr) => {
      const [hours, minutes] = timeStr.split(':').map(Number)
      return hours * 60 + minutes
    }
    
    const s1 = toMinutes(start1)
    const e1 = toMinutes(end1)
    const s2 = toMinutes(start2)
    const e2 = toMinutes(end2)
    
    return s1 < e2 && s2 < e1
  }
}