import { useState, useEffect } from 'react'
import { subjectService, profesorService, enrollmentService } from '../../services'
import { useAuth } from '../../context/AuthContext'
import { BookOpen, Users, FileText, AlertCircle } from 'lucide-react'
import Loading from '../common/Loading'

const ProfesorSubjects = () => {
  const { user } = useAuth()
  const [subjects, setSubjects] = useState([])
  const [selectedSubject, setSelectedSubject] = useState(null)
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(true)
  const [loadingStudents, setLoadingStudents] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (user?.id) {
      fetchSubjects()
    }
  }, [user?.id])

  useEffect(() => {
    if (selectedSubject?.id) {
      fetchStudents(selectedSubject.id)
    }
  }, [selectedSubject?.id])

  const fetchSubjects = async () => {
    try {
      setLoading(true)
      setError('')
      // Intentar obtener materias asignadas usando el servicio específico
      const data = await profesorService.getAssignedSubjects(user?.id)
      
      if (!data || data.length === 0) {
        setError('No tienes materias asignadas o no tienes permisos para verlas. Contacta al administrador.')
        setSubjects([])
        return
      }
      
      setSubjects(data)
      
      if (data.length > 0 && !selectedSubject) {
        setSelectedSubject(data[0])
      }
    } catch (err) {
      console.error('Error fetching subjects:', err)
      setError(err.message || 'Error al cargar materias asignadas')
      setSubjects([])
    } finally {
      setLoading(false)
    }
  }

  const fetchStudents = async (subjectId) => {
    if (!subjectId) return
    
    try {
      setLoadingStudents(true)
      setError('')
      const data = await profesorService.getStudentsBySubject(subjectId)
      setStudents(data || [])
    } catch (err) {
      console.error('Error fetching students:', err)
      // No mostrar error aquí, solo loguear y dejar array vacío
      setStudents([])
    } finally {
      setLoadingStudents(false)
    }
  }


  if (loading) {
    return <Loading />
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-purple-800 bg-clip-text text-transparent mb-1">
          Mis Materias Asignadas
        </h1>
        <p className="text-gray-600 text-sm">Gestiona tus materias y estudiantes</p>
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 text-red-700 px-4 py-3 rounded-lg mb-4 shadow-md flex items-center space-x-2">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <p className="font-medium">{error}</p>
        </div>
      )}

      {subjects.length === 0 ? (
        <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 text-center">
          <BookOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-700 mb-2">No tienes materias asignadas</h3>
          <p className="text-gray-500">Contacta al administrador para que te asigne materias.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Lista de Materias */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100">
              <div className="p-4 border-b border-gray-200 bg-gradient-to-r from-purple-600 to-purple-700">
                <h2 className="text-lg font-semibold text-white flex items-center space-x-2">
                  <BookOpen className="w-5 h-5" />
                  <span>Materias</span>
                </h2>
              </div>
              <div className="p-4 space-y-2 max-h-[600px] overflow-y-auto">
                {subjects.map((subject) => (
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
                ))}
              </div>
            </div>
          </div>

          {/* Detalles de Materia y Estudiantes */}
          <div className="lg:col-span-2">
            {selectedSubject ? (
              <div className="space-y-6">
                {/* Información de la Materia */}
                <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900 mb-2">{selectedSubject?.nombre || 'Sin nombre'}</h2>
                      <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                        <span><strong>Código:</strong> {selectedSubject?.codigo_institucional || 'N/A'}</span>
                        <span><strong>Créditos:</strong> {selectedSubject?.numero_creditos || 0}</span>
                        {selectedSubject?.horario && (
                          <span><strong>Horario:</strong> {selectedSubject.horario}</span>
                        )}
                      </div>
                      {selectedSubject?.descripcion && (
                        <p className="mt-3 text-gray-700">{selectedSubject.descripcion}</p>
                      )}
                    </div>
                  </div>
                </div>

                {/* Lista de Estudiantes */}
                <div className="bg-white rounded-2xl shadow-lg border border-gray-100">
                  <div className="p-4 border-b border-gray-200 bg-gradient-to-r from-blue-600 to-blue-700">
                    <h3 className="text-lg font-semibold text-white flex items-center space-x-2">
                      <Users className="w-5 h-5" />
                      <span>Estudiantes Inscritos ({students.length})</span>
                    </h3>
                  </div>
                  {loadingStudents ? (
                    <div className="p-8 text-center">
                      <Loading />
                    </div>
                  ) : students.length === 0 ? (
                    <div className="p-8 text-center text-gray-500">
                      <Users className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                      <p>No hay estudiantes inscritos en esta materia</p>
                    </div>
                  ) : (
                    <div className="p-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {students.map((student) => (
                          <div
                            key={student?.id || Math.random()}
                            className="p-4 bg-gradient-to-br from-purple-50 to-blue-50 rounded-xl border border-purple-200 hover:shadow-md transition-shadow"
                          >
                            <div className="font-semibold text-gray-900">
                              {student?.nombre || ''} {student?.apellido || ''}
                            </div>
                            <div className="text-sm text-gray-600 mt-1">
                              {student?.codigo_institucional || 'N/A'}
                            </div>
                            {student?.email && (
                              <div className="text-xs text-gray-500 mt-1">{student.email}</div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
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

export default ProfesorSubjects

