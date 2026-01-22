/**
 * Profesor Service
 * Handles professor-specific operations
 */

import api from './api'
import { gradeService } from './gradeService'

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