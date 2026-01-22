import { useState, useEffect } from 'react'
import { reportService, userService, profesorService, subjectService } from '../../services'
import { useAuth } from '../../context/AuthContext'
import { Download, FileText, Users, AlertCircle, CheckCircle, BookOpen } from 'lucide-react'
import Loading from '../common/Loading'

const Reports = () => {
  const { user } = useAuth()
  const [students, setStudents] = useState([])
  const [subjects, setSubjects] = useState([])
  const [selectedStudentId, setSelectedStudentId] = useState('')
  const [selectedSubjectId, setSelectedSubjectId] = useState('')
  const [format, setFormat] = useState('pdf')
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    if (user?.role === 'Admin') {
      fetchStudents()
    } else if (user?.role === 'Profesor') {
      fetchSubjects()
    } else {
      setLoading(false)
    }
  }, [])

  const fetchStudents = async () => {
    try {
      setLoading(true)
      setError('')
      const allUsers = await userService.getAll()
      // Filtrar solo estudiantes
      const estudiantes = allUsers.filter(u => u.role === 'Estudiante')
      setStudents(estudiantes)
    } catch (err) {
      setError(err.message || 'Error al cargar estudiantes')
      console.error('Error fetching students:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchSubjects = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await profesorService.getAssignedSubjects(user.id)
      setSubjects(data)
    } catch (err) {
      setError(err.message || 'Error al cargar materias')
      console.error('Error fetching subjects:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateReport = async () => {
    // Validar según el rol
    if (user?.role === 'Admin' && !selectedStudentId) {
      setError('Debe seleccionar un estudiante para generar el reporte')
      return
    }
    if (user?.role === 'Profesor' && !selectedSubjectId) {
      setError('Debe seleccionar una materia para generar el reporte')
      return
    }

    setError('')
    setSuccess('')
    setGenerating(true)

    try {
      let response
      let filename
      
      if (user?.role === 'Admin') {
        // Reporte de estudiante (Admin)
        response = await reportService.getStudentReport(
          parseInt(selectedStudentId),
          format
        )
        const selectedStudent = students.find(s => s.id === parseInt(selectedStudentId))
        const studentName = selectedStudent
          ? `${selectedStudent.nombre}_${selectedStudent.apellido}`.toLowerCase().replace(/\s+/g, '_')
          : `estudiante_${selectedStudentId}`
        filename = `reporte_${studentName}`
      } else if (user?.role === 'Profesor') {
        // Reporte de materia (Profesor)
        response = await reportService.getSubjectReport(
          parseInt(selectedSubjectId),
          format
        )
        const selectedSubject = subjects.find(s => s.id === parseInt(selectedSubjectId))
        const subjectName = selectedSubject
          ? `${selectedSubject.nombre}_${selectedSubject.codigo_institucional}`.toLowerCase().replace(/\s+/g, '_')
          : `materia_${selectedSubjectId}`
        filename = `reporte_materia_${subjectName}`
      } else {
        // Reporte general (Estudiante)
        response = await reportService.getGeneralReport(format)
        const studentName = `${user.nombre}_${user.apellido}`.toLowerCase().replace(/\s+/g, '_')
        filename = `reporte_general_${studentName}`
      }

      let blob
      let mimeType

      if (format === 'json') {
        // Para JSON, el backend devuelve un objeto parseado
        const jsonContent = typeof response === 'string' ? JSON.parse(response) : response
        const jsonString = JSON.stringify(jsonContent, null, 2)
        blob = new Blob([jsonString], { type: 'application/json' })
        filename = `${filename}.json`
        mimeType = 'application/json'
      } else if (format === 'pdf') {
        // Para PDF, el backend devuelve un Blob directamente
        blob = response instanceof Blob ? response : new Blob([response], { type: 'application/pdf' })
        filename = `${filename}.pdf`
        mimeType = 'application/pdf'
      } else if (format === 'html') {
        // Para HTML, el backend devuelve un string o Blob
        if (response instanceof Blob) {
          blob = response
        } else if (typeof response === 'string') {
          blob = new Blob([response], { type: 'text/html' })
        } else {
          blob = new Blob([JSON.stringify(response)], { type: 'text/html' })
        }
        filename = `${filename}.html`
        mimeType = 'text/html'
      }

      // Crear URL del blob y descargar
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      setSuccess('Reporte generado y descargado exitosamente')
      setTimeout(() => setSuccess(''), 5000)
    } catch (err) {
      console.error('Error generating report:', err)
      setError(
        err.message || 'Error al generar el reporte. Verifique que el estudiante tenga notas registradas.'
      )
      setTimeout(() => setError(''), 7000)
    } finally {
      setGenerating(false)
    }
  }

  if (loading) {
    return <Loading />
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-purple-800 bg-clip-text text-transparent mb-1">
            {user?.role === 'Admin' 
              ? 'Reportes de Estudiantes'
              : user?.role === 'Profesor'
              ? 'Reportes de Materias'
              : 'Mi Reporte General'}
          </h1>
          <p className="text-gray-600 text-sm">
            {user?.role === 'Admin'
              ? 'Genera reportes académicos de estudiantes en diferentes formatos.'
              : user?.role === 'Profesor'
              ? 'Genera reportes de tus materias asignadas en diferentes formatos.'
              : 'Genera tu reporte académico general en diferentes formatos.'}
          </p>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 text-red-700 px-4 py-3 rounded-lg mb-4 shadow-md flex items-center space-x-2">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <p className="font-medium">{error}</p>
        </div>
      )}

      {success && (
        <div className="bg-green-50 border-l-4 border-green-500 text-green-700 px-4 py-3 rounded-lg mb-4 shadow-md flex items-center space-x-2">
          <CheckCircle className="w-5 h-5 flex-shrink-0" />
          <p className="font-medium">{success}</p>
        </div>
      )}

      <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
        <div className="mb-6">
          <h2 className="text-2xl font-semibold text-gray-800 mb-2">Configuración del Reporte</h2>
          <p className="text-gray-600 text-sm">Selecciona el estudiante y el formato del reporte que deseas generar.</p>
        </div>

        <div className="space-y-6">
          {/* Selección según rol */}
          {user?.role === 'Admin' && (
            <div>
              <label htmlFor="student" className="block text-sm font-medium text-gray-700 mb-2">
                Seleccionar Estudiante <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Users className="h-5 w-5 text-gray-400" />
                </div>
                <select
                  id="student"
                  value={selectedStudentId}
                  onChange={(e) => {
                    setSelectedStudentId(e.target.value)
                    setError('')
                  }}
                  disabled={generating}
                  className="block w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition appearance-none bg-white disabled:bg-gray-100 disabled:cursor-not-allowed"
                >
                  <option value="">-- Seleccione un estudiante --</option>
                  {students.map((student) => (
                    <option key={student.id} value={student.id}>
                      {student.nombre} {student.apellido} - {student.codigo_institucional}
                    </option>
                  ))}
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
                  <svg className="h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
              {selectedStudentId && (
                <p className="mt-2 text-sm text-gray-500">
                  Estudiante seleccionado: <span className="font-medium">
                    {students.find(s => s.id === parseInt(selectedStudentId))?.nombre} {students.find(s => s.id === parseInt(selectedStudentId))?.apellido}
                  </span>
                </p>
              )}
            </div>
          )}

          {user?.role === 'Profesor' && (
            <div>
              <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-2">
                Seleccionar Materia <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <BookOpen className="h-5 w-5 text-gray-400" />
                </div>
                <select
                  id="subject"
                  value={selectedSubjectId}
                  onChange={(e) => {
                    setSelectedSubjectId(e.target.value)
                    setError('')
                  }}
                  disabled={generating}
                  className="block w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition appearance-none bg-white disabled:bg-gray-100 disabled:cursor-not-allowed"
                >
                  <option value="">-- Seleccione una materia --</option>
                  {subjects.map((subject) => (
                    <option key={subject.id} value={subject.id}>
                      {subject.nombre} - {subject.codigo_institucional}
                    </option>
                  ))}
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
                  <svg className="h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
              {selectedSubjectId && (
                <p className="mt-2 text-sm text-gray-500">
                  Materia seleccionada: <span className="font-medium">
                    {subjects.find(s => s.id === parseInt(selectedSubjectId))?.nombre}
                  </span>
                </p>
              )}
            </div>
          )}

          {user?.role === 'Estudiante' && (
            <div className="bg-blue-50 border-l-4 border-blue-500 text-blue-700 px-4 py-3 rounded-lg">
              <p className="font-medium">Se generará tu reporte general con todas tus materias y calificaciones.</p>
            </div>
          )}

          {/* Selección de Formato */}
          <div>
            <label htmlFor="format" className="block text-sm font-medium text-gray-700 mb-2">
              Formato del Reporte
            </label>
            <div className="grid grid-cols-3 gap-4">
              <label className={`relative flex flex-col items-center justify-center p-4 border-2 rounded-lg cursor-pointer transition-all duration-200 ${
                format === 'pdf'
                  ? 'border-purple-500 bg-purple-50'
                  : 'border-gray-200 hover:border-purple-300 hover:bg-gray-50'
              } ${generating ? 'opacity-50 cursor-not-allowed' : ''}`}>
                <input
                  type="radio"
                  name="format"
                  value="pdf"
                  checked={format === 'pdf'}
                  onChange={(e) => setFormat(e.target.value)}
                  disabled={generating}
                  className="sr-only"
                />
                <FileText className={`w-8 h-8 mb-2 ${format === 'pdf' ? 'text-purple-600' : 'text-gray-400'}`} />
                <span className={`font-medium ${format === 'pdf' ? 'text-purple-700' : 'text-gray-700'}`}>PDF</span>
                <span className="text-xs text-gray-500 mt-1">Para imprimir</span>
              </label>

              <label className={`relative flex flex-col items-center justify-center p-4 border-2 rounded-lg cursor-pointer transition-all duration-200 ${
                format === 'html'
                  ? 'border-purple-500 bg-purple-50'
                  : 'border-gray-200 hover:border-purple-300 hover:bg-gray-50'
              } ${generating ? 'opacity-50 cursor-not-allowed' : ''}`}>
                <input
                  type="radio"
                  name="format"
                  value="html"
                  checked={format === 'html'}
                  onChange={(e) => setFormat(e.target.value)}
                  disabled={generating}
                  className="sr-only"
                />
                <FileText className={`w-8 h-8 mb-2 ${format === 'html' ? 'text-purple-600' : 'text-gray-400'}`} />
                <span className={`font-medium ${format === 'html' ? 'text-purple-700' : 'text-gray-700'}`}>HTML</span>
                <span className="text-xs text-gray-500 mt-1">Para visualizar</span>
              </label>

              <label className={`relative flex flex-col items-center justify-center p-4 border-2 rounded-lg cursor-pointer transition-all duration-200 ${
                format === 'json'
                  ? 'border-purple-500 bg-purple-50'
                  : 'border-gray-200 hover:border-purple-300 hover:bg-gray-50'
              } ${generating ? 'opacity-50 cursor-not-allowed' : ''}`}>
                <input
                  type="radio"
                  name="format"
                  value="json"
                  checked={format === 'json'}
                  onChange={(e) => setFormat(e.target.value)}
                  disabled={generating}
                  className="sr-only"
                />
                <FileText className={`w-8 h-8 mb-2 ${format === 'json' ? 'text-purple-600' : 'text-gray-400'}`} />
                <span className={`font-medium ${format === 'json' ? 'text-purple-700' : 'text-gray-700'}`}>JSON</span>
                <span className="text-xs text-gray-500 mt-1">Para datos</span>
              </label>
            </div>
          </div>

          {/* Botón de Generar */}
          <div className="pt-4 border-t border-gray-200">
            <button
              onClick={handleGenerateReport}
              disabled={
                generating ||
                (user?.role === 'Admin' && !selectedStudentId) ||
                (user?.role === 'Profesor' && !selectedSubjectId)
              }
              className="w-full flex items-center justify-center space-x-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-xl hover:from-purple-700 hover:to-purple-800 shadow-lg hover:shadow-xl transition-all duration-200 font-semibold transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              {generating ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Generando reporte...</span>
                </>
              ) : (
                <>
                  <Download className="w-5 h-5" />
                  <span>Generar y Descargar Reporte</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Información adicional */}
      <div className="mt-8 bg-gradient-to-r from-purple-50 to-blue-50 rounded-2xl shadow-lg p-6 border border-purple-100">
        <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center space-x-2">
          <FileText className="w-5 h-5 text-purple-600" />
          <span>Información sobre los Reportes</span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
          <div>
            <p className="font-medium text-gray-800 mb-1">📄 Formato PDF</p>
            <p>Ideal para imprimir y compartir. Incluye todas las notas y promedios del estudiante.</p>
          </div>
          <div>
            <p className="font-medium text-gray-800 mb-1">🌐 Formato HTML</p>
            <p>Visualiza el reporte directamente en tu navegador. Perfecto para revisión digital.</p>
          </div>
          <div>
            <p className="font-medium text-gray-800 mb-1">📊 Formato JSON</p>
            <p>Datos estructurados para análisis o integración con otras aplicaciones.</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Reports

