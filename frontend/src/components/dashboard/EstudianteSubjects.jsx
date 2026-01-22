import { useState, useEffect } from 'react'
import { estudianteService } from '../../services'
import { useAuth } from '../../context/AuthContext'
import { BookOpen, GraduationCap, TrendingUp, AlertCircle, FileText } from 'lucide-react'
import Loading from '../common/Loading'
import { reportService } from '../../services'

const EstudianteSubjects = () => {
  const { user } = useAuth()
  const [enrollments, setEnrollments] = useState([])
  const [selectedSubject, setSelectedSubject] = useState(null)
  const [subjectStatus, setSubjectStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [loadingStatus, setLoadingStatus] = useState(false)
  const [error, setError] = useState('')
  const [generatingReport, setGeneratingReport] = useState(false)

  useEffect(() => {
    if (user?.id) {
      fetchEnrollments()
    }
  }, [user?.id])

  useEffect(() => {
    if (selectedSubject?.id) {
      fetchSubjectStatus(selectedSubject.id)
    }
  }, [selectedSubject?.id])

  const fetchEnrollments = async () => {
    try {
      setLoading(true)
      setError('')
      
      // Usar el endpoint /enrollments/me para obtener las inscripciones del estudiante
      const enrollmentsData = await estudianteService.getMyEnrollments(user.id)
      
      if (enrollmentsData && enrollmentsData.length > 0) {
        setEnrollments(enrollmentsData)
        // Seleccionar automáticamente la primera materia
        if (enrollmentsData[0]?.subject) {
          setSelectedSubject(enrollmentsData[0].subject)
        }
      } else {
        setEnrollments([])
        setError('No estás inscrito a ninguna materia. Contacta con tu profesor.')
      }
    } catch (err) {
      console.error('Error fetching enrollments:', err)
      setEnrollments([])
      setError('No se pudieron cargar tus materias inscritas. Contacta con tu profesor.')
    } finally {
      setLoading(false)
    }
  }


  const fetchSubjectStatus = async (subjectId) => {
    if (!subjectId) return
    
    try {
      setLoadingStatus(true)
      setError('')
      const status = await estudianteService.getSubjectStatus(subjectId, user?.id)
      setSubjectStatus(status || {
        subject: null,
        enrollment: null,
        grades: [],
        promedio: null,
        totalGrades: 0,
      })
    } catch (err) {
      console.error('Error fetching subject status:', err)
      // No mostrar error aquí, solo establecer estado vacío
      setSubjectStatus({
        subject: null,
        enrollment: null,
        grades: [],
        promedio: null,
        totalGrades: 0,
      })
    } finally {
      setLoadingStatus(false)
    }
  }

  const handleGenerateReport = async (format = 'pdf') => {
    try {
      setGeneratingReport(true)
      setError('')
      
      const response = await reportService.getGeneralReport(format)
      
      const studentName = `${user.nombre}_${user.apellido}`.toLowerCase().replace(/\s+/g, '_')

      let blob
      let filename
      
      if (format === 'json') {
        const jsonContent = typeof response === 'string' ? JSON.parse(response) : response
        const jsonString = JSON.stringify(jsonContent, null, 2)
        blob = new Blob([jsonString], { type: 'application/json' })
        filename = `reporte_general_${studentName}.json`
      } else if (format === 'pdf') {
        blob = response instanceof Blob ? response : new Blob([response], { type: 'application/pdf' })
        filename = `reporte_general_${studentName}.pdf`
      } else if (format === 'html') {
        if (response instanceof Blob) {
          blob = response
        } else if (typeof response === 'string') {
          blob = new Blob([response], { type: 'text/html' })
        } else {
          blob = new Blob([JSON.stringify(response)], { type: 'text/html' })
        }
        filename = `reporte_general_${studentName}.html`
      }

      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (err) {
      console.error('Error generating report:', err)
        setError(err.response?.data?.detail || err.message || 'Error al generar el reporte')
    } finally {
      setGeneratingReport(false)
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
            Mis Materias
          </h1>
          <p className="text-gray-600 text-sm">Consulta tus materias inscritas y calificaciones</p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => handleGenerateReport('pdf')}
            disabled={generatingReport}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 flex items-center space-x-2"
            title="Generar Reporte PDF"
          >
            <FileText className="w-4 h-4" />
            <span>Reporte PDF</span>
          </button>
          <button
            onClick={() => handleGenerateReport('html')}
            disabled={generatingReport}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center space-x-2"
            title="Generar Reporte HTML"
          >
            <FileText className="w-4 h-4" />
            <span>Reporte HTML</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 text-red-700 px-4 py-3 rounded-lg mb-4 shadow-md flex items-center space-x-2">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <p className="font-medium">{error}</p>
        </div>
      )}

      {enrollments.length === 0 ? (
        <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 text-center">
          <BookOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-700 mb-2">No estás inscrito a ninguna materia</h3>
          <p className="text-gray-500 mb-4">
            Contacta con tu profesor o administrador para inscribirte en las materias correspondientes.
          </p>
          <p className="text-sm text-gray-400">
            Una vez inscrito, podrás ver aquí todas tus materias y calificaciones.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Lista de Materias */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100">
              <div className="p-4 border-b border-gray-200 bg-gradient-to-r from-purple-600 to-purple-700">
                <h2 className="text-lg font-semibold text-white flex items-center space-x-2">
                  <BookOpen className="w-5 h-5" />
                  <span>Materias ({enrollments.length})</span>
                </h2>
              </div>
              <div className="p-4 space-y-2 max-h-[600px] overflow-y-auto">
                {enrollments.map((enrollment) => {
                  const subject = enrollment?.subject || enrollment
                  if (!subject) return null
                  return (
                    <button
                      key={subject?.id || Math.random()}
                      onClick={() => subject && setSelectedSubject(subject)}
                      className={`w-full text-left p-4 rounded-xl transition-all duration-200 ${
                        selectedSubject?.id === subject?.id
                          ? 'bg-gradient-to-r from-purple-600 to-purple-700 text-white shadow-lg'
                          : 'bg-gray-50 hover:bg-purple-50 text-gray-700 border border-gray-200'
                      }`}
                    >
                      <div className="font-semibold">{subject?.nombre || 'Sin nombre'}</div>
                      <div className={`text-sm mt-1 ${
                        selectedSubject?.id === subject?.id ? 'text-purple-100' : 'text-gray-500'
                      }`}>
                        {subject?.codigo_institucional || 'N/A'} • {subject?.numero_creditos || 0} créditos
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>
          </div>

          {/* Detalles de Materia y Notas */}
          <div className="lg:col-span-2">
            {selectedSubject ? (
              <div className="space-y-6">
                {/* Información de la Materia */}
                {/* <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">{selectedSubject?.nombre || 'Sin nombre'}</h2>
                  <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-4">
                    <span><strong>Código:</strong> {selectedSubject?.codigo_institucional || 'N/A'}</span>
                    <span><strong>Créditos:</strong> {selectedSubject?.numero_creditos || 0}</span>
                    {selectedSubject?.horario && (
                      <span><strong>Horario:</strong> {selectedSubject.horario}</span>
                    )}
                  </div>
                  {selectedSubject?.descripcion && (
                    <p className="text-gray-700">{selectedSubject.descripcion}</p>
                  )}
                </div> */}

                {/* Estado y Notas */}
                {loadingStatus ? (
                  <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 text-center">
                    <Loading />
                  </div>
                ) : subjectStatus ? (
                  <div className="space-y-4">
                    {/* Promedio */}
                    {subjectStatus.promedio !== null && (
                      <div className="bg-gradient-to-r from-purple-600 to-purple-700 rounded-2xl shadow-lg p-6 text-white">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-purple-200 text-sm mb-1">Promedio de la Materia</p>
                            <p className="text-4xl font-bold">{subjectStatus.promedio.toFixed(2)}</p>
                          </div>
                          <TrendingUp className="w-12 h-12 text-purple-200" />
                        </div>
                      </div>
                    )}

                    {/* Lista de Notas */}
                    <div className="bg-white rounded-2xl shadow-lg border border-gray-100">
                      <div className="p-4 border-b border-gray-200 bg-gradient-to-r from-blue-600 to-blue-700">
                        <h3 className="text-lg font-semibold text-white flex items-center space-x-2">
                          <GraduationCap className="w-5 h-5" />
                          <span>Mis Notas ({subjectStatus.grades.length})</span>
                        </h3>
                      </div>
                      {subjectStatus.grades.length === 0 ? (
                        <div className="p-8 text-center text-gray-500">
                          <GraduationCap className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                          <p>No hay notas registradas para esta materia</p>
                        </div>
                      ) : (
                        <div className="p-4">
                          <div className="space-y-3">
                            {subjectStatus.grades.map((grade) => (
                              <div
                                key={grade?.id || Math.random()}
                                className="p-4 bg-gradient-to-br from-purple-50 to-blue-50 rounded-xl border border-purple-200 hover:shadow-md transition-shadow"
                              >
                                <div className="flex justify-between items-center">
                                  <div>
                                    <div className="font-semibold text-gray-900">Período: {grade?.periodo || 'N/A'}</div>
                                    {grade?.fecha && (
                                      <div className="text-sm text-gray-600 mt-1">
                                        Fecha: {new Date(grade.fecha).toLocaleDateString('es-ES')}
                                      </div>
                                    )}
                                    {grade?.observaciones && (
                                      <div className="text-sm text-gray-600 mt-1">{grade.observaciones}</div>
                                    )}
                                  </div>
                                  <div className="text-right">
                                    <span className={`px-4 py-2 text-lg font-bold rounded-full shadow-md ${
                                      (grade?.nota || 0) >= 4.5 ? 'bg-gradient-to-r from-green-500 to-green-600 text-white' :
                                      (grade?.nota || 0) >= 3.5 ? 'bg-gradient-to-r from-yellow-500 to-yellow-600 text-white' :
                                      'bg-gradient-to-r from-red-500 to-red-600 text-white'
                                    }`}>
                                      {grade?.nota || 0}
                                    </span>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 text-center">
                    <p className="text-gray-500">No se pudo cargar el estado de la materia</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 text-center">
                <BookOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">Selecciona una materia para ver detalles</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default EstudianteSubjects

