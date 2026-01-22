/**
 * Estudiante Service
 * Handles student-specific operations
 */

import api from './api'
import { gradeService } from './gradeService'

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
   * Obtiene las materias inscritas del estudiante usando el endpoint /enrollments/me
   */
  getMyEnrollments: async (estudianteId) => {
    try {
      const response = await api.get('/enrollments/me')
      return response.data || []
    } catch (error) {
      console.error('Error fetching my enrollments:', error)
      // Si hay error 403 o similar, retornar array vacío
      if (error.response?.status === 403 || error.response?.status === 401) {
        return []
      }
      throw error
    }
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