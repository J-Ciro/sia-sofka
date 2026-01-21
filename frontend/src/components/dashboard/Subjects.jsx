import { useState, useEffect } from 'react'
import { subjectService } from '../../services/apiService'
import { Plus, Edit, Trash2 } from 'lucide-react'
import SubjectModal from '../modals/SubjectModal'
import Loading from '../common/Loading'

const Subjects = () => {
  const [subjects, setSubjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedSubject, setSelectedSubject] = useState(null)

  useEffect(() => {
    fetchSubjects()
  }, [])

  const fetchSubjects = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await subjectService.getAll()
      setSubjects(data)
    } catch (err) {
          setError(err.response?.data?.detail || err.message || 'Error al cargar materias')
      console.error('Error fetching subjects:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    setSelectedSubject(null)
    setIsModalOpen(true)
  }

  const handleEdit = (subject) => {
    setSelectedSubject(subject)
    setIsModalOpen(true)
  }

  const handleDelete = async (subjectId) => {
    if (!window.confirm('¿Estás seguro de que deseas eliminar esta materia?')) {
      return
    }

    try {
      await subjectService.delete(subjectId)
      setSuccess('Materia eliminada exitosamente')
      fetchSubjects()
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
          setError(err.response?.data?.detail || err.message || 'Error al eliminar materia')
      setTimeout(() => setError(''), 5000)
    }
  }

  const handleModalSubmit = async (subjectData) => {
    try {
      setError('')
      if (selectedSubject) {
        await subjectService.update(selectedSubject.id, subjectData)
        setSuccess('Materia actualizada exitosamente')
      } else {
        await subjectService.create(subjectData)
        setSuccess('Materia creada exitosamente')
      }
      setIsModalOpen(false)
      fetchSubjects()
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
          setError(err.response?.data?.detail || err.message || 'Error al guardar materia')
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
            Materias
          </h1>
          <p className="text-gray-600 text-sm">Gestiona las materias académicas</p>
        </div>
        <button
          onClick={handleCreate}
          className="flex items-center space-x-2 px-5 py-3 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-xl hover:from-purple-700 hover:to-purple-800 shadow-lg hover:shadow-xl transition-all duration-200 font-semibold transform hover:scale-105"
        >
          <Plus className="w-5 h-5" />
          <span>Nueva Materia</span>
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
                Nombre
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-white uppercase tracking-wider">
                Código
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-white uppercase tracking-wider">
                Créditos
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-white uppercase tracking-wider">
                Horario
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-white uppercase tracking-wider">
                Profesor
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-white uppercase tracking-wider">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {subjects.length === 0 ? (
              <tr>
                <td colSpan="6" className="px-6 py-4 text-center text-gray-500">
                  No hay materias registradas
                </td>
              </tr>
            ) : (
              subjects.map((subject) => (
                <tr key={subject.id} className="hover:bg-purple-50 transition-colors duration-150">
                  <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">{subject.nombre}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {subject.codigo_institucional}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {subject.numero_creditos}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {subject.horario || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {subject.profesor?.nombre} {subject.profesor?.apellido}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex items-center space-x-3">
                      <button
                        onClick={() => handleEdit(subject)}
                        className="p-2 text-purple-600 hover:text-white hover:bg-purple-600 rounded-lg transition-all duration-200 hover:scale-110"
                        title="Editar"
                      >
                        <Edit className="w-5 h-5" />
                      </button>
                      <button
                        onClick={() => handleDelete(subject.id)}
                        className="p-2 text-red-600 hover:text-white hover:bg-red-600 rounded-lg transition-all duration-200 hover:scale-110"
                        title="Eliminar"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <SubjectModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          setSelectedSubject(null)
        }}
        subject={selectedSubject}
        onSubmit={handleModalSubmit}
      />
    </div>
  )
}

export default Subjects
