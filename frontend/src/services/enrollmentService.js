/**
 * Enrollment Service
 * Handles student enrollment operations
 */

import api from './api'

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