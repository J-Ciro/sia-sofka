/**
 * Report Service
 * Handles report generation operations
 */

import api from './api'

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