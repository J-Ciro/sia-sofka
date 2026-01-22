/**
 * Classroom Service
 * Handles classroom management operations
 */

import api from './api'

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