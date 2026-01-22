/**
 * Attendance Service
 * Handles attendance management operations
 */

import api from './api'

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