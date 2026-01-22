import { useState, useRef } from 'react'
import { X, FileSpreadsheet, Download, Upload } from 'lucide-react'
import { userService } from '../../services'

const BulkImportModal = ({ isOpen, onClose, onSuccess }) => {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const inputRef = useRef(null)

  const reset = () => {
    setFile(null)
    setResult(null)
    setError('')
    if (inputRef.current) inputRef.current.value = ''
  }

  const handleClose = () => {
    reset()
    onClose()
  }

  const handleFileChange = (e) => {
    const f = e.target.files?.[0]
    setFile(f)
    setResult(null)
    setError('')
  }

  const handleImport = async () => {
    if (!file) {
      setError('Seleccione un archivo .xlsx')
      return
    }
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const data = await userService.bulkImport(file)
      
      // Always show the result if we get a BulkImportResult structure
      // This includes both success cases and validation error cases
      if (typeof data === 'object' && ('created' in data || 'updated' in data || 'errors' in data)) {
        setResult(data)
        // Only call onSuccess if there were actual successful operations and no errors
        if (data.errors?.length === 0 && (data.created > 0 || data.updated > 0)) {
          onSuccess?.()
        }
      } else {
        // This shouldn't happen with our current backend, but handle unexpected responses
        setError('Respuesta inesperada del servidor')
      }
    } catch (err) {
      setError(formatError(err, 'importación'))
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async () => {
    setError('')
    try {
      await userService.exportToExcel('Estudiante')
    } catch (err) {
      setError(formatError(err, 'exportación'))
    }
  }

  const handleDownloadTemplate = async () => {
    setError('')
    try {
      await userService.downloadImportTemplate()
    } catch (err) {
      setError(formatError(err, 'descarga de plantilla'))
    }
  }

  /**
   * Format error messages with specific handling for different error types
   * Provides user-friendly messages and technical details for QA
   */
  function formatError(err, operation) {
    if (!err) return `Error durante ${operation}`
    
    // If we have a structured error from our API service
    if (err.message && err.type) {
      return err.message
    }
    
    // Legacy error handling for backward compatibility
    if (typeof err.message === 'string') return err.message
    
    const detail = err.response?.data?.detail
    if (detail) {
      if (Array.isArray(detail)) {
        return detail.map((x) => x.msg || (x.loc && x.loc.join('.'))).filter(Boolean).join('; ')
      }
      return String(detail)
    }
    
    if (Array.isArray(err.message)) {
      return err.message.map((x) => x?.msg || (x?.loc && x.loc.join('.'))).filter(Boolean).join('; ') || `Error durante ${operation}`
    }
    
    return `Error durante ${operation}`
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center p-4 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-800">Importar / Exportar Excel</h2>
          <button onClick={handleClose} className="p-1 text-gray-500 hover:text-gray-700 rounded">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-4 space-y-4">
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-start gap-2">
                <div className="flex-shrink-0 w-5 h-5 text-red-500 mt-0.5">
                  <svg fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="flex-1">
                  <h4 className="text-sm font-medium text-red-800 mb-1">Error en la operación</h4>
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Importar */}
          <section>
            <h3 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
              <Upload className="w-4 h-4" /> Importar estudiantes
            </h3>
            <div className="flex gap-2">
              <input
                ref={inputRef}
                type="file"
                accept=".xlsx"
                onChange={handleFileChange}
                className="flex-1 text-sm text-gray-600 file:mr-2 file:py-2 file:px-3 file:rounded file:border-0 file:bg-purple-50 file:text-purple-700"
              />
              <button
                onClick={handleImport}
                disabled={loading || !file}
                className="px-3 py-2 bg-purple-600 text-white rounded-lg text-sm font-medium hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
              >
                {loading ? 'Procesando…' : 'Importar'}
              </button>
            </div>
            {loading && (
              <div className="mt-2 h-1.5 bg-gray-200 rounded overflow-hidden">
                <div className="h-full w-2/3 bg-purple-500 animate-pulse" />
              </div>
            )}
          </section>

          {/* Resultado importación */}
          {result && (
            <section className="p-3 bg-gray-50 rounded-lg border border-gray-200">
              <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                <div className="w-4 h-4">
                  {result.errors?.length === 0 ? (
                    <svg className="text-green-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  ) : (
                    <svg className="text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  )}
                </div>
                Resultado de la importación
              </h4>
              
              <div className="grid grid-cols-3 gap-4 mb-3">
                <div className="text-center">
                  <div className="text-lg font-bold text-green-600">{result.created ?? 0}</div>
                  <div className="text-xs text-gray-600">Creados</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-blue-600">{result.updated ?? 0}</div>
                  <div className="text-xs text-gray-600">Actualizados</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-red-600">{result.errors?.length ?? 0}</div>
                  <div className="text-xs text-gray-600">Errores</div>
                </div>
              </div>
              
              {result.errors?.length > 0 && (
                <div className="mt-3 p-2 bg-red-50 rounded border border-red-200">
                  <h5 className="text-xs font-semibold text-red-800 mb-2">Detalles de errores:</h5>
                  <ul className="text-xs text-red-700 space-y-1 max-h-32 overflow-y-auto">
                    {result.errors.map((e, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="flex-shrink-0 font-medium">Fila {e.row}:</span>
                        <span className="flex-1">
                          <span className="font-medium">{e.field}</span> – {e.message}
                          {e.value != null && (
                            <span className="text-red-600 ml-1">
                              (valor: "{String(e.value).slice(0, 30)}{String(e.value).length > 30 ? '...' : ''}")
                            </span>
                          )}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {result.errors?.length === 0 && (result.created > 0 || result.updated > 0) && (
                <div className="mt-2 p-2 bg-green-50 rounded border border-green-200">
                  <p className="text-xs text-green-800">
                    ✅ Importación completada exitosamente
                  </p>
                </div>
              )}
            </section>
          )}

          {/* Exportar y plantilla */}
          <section className="pt-2 border-t border-gray-200">
            <h3 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
              <FileSpreadsheet className="w-4 h-4" /> Descargas
            </h3>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={handleExport}
                className="flex items-center gap-2 px-3 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700"
              >
                <Download className="w-4 h-4" /> Exportar usuarios
              </button>
              <button
                onClick={handleDownloadTemplate}
                className="flex items-center gap-2 px-3 py-2 bg-gray-600 text-white rounded-lg text-sm font-medium hover:bg-gray-700"
              >
                <Download className="w-4 h-4" /> Descargar plantilla
              </button>
            </div>
          </section>
        </div>

        <div className="p-4 border-t border-gray-200 flex justify-end">
          <button
            onClick={handleClose}
            className="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300 font-medium"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  )
}

export default BulkImportModal
