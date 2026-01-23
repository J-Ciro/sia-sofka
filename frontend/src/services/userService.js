/**
 * User Service
 * Handles user management operations including bulk import/export
 */

import api from './api'
import axios from 'axios'

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

  /** Importar estudiantes desde Excel. Retorna { created, updated, errors }. En 400 con errores, res.data ya tiene ese formato. */
  bulkImport: async (file) => {
    const fd = new FormData()
    fd.append('file', file)
    
    // Use axios directly with custom config to bypass interceptors for this specific call
    const config = {
      method: 'post',
      url: '/users/bulk-import',
      data: fd,
      baseURL: api.defaults.baseURL,
      headers: {
        ...api.defaults.headers,
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
      transformRequest: [(data, headers) => {
        if (data instanceof FormData) delete headers['Content-Type']
        return data
      }],
      // Accept 200 (success) and 400 (validation errors with BulkImportResult)
      validateStatus: (status) => status === 200 || status === 400,
    }
    
    try {
      const response = await axios(config)
      
      // Success case (200)
      if (response.status === 200) {
        return response.data
      }
      
      // Handle 400 responses
      if (response.status === 400) {
        // Check if response is a BulkImportResult (has created/updated/errors)
        // BulkImportResult has created, updated, and errors fields
        const isBulkImportResult = response.data && 
          (typeof response.data.created === 'number' || 
           typeof response.data.updated === 'number' || 
           Array.isArray(response.data.errors))
        
        if (isBulkImportResult) {
          // It's a BulkImportResult with validation errors (row-level errors)
          return response.data
        } else {
          // It's an error message (like file format, size, corruption, etc.)
          // These are file-level errors that should be shown as error, not as result
          const errorDetail = response.data?.detail
          const errorMessage = userService._getSpecificErrorMessage(errorDetail, 400, 'importación')
          
          throw {
            message: errorMessage,
            type: userService._getErrorType(errorDetail, 400),
            originalError: errorDetail,
            status: 400,
            response: response,
          }
        }
      }
      
      // Should not reach here, but return data if we do
      return response.data
    } catch (error) {
      // Handle specific error types from backend
      const errorDetail = error.response?.data?.detail || error.originalError
      const status = error.response?.status || error.status || 500
      
      // If error already has structured format, re-throw it
      if (error.message && error.type) {
        throw error
      }
      
      // Create structured error object with specific messages
      const structuredError = {
        message: userService._getSpecificErrorMessage(errorDetail, status, 'importación'),
        type: userService._getErrorType(errorDetail, status),
        originalError: errorDetail,
        status: status,
        response: error.response,
      }
      
      throw structuredError
    }
  },

  /** Exportar usuarios a Excel. Descarga el archivo. */
  exportToExcel: async (role = null) => {
    try {
      const params = role ? { role } : {}
      const res = await api.get('/users/export', { params, responseType: 'blob' })
      const url = window.URL.createObjectURL(res.data)
      const a = document.createElement('a')
      a.href = url
      a.download = `usuarios${role ? `_${role}` : ''}.xlsx`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      const errorDetail = error.response?.data?.detail
      const status = error.response?.status
      
      throw {
        message: userService._getSpecificErrorMessage(errorDetail, status, 'exportación'),
        type: userService._getErrorType(errorDetail, status),
        originalError: errorDetail,
        status: status,
        response: error.response,
      }
    }
  },

  /** Descargar plantilla Excel para importación. */
  downloadImportTemplate: async () => {
    try {
      const res = await api.get('/users/template', { responseType: 'blob' })
      const url = window.URL.createObjectURL(res.data)
      const a = document.createElement('a')
      a.href = url
      a.download = 'plantilla_estudiantes.xlsx'
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      const errorDetail = error.response?.data?.detail
      const status = error.response?.status
      
      throw {
        message: userService._getSpecificErrorMessage(errorDetail, status, 'descarga de plantilla'),
        type: userService._getErrorType(errorDetail, status),
        originalError: errorDetail,
        status: status,
        response: error.response,
      }
    }
  },

  /**
   * Get specific error message based on backend response
   * @private
   */
  _getSpecificErrorMessage: (detail, status, operation) => {
    if (!detail) {
      return userService._getGenericErrorMessage(status, operation)
    }

    const detailStr = typeof detail === 'string' ? detail : JSON.stringify(detail)
    
    // File format errors
    if (detailStr.includes('Solo se aceptan archivos') || detailStr.includes('no es válido')) {
      return detail
    }
    
    // File size errors
    if (detailStr.includes('supera el límite') || detailStr.includes('MB')) {
      return detail
    }
    
    // File corruption errors
    if (detailStr.includes('corrupto') || detailStr.includes('no se puede leer')) {
      return detail
    }
    
    // Empty file errors
    if (detailStr.includes('vacío') || detailStr.includes('no contiene datos')) {
      return detail
    }
    
    // Missing columns errors
    if (detailStr.includes('Faltan') && detailStr.includes('columnas')) {
      return detail
    }
    
    // Too many rows errors
    if (detailStr.includes('filas') && detailStr.includes('límite')) {
      return detail
    }
    
    // Database errors
    if (detailStr.includes('base de datos') || detailStr.includes('Database')) {
      return `Error en la base de datos durante ${operation}. Por favor, inténtelo de nuevo.`
    }
    
    // Permission errors
    if (status === 403 || detailStr.includes('permisos') || detailStr.includes('Forbidden')) {
      return `No tiene permisos suficientes para realizar esta ${operation}`
    }
    
    // Authentication errors
    if (status === 401 || detailStr.includes('Authentication') || detailStr.includes('Unauthorized')) {
      return 'Su sesión ha expirado. Por favor, inicie sesión nuevamente.'
    }
    
    // Network timeout
    if (status === 408 || detailStr.includes('timeout') || detailStr.includes('Timeout')) {
      return `Tiempo de espera agotado durante ${operation}. El archivo puede ser muy grande.`
    }
    
    // Server errors
    if (status >= 500) {
      return `Error interno del servidor durante ${operation}. Por favor, contacte al administrador.`
    }
    
    // Return original detail if it's a clear message
    if (typeof detail === 'string' && detail.length > 0) {
      return detail
    }
    
    return userService._getGenericErrorMessage(status, operation)
  },

  /**
   * Get error type for categorization
   * @private
   */
  _getErrorType: (detail, status) => {
    if (!detail && !status) return 'unknown'
    
    const detailStr = typeof detail === 'string' ? detail : JSON.stringify(detail)
    
    if (detailStr.includes('Solo se aceptan archivos') || detailStr.includes('no es válido')) {
      return 'file_format'
    }
    if (detailStr.includes('supera el límite') || detailStr.includes('MB')) {
      return 'file_size'
    }
    if (detailStr.includes('corrupto') || detailStr.includes('no se puede leer')) {
      return 'file_corrupted'
    }
    if (detailStr.includes('vacío') || detailStr.includes('no contiene datos')) {
      return 'file_empty'
    }
    if (detailStr.includes('Faltan') && detailStr.includes('columnas')) {
      return 'missing_columns'
    }
    if (detailStr.includes('filas') && detailStr.includes('límite')) {
      return 'too_many_rows'
    }
    if (detailStr.includes('base de datos') || detailStr.includes('Database')) {
      return 'database_error'
    }
    if (status === 403) return 'permission_denied'
    if (status === 401) return 'authentication_required'
    if (status === 408) return 'timeout'
    if (status >= 500) return 'server_error'
    if (status >= 400) return 'client_error'
    
    return 'unknown'
  },

  /**
   * Get generic error message based on status code
   * @private
   */
  _getGenericErrorMessage: (status, operation) => {
    switch (status) {
      case 400:
        return `Datos inválidos para ${operation}. Verifique el archivo y vuelva a intentar.`
      case 401:
        return 'Su sesión ha expirado. Por favor, inicie sesión nuevamente.'
      case 403:
        return `No tiene permisos para realizar esta ${operation}.`
      case 404:
        return 'Recurso no encontrado.'
      case 408:
        return `Tiempo de espera agotado durante ${operation}.`
      case 413:
        return 'El archivo es demasiado grande.'
      case 422:
        return `Los datos proporcionados no son válidos para ${operation}.`
      case 429:
        return 'Demasiadas solicitudes. Por favor, espere un momento.'
      case 500:
        return `Error interno del servidor durante ${operation}.`
      case 502:
        return 'Error de conexión con el servidor.'
      case 503:
        return 'Servicio no disponible temporalmente.'
      case 504:
        return 'Tiempo de espera del servidor agotado.'
      default:
        return `Error inesperado durante ${operation}. Por favor, inténtelo de nuevo.`
    }
  },
}