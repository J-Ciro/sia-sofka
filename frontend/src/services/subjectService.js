/**
 * Subject Service
 * Handles subject management operations
 */

import api from './api'

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