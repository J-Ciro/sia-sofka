import { useState, useEffect } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { classroomService } from '../../services'
import { Plus, Edit, Trash2 } from 'lucide-react'
import ClassroomModal from '../modals/ClassroomModal'
import Loading from '../common/Loading'

export default function Aulas() {
  const { user } = useAuth()
  const [classrooms, setClassrooms] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [modalOpen, setModalOpen] = useState(false)
  const [selected, setSelected] = useState(null)

  useEffect(() => {
    if (user?.role === 'Admin') fetchClassrooms()
    else setLoading(false)
  }, [user?.role])

  const fetchClassrooms = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await classroomService.getAll()
      setClassrooms(Array.isArray(data) ? data : [])
    } catch (err) {
      setError(err?.message || 'Error al cargar aulas')
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    setSelected(null)
    setModalOpen(true)
  }

  const handleEdit = (c) => {
    setSelected(c)
    setModalOpen(true)
  }

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar esta aula? No se puede si tiene horarios asignados.')) return
    try {
      await classroomService.delete(id)
      setSuccess('Aula eliminada')
      fetchClassrooms()
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(err?.message || 'Error al eliminar')
      setTimeout(() => setError(''), 5000)
    }
  }

  const handleSubmit = async (data) => {
    try {
      setError('')
      if (selected) {
        await classroomService.update(selected.id, data)
        setSuccess('Aula actualizada')
      } else {
        await classroomService.create(data)
        setSuccess('Aula creada')
      }
      setModalOpen(false)
      fetchClassrooms()
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(err?.message || 'Error al guardar')
      setTimeout(() => setError(''), 5000)
    }
  }

  if (loading) return <Loading />
  if (user?.role !== 'Admin') return <Navigate to="/" replace />

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap justify-between items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Aulas (banco de salones)</h1>
          <p className="text-gray-600 text-sm">Crea y gestiona las aulas. Los profesores eligen de este banco al asignar horarios.</p>
        </div>
        <button
          onClick={handleCreate}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-purple-600 text-white hover:bg-purple-700 shadow-sm"
        >
          <Plus className="w-5 h-5" />
          Nueva aula
        </button>
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">{error}</div>
      )}
      {success && (
        <div className="p-3 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">{success}</div>
      )}

      <div className="bg-white rounded-xl shadow border border-gray-100 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Código</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Nombre</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Capacidad</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Ubicación</th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {classrooms.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-4 py-8 text-center text-gray-500">
                  No hay aulas. Crea una para que los profesores puedan asignar salones a sus horarios.
                </td>
              </tr>
            ) : (
              classrooms.map((c) => (
                <tr key={c.id} className="hover:bg-purple-50/50">
                  <td className="px-4 py-3 font-medium text-gray-900">{c.codigo}</td>
                  <td className="px-4 py-3 text-gray-700">{c.nombre}</td>
                  <td className="px-4 py-3 text-gray-700">{c.capacidad}</td>
                  <td className="px-4 py-3 text-gray-600">{c.ubicacion || '–'}</td>
                  <td className="px-4 py-3 text-right">
                    <button onClick={() => handleEdit(c)} className="p-2 text-purple-600 hover:bg-purple-100 rounded-lg" title="Editar">
                      <Edit className="w-4 h-4" />
                    </button>
                    <button onClick={() => handleDelete(c.id)} className="p-2 text-red-600 hover:bg-red-50 rounded-lg ml-1" title="Eliminar">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <ClassroomModal
        isOpen={modalOpen}
        onClose={() => { setModalOpen(false); setSelected(null) }}
        classroom={selected}
        onSubmit={handleSubmit}
      />
    </div>
  )
}
