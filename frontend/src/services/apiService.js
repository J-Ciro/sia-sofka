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

  // Obtener todas las sesiones de una materia
  getSessionsBySubject: async (subjectId) => {
    const response = await api.get('/attendance/sessions', { params: { subject_id: subjectId } })
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

  // Obtener historial de asistencia de un estudiante
  getStudentHistory: async (studentId, subjectId) => {
    const response = await api.get(`/attendance/student/${studentId}`, {
      params: { subject_id: subjectId },
    })
    return response.data
  },

  // Marcar asistencia masiva
  markAllAttendance: async (sessionId, estado) => {
    const response = await api.post(`/attendance/sessions/${sessionId}/mark-all`, { estado })
    return response.data
  },
}
