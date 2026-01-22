/**
 * Grade Service
 * Handles student grade operations
 */

import api from './api'

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