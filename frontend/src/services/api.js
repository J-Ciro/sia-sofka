import axios from 'axios'
import { API_BASE_URL } from '../config/constants'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 segundos de timeout
})

// Interceptor para agregar el token a las peticiones
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor para manejar errores de respuesta
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Manejo de errores de autenticación
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      // Solo redirigir si no estamos ya en la página de login
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }

    // Manejo de errores del servidor (verificar primero para evitar tratar errores de validación como errores de red)
    if (error.response) {
      // El servidor respondió con un código de error
      const { status, data } = error.response
      
      // Errores 4xx (cliente) - incluye errores de validación (400) y conflictos (422)
      if (status >= 400 && status < 500) {
        console.error(`Error del cliente (${status}):`, data)
        
        // Extraer mensaje de error de diferentes formatos
        let errorMessage = 'Ha ocurrido un error'
        
        // FastAPI validation errors pueden venir en diferentes formatos
        if (data?.detail) {
          if (typeof data.detail === 'string') {
            errorMessage = data.detail
          } else if (Array.isArray(data.detail)) {
            // Pydantic validation errors vienen como array
            const messages = data.detail.map(err => {
              if (typeof err === 'object' && err.msg) {
                return `${err.loc?.join('.') || ''}: ${err.msg}`
              }
              return String(err)
            })
            errorMessage = messages.join('. ')
          } else if (typeof data.detail === 'object' && data.detail.message) {
            errorMessage = data.detail.message
          }
        } else if (data?.message) {
          errorMessage = data.message
        }
        
        return Promise.reject({
          message: errorMessage,
          status,
          data,
          response: error.response,
        })
      }
      
      // Errores 5xx (servidor)
      if (status >= 500) {
        console.error(`Error del servidor (${status}):`, data)
        return Promise.reject({
          message: 'Error del servidor. Por favor, intenta más tarde.',
          status,
          data,
        })
      }
    }

    // Manejo de errores de red (solo si no hay respuesta del servidor)
    if (error.code === 'ECONNABORTED' || error.message === 'Network Error' || (!error.response && error.code)) {
      console.error('Error de conexión: No se pudo conectar con el servidor')
      return Promise.reject({
        message: 'Error de conexión. Por favor, verifica tu conexión a internet.',
        isNetworkError: true,
      })
    }

    // Error sin respuesta del servidor y sin código de red
    return Promise.reject({
      message: error.message || 'Error desconocido. Por favor, intenta nuevamente.',
      originalError: error,
    })
  }
)

export default api
