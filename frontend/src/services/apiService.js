/**
 * Servicio de API con métodos helper para las diferentes entidades
 * Facilita el uso de la API desde los componentes
 */

import api from './api'

// ==================== AUTH ====================
export const authService = {
  login: async (email, password) => {
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)

    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return response.data
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me')
    return response.data
  },

  register: async (userData) => {
    const response = await api.post('/auth/register', userData)
    return response.data
  },
}

// ==================== USERS ====================
export const userService = {
  getAll: async (skip = 0, limit = 100) => {
    const response = await api.get('/users', { params: { skip, limit } })
    return response.data
  },

  getById: async (userId) => {
    const response = await api.get(`/users/${userId}`)
    return response.data
  },

  create: async (userData) => {
    const response = await api.post('/users', userData)
    return response.data
  },

  update: async (userId, userData) => {
    const response = await api.put(`/users/${userId}`, userData)
    return response.data
  },

  delete: async (userId) => {
    await api.delete(`/users/${userId}`)
  },

  /** Importar estudiantes desde Excel. Retorna { created, updated, errors }. En 400 con errores, res.data ya tiene ese formato. */
  bulkImport: async (file) => {
    const fd = new FormData()
    fd.append('file', file)
    const res = await api.post('/users/bulk-import', fd, {
      validateStatus: (s) => s === 200 || s === 400,
      transformRequest: [(data, headers) => {
        if (data instanceof FormData) delete headers['Content-Type']
        return data
      }],
    })
    return res.data
  },

  /** Exportar usuarios a Excel. Descarga el archivo. */
  exportToExcel: async (role = null) => {
    const params = role ? { role } : {}
    const res = await api.get('/users/export', { params, responseType: 'blob' })
    const url = window.URL.createObjectURL(res.data)
    const a = document.createElement('a')
    a.href = url
    a.download = `usuarios${role ? `_${role}` : ''}.xlsx`
    a.click()
    window.URL.revokeObjectURL(url)
  },

  /** Descargar plantilla Excel para importación. */
  downloadImportTemplate: async () => {
    const res = await api.get('/users/template', { responseType: 'blob' })
    const url = window.URL.createObjectURL(res.data)
    const a = document.createElement('a')
    a.href = url
    a.download = 'plantilla_estudiantes.xlsx'
    a.click()
    window.URL.revokeObjectURL(url)
  },
}

// ==================== SUBJECTS ====================
export const subjectService = {
  getAll: async (skip = 0, limit = 100) => {
    const response = await api.get('/subjects', { params: { skip, limit } })
    return response.data
  },

  getById: async (subjectId) => {
    const response = await api.get(`/subjects/${subjectId}`)
    return response.data
  },

  create: async (subjectData) => {
    const response = await api.post('/subjects', subjectData)
    return response.data
  },

  update: async (subjectId, subjectData) => {
    const response = await api.put(`/subjects/${subjectId}`, subjectData)
    return response.data
  },

  delete: async (subjectId) => {
    await api.delete(`/subjects/${subjectId}`)
  },
}

// ==================== ENROLLMENTS ====================
export const enrollmentService = {
  getAll: async (skip = 0, limit = 100) => {
    const response = await api.get('/enrollments', { params: { skip, limit } })
    return response.data
  },

  getById: async (enrollmentId) => {
    const response = await api.get(`/enrollments/${enrollmentId}`)
    return response.data
  },

  create: async (enrollmentData) => {
    const response = await api.post('/enrollments', enrollmentData)
    return response.data
  },

  delete: async (enrollmentId) => {
    await api.delete(`/enrollments/${enrollmentId}`)
  },
}

// ==================== GRADES ====================
export const gradeService = {
  getAll: async (params = {}) => {
    const response = await api.get('/grades', { params })
    return response.data
  },

  getById: async (gradeId) => {
    const response = await api.get(`/grades/${gradeId}`)
    return response.data
  },

  create: async (gradeData, subjectId) => {
    const response = await api.post('/grades', gradeData, {
      params: { subject_id: subjectId },
    })
    return response.data
  },

  update: async (gradeId, gradeData) => {
    const response = await api.put(`/grades/${gradeId}`, gradeData)
    return response.data
  },

  delete: async (gradeId) => {
    await api.delete(`/grades/${gradeId}`)
  },
}

// ==================== REPORTS ====================
export const reportService = {
  /**
   * Obtiene el reporte de un estudiante
   * @param {number} estudianteId - ID del estudiante
   * @param {string} format - Formato: 'pdf', 'html' o 'json'
   * @returns {Promise<Blob|Object>} - Blob para PDF/HTML, Object para JSON
   */
  getStudentReport: async (estudianteId, format = 'pdf') => {
    const response = await api.get(`/reports/student/${estudianteId}`, {
      params: { format },
      responseType: format === 'json' ? 'json' : 'blob',
    })
    return response.data
  },

  getSubjectReport: async (subjectId, format = 'pdf') => {
    const response = await api.get(`/reports/subject/${subjectId}`, {
      params: { format },
      responseType: format === 'json' ? 'json' : 'blob',
    })
    return response.data
  },

  getGeneralReport: async (format = 'pdf') => {
    const response = await api.get('/reports/general', {
      params: { format },
      responseType: format === 'json' ? 'json' : 'blob',
    })
    return response.data
  },
}

// ==================== PROFILE ====================
export const profileService = {
  get: async () => {
    const response = await api.get('/profile')
    return response.data
  },

  update: async (profileData) => {
    const response = await api.put('/profile', profileData)
    return response.data
  },
}

// ==================== PROFESOR ====================
export const profesorService = {
  /**
   * Obtiene las materias asignadas al profesor
   * Ahora el backend permite a los profesores acceder a /subjects y automáticamente
   * retorna solo sus materias asignadas
   */
  getAssignedSubjects: async (profesorId) => {
    try {
      // El backend ahora retorna automáticamente solo las materias asignadas al profesor
      const response = await api.get('/subjects')
      // El backend ya filtra por profesor_id, pero verificamos por seguridad
      const subjects = response.data || []
      // Verificar que todas las materias pertenezcan al profesor (doble verificación)
      return subjects.filter((subject) => subject.profesor_id === profesorId)
    } catch (error) {
      console.error('Error getting assigned subjects:', error)
      // Si falla, retornar array vacío
      if (error.response?.status === 403 || error.response?.status === 401) {
        console.warn('No se tienen permisos para acceder a /subjects.')
        return []
      }
      throw error
    }
  },

  /**
   * Obtiene los estudiantes inscritos en una materia
   * Usa /subjects/{subject_id}/students para obtener estudiantes desde inscripciones
   */
  getStudentsBySubject: async (subjectId) => {
    try {
      const response = await api.get(`/subjects/${subjectId}/students`)
      return response.data || []
    } catch (error) {
      console.error('Error getting students by subject:', error)
      // Si falla, retornar array vacío en lugar de lanzar error
      if (error.response?.status === 403 || error.response?.status === 401) {
        console.warn('No se tienen permisos para acceder a los estudiantes de esta materia.')
        return []
      }
      if (error.response?.status === 404 || error.response?.status === 400) {
        console.warn('Materia no encontrada o no asignada.')
        return []
      }
      throw error
    }
  },

  /**
   * Obtiene las inscripciones de una materia
   * Usa /subjects/{subject_id}/enrollments para obtener inscripciones con enrollment_id
   */
  getEnrollmentsBySubject: async (subjectId) => {
    try {
      const response = await api.get(`/subjects/${subjectId}/enrollments`)
      return response.data || []
    } catch (error) {
      console.error('Error getting enrollments by subject:', error)
      // Si falla, retornar array vacío en lugar de lanzar error
      if (error.response?.status === 403 || error.response?.status === 401) {
        console.warn('No se tienen permisos para acceder a las inscripciones de esta materia.')
        return []
      }
      if (error.response?.status === 404 || error.response?.status === 400) {
        console.warn('Materia no encontrada o no asignada.')
        return []
      }
      throw error
    }
  },

  /**
   * Obtiene las notas de una materia con información de estudiantes
   */
  getGradesBySubject: async (subjectId, enrollmentId = null) => {
    const params = { subject_id: subjectId }
    if (enrollmentId) {
      params.enrollment_id = enrollmentId
    }
    return await gradeService.getAll(params)
  },
}

