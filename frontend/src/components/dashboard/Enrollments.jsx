import { useState, useEffect } from 'react'
import { enrollmentService } from '../../services/apiService'
import { Plus, Trash2 } from 'lucide-react'
import EnrollmentModal from '../modals/EnrollmentModal'
import Loading from '../common/Loading'

const Enrollments = () => {
  const [enrollments, setEnrollments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)

  useEffect(() => {
    fetchEnrollments()
  }, [])

  const fetchEnrollments = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await enrollmentService.getAll()
      console.log('Enrollments data:', data) // Debug
      console.log('Number of enrollments:', data?.length || 0) // Debug
      console.log('First enrollment:', data?.[0]) // Debug - ver estructura del primer elemento
      if (data?.[0]) {
        console.log('Estudiante:', data[0].estudiante) // Debug
        console.log('Subject:', data[0].subject) // Debug
      }
      // Asegurar que data es un array
      const enrollmentsArray = Array.isArray(data) ? data : []
      setEnrollments(enrollmentsArray)
      console.log('Enrollments set to state:', enrollmentsArray.length) // Debug
    } catch (err) {
      setError(err.message || 'Error al cargar inscripciones')
      console.error('Error fetching enrollments:', err)
      console.error('Error details:', err.response?.data || err.message)
      setEnrollments([]) // Asegurar que se establece un array vacío en caso de error
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    setIsModalOpen(true)
  }

  const handleDelete = async (enrollmentId) => {
    if (!window.confirm('¿Estás seguro de que deseas eliminar esta inscripción?')) {
      return
    }

    try {
      await enrollmentService.delete(enrollmentId)
      setSuccess('Inscripción eliminada exitosamente')
      fetchEnrollments()
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(
        err.response?.data?.detail || err.message || 'Error al eliminar inscripción'
      )
      setTimeout(() => setError(''), 5000)
    }
  }

  const handleModalSubmit = async (enrollmentData) => {
    try {
      setError('')
      await enrollmentService.create(enrollmentData)
      setSuccess('Inscripción creada exitosamente')
      setIsModalOpen(false)
      fetchEnrollments()
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(
        err.response?.data?.detail || err.message || 'Error al crear inscripción'
      )
      setTimeout(() => setError(''), 5000)
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
            Inscripciones
          </h1>
          <p className="text-gray-600 text-sm">Gestiona las inscripciones de estudiantes</p>
        </div>
        <button
          onClick={handleCreate}
          className="flex items-center space-x-2 px-5 py-3 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-xl hover:from-purple-700 hover:to-purple-800 shadow-lg hover:shadow-xl transition-all duration-200 font-semibold transform hover:scale-105"
        >
          <Plus className="w-5 h-5" />
          <span>Nueva Inscripción</span>
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 text-red-700 px-4 py-3 rounded-lg mb-4 shadow-md">
          <p className="font-medium">{error}</p>
        </div>
      )}

      {success && (
        <div className="bg-green-50 border-l-4 border-green-500 text-green-700 px-4 py-3 rounded-lg mb-4 shadow-md">
          <p className="font-medium">{success}</p>
        </div>
      )}

      <div className="bg-white rounded-2xl shadow-lg overflow-hidden border border-gray-100">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gradient-to-r from-purple-600 to-purple-700">
            <tr>
              <th className="px-6 py-4 text-left text-xs font-semibold text-white uppercase tracking-wider">
                Estudiante
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-white uppercase tracking-wider">
                Materia
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-white uppercase tracking-wider">
                Código Estudiante
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-white uppercase tracking-wider">
                Fecha
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-white uppercase tracking-wider">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {enrollments.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-6 py-4 text-center text-gray-500">
                  No hay inscripciones registradas
                </td>
              </tr>
            ) : (
              enrollments.map((enrollment) => {
                // Manejar datos relacionados que pueden ser null
                const estudianteNombre = enrollment.estudiante?.nombre || 'N/A'
                const estudianteApellido = enrollment.estudiante?.apellido || ''
                const subjectNombre = enrollment.subject?.nombre || 'N/A'
                const codigoEstudiante = enrollment.estudiante?.codigo_institucional || 'N/A'
                
                return (
                  <tr key={enrollment.id} className="hover:bg-purple-50 transition-colors duration-150">
                    <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">
                      {estudianteNombre} {estudianteApellido}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-700">
                      {subjectNombre}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-700">
                      {codigoEstudiante}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-700">
                      {enrollment.created_at
                        ? new Date(enrollment.created_at).toLocaleDateString('es-ES')
                        : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => handleDelete(enrollment.id)}
                        className="p-2 text-red-600 hover:text-white hover:bg-red-600 rounded-lg transition-all duration-200 hover:scale-110"
                        title="Eliminar"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>

      <EnrollmentModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          setError('') // Limpiar errores al cerrar
        }}
        onSubmit={handleModalSubmit}
        existingEnrollments={enrollments}
      />
    </div>
  )
}

export default Enrollments
