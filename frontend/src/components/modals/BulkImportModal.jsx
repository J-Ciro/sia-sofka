import { useState, useRef } from 'react'
import { X, FileSpreadsheet, Download, Upload } from 'lucide-react'
import { userService } from '../../services/apiService'

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
      setResult(data)
      if (data.errors?.length === 0 && (data.created > 0 || data.updated > 0)) {
        onSuccess?.()
      }
    } catch (err) {
      setError(formatErr(err, 'Error al importar'))
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async () => {
    setError('')
    try {
      await userService.exportToExcel('Estudiante')
    } catch (err) {
      setError(formatErr(err, 'Error al exportar'))
    }
  }

  const handleDownloadTemplate = async () => {
    setError('')
    try {
      await userService.downloadImportTemplate()
    } catch (err) {
      setError(formatErr(err, 'Error al descargar plantilla'))
    }
  }

  function formatErr(err, fallback) {
    if (!err) return fallback
    if (typeof err.message === 'string') return err.message
    const d = err.response?.data?.detail
    if (d) return Array.isArray(d) ? d.map((x) => x.msg || (x.loc && x.loc.join('.'))).filter(Boolean).join('; ') : String(d)
    if (Array.isArray(err.message)) return err.message.map((x) => x?.msg || (x?.loc && x.loc.join('.'))).filter(Boolean).join('; ') || fallback
    return fallback
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
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
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
              <h4 className="text-sm font-semibold text-gray-700 mb-2">Resultado</h4>
              <p className="text-sm text-gray-700">
                <span className="font-medium text-green-600">{result.created ?? 0}</span> creados,{' '}
                <span className="font-medium text-blue-600">{result.updated ?? 0}</span> actualizados,{' '}
                <span className="font-medium text-red-600">{result.errors?.length ?? 0}</span> errores
              </p>
              {result.errors?.length > 0 && (
                <ul className="mt-2 text-xs text-red-700 space-y-1 max-h-32 overflow-y-auto">
                  {result.errors.map((e, i) => (
                    <li key={i}>
                      Fila {e.row}: {e.field} – {e.message}
                      {e.value != null && ` (${String(e.value).slice(0, 30)}…)`}
                    </li>
                  ))}
                </ul>
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