// ==================== ESTUDIANTE ====================
export const estudianteService = {
  /**
   * Obtiene las materias en las que el estudiante está inscrito.
   * Usa GET /enrollments/me (requiere rol Estudiante). Devuelve subjects para selectores.
   */
  getEnrolledSubjects: async () => {
    const response = await api.get('/enrollments/me')
    const enrollments = response.data || []
    return enrollments.map((e) => e.subject).filter(Boolean)
  },

  /**
   * Obtiene las materias inscritas del estudiante
   * Intenta acceder a /enrollments y filtra por estudiante_id
   * Si falla (403), intenta inferir desde las notas
   */
  getMyEnrollments: async (estudianteId) => {
    // NO intentar acceder a /enrollments porque requiere Admin y genera error 403
    // Retornar array vacío directamente para evitar errores en consola
    // El estudiante puede ver sus notas usando /grades?subject_id={id} pero necesita conocer el subject_id
    // La mejor solución sería que el backend proporcione un endpoint específico para estudiantes
    return []
  },

  /**
   * Obtiene las materias del estudiante desde las notas que ya tiene
   * Extrae las materias únicas desde las notas obtenidas previamente
   */
  getMySubjectsFromGrades: async (estudianteId, knownSubjectIds = []) => {
    // Si no hay subject_ids conocidos, retornar array vacío
    if (!knownSubjectIds || knownSubjectIds.length === 0) {
      return []
    }
    
    const mySubjects = []
    const subjectMap = new Map()
    
    // Para cada subject_id conocido, intentar obtener notas y extraer la materia
    for (const subjectId of knownSubjectIds) {
      try {
        const grades = await gradeService.getAll({ subject_id: subjectId })
        // Filtrar solo las notas del estudiante
        const myGrades = grades.filter(
          (g) => g.enrollment?.estudiante_id === estudianteId
        )
        
        // Si tiene notas, extraer la materia
        if (myGrades.length > 0 && myGrades[0].enrollment?.subject) {
          const subject = myGrades[0].enrollment.subject
          if (!subjectMap.has(subject.id)) {
            subjectMap.set(subject.id, {
              ...subject,
              enrollment: myGrades[0].enrollment,
            })
          }
        }
      } catch (err) {
        // Silenciar errores individuales
        console.warn(`No se pudieron obtener notas para materia ${subjectId}:`, err)
      }
    }
    
    return Array.from(subjectMap.values())
  },

  /**
   * Obtiene las notas del estudiante en una materia específica
   */
  getGradesBySubject: async (subjectId) => {
    return await gradeService.getAll({ subject_id: subjectId })
  },

  /**
   * Obtiene el estado de una materia para el estudiante
   * Calcula promedio y obtiene información de la materia
   */
  getSubjectStatus: async (subjectId, estudianteId) => {
    try {
      // Obtener notas del estudiante en la materia (requiere subject_id para estudiante)
      const grades = await gradeService.getAll({ subject_id: subjectId })
      
      // Filtrar solo las notas del estudiante
      const myGrades = grades.filter(
        (grade) => grade.enrollment?.estudiante_id === estudianteId
      )
      
      // Calcular promedio
      let promedio = null
      if (myGrades.length > 0) {
        const sum = myGrades.reduce((acc, grade) => acc + parseFloat(grade.nota || 0), 0)
        promedio = sum / myGrades.length
      }
      
      // Obtener información de la materia desde las notas
      const subject = myGrades[0]?.enrollment?.subject || null
      const enrollment = myGrades[0]?.enrollment || null
      
      return {
        subject,
        enrollment,
        grades: myGrades,
        promedio,
        totalGrades: myGrades.length,
      }
    } catch (error) {
      console.error('Error getting subject status:', error)
      // Si falla, retornar estructura vacía en lugar de lanzar error
      if (error.response?.status === 403 || error.response?.status === 401) {
        console.warn('No se tienen permisos para acceder a las notas de esta materia.')
        return {
          subject: null,
          enrollment: null,
          grades: [],
          promedio: null,
          totalGrades: 0,
        }
      }
      throw error
    }
  },
}

// ==================== CLASSROOMS ====================
export const classroomService = {
  getAll: async () => {
    const response = await api.get('/classrooms')
    return response.data
  },

  getById: async (id) => {
    const response = await api.get(`/classrooms/${id}`)
    return response.data
  },

  create: async (data) => {
    const response = await api.post('/classrooms', data)
    return response.data
  },

  update: async (id, data) => {
    const response = await api.put(`/classrooms/${id}`, data)
    return response.data
  },

  delete: async (id) => {
    await api.delete(`/classrooms/${id}`)
  },
}

// ==================== SCHEDULES (horarios) ====================
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

// ==================== ATTENDANCE ====================
export const attendanceService = {
  // Crear sesión de clase
  createSession: async (sessionData) => {
    const response = await api.post('/attendance/sessions', sessionData)
    return response.data
  },

  // Obtener sesión por ID
  getSession: async (sessionId) => {
    const response = await api.get(`/attendance/sessions/${sessionId}`)
    return response.data
  },

  // Obtener todas las sesiones (con filtro opcional de materia)
  getSessionsBySubject: async (subjectId) => {
    const params = subjectId ? { subject_id: subjectId } : {}
    const response = await api.get('/attendance/sessions', { params })
    return response.data
  },

  // Obtener asistencias de una sesión
  getSessionAttendances: async (sessionId) => {
    const response = await api.get(`/attendance/sessions/${sessionId}/attendances`)
    return response.data
  },

  // Actualizar estado de asistencia individual
  updateAttendance: async (attendanceId, estado) => {
    const response = await api.patch(`/attendance/${attendanceId}`, { estado })
    return response.data
  },

  // Obtener estadísticas de una sesión
  getSessionStats: async (sessionId) => {
    const response = await api.get(`/attendance/sessions/${sessionId}/stats`)
    return response.data
  },

  // Historial de asistencia del estudiante actual en una materia (usa token, solo Estudiante)
  getStudentHistory: async (subjectId) => {
    const response = await api.get('/attendance/student/me', {
      params: { subject_id: subjectId },
    })
    return response.data
  },

  // Marcar asistencia masiva
  markAllAttendance: async (sessionId, estado) => {
    const response = await api.post(`/attendance/sessions/${sessionId}/mark-all`, { estado })
    return response.data
  },

  // Guardar asistencias de una sesión
  saveSessionAttendances: async (sessionId, attendanceUpdates) => {
    const response = await api.post(`/attendance/sessions/${sessionId}/save`, attendanceUpdates)
    return response.data
  },
}
