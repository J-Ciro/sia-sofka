import { useState, useEffect } from 'react'
import { X } from 'lucide-react'
import { userService } from '../../services'

const SubjectModal = ({ isOpen, onClose, subject, onSubmit }) => {
  const [formData, setFormData] = useState({
    nombre: '',
    codigo_institucional: '',
    numero_creditos: '',
    horario: '',
    descripcion: '',
    profesor_id: '',
  })
  const [profesores, setProfesores] = useState([])
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (isOpen) {
      fetchProfesores()
    }
  }, [isOpen])

  useEffect(() => {
    if (subject) {
      setFormData({
        nombre: subject.nombre || '',
        codigo_institucional: subject.codigo_institucional || '',
        numero_creditos: subject.numero_creditos || '',
        horario: subject.horario || '',
        descripcion: subject.descripcion || '',
        profesor_id: subject.profesor_id || '',
      })
    } else {
      setFormData({
        nombre: '',
        codigo_institucional: '',
        numero_creditos: '',
        horario: '',
        descripcion: '',
        profesor_id: '',
      })
    }
    setErrors({})
  }, [subject, isOpen])

  const fetchProfesores = async () => {
    try {
      setLoading(true)
      const users = await userService.getAll()
      const profesoresList = users.filter((u) => u.role === 'Profesor')
      setProfesores(profesoresList)
    } catch (error) {
      console.error('Error fetching profesores:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }))
    }
  }

  const validate = () => {
    const newErrors = {}
    
    if (!formData.nombre) newErrors.nombre = 'El nombre es requerido'
    // codigo_institucional es opcional - se autogenera si no se proporciona
    if (!formData.numero_creditos) {
      newErrors.numero_creditos = 'El número de créditos es requerido'
    }
    if (formData.numero_creditos && (isNaN(formData.numero_creditos) || formData.numero_creditos < 1)) {
      newErrors.numero_creditos = 'El número de créditos debe ser mayor a 0'
    }
    if (!formData.profesor_id) {
      newErrors.profesor_id = 'Debe seleccionar un profesor'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (validate()) {
      const dataToSubmit = {
        nombre: formData.nombre,
        numero_creditos: parseInt(formData.numero_creditos),
        profesor_id: parseInt(formData.profesor_id),
        horario: formData.horario || null,
        descripcion: formData.descripcion || null,
      }
      // Solo incluir codigo_institucional si se proporciona (no vacío)
      if (formData.codigo_institucional && formData.codigo_institucional.trim()) {
        dataToSubmit.codigo_institucional = formData.codigo_institucional.trim()
      }
      onSubmit(dataToSubmit)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">
            {subject ? 'Editar Materia' : 'Nueva Materia'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nombre *
              </label>
              <input
                type="text"
                name="nombre"
                value={formData.nombre}
                onChange={handleChange}
                className={`w-full px-3 py-2 border rounded-md ${
                  errors.nombre ? 'border-red-500' : 'border-gray-300'
                }`}
                required
              />
              {errors.nombre && (
                <p className="text-red-500 text-xs mt-1">{errors.nombre}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Código Institucional
                <span className="text-gray-400 text-xs ml-1">(opcional - se autogenera si no se proporciona)</span>
              </label>
              <input
                type="text"
                name="codigo_institucional"
                value={formData.codigo_institucional}
                onChange={handleChange}
                placeholder="Se generará automáticamente"
                className={`w-full px-3 py-2 border rounded-md ${
                  errors.codigo_institucional ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.codigo_institucional && (
                <p className="text-red-500 text-xs mt-1">{errors.codigo_institucional}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Número de Créditos *
              </label>
              <input
                type="number"
                name="numero_creditos"
                value={formData.numero_creditos}
                onChange={handleChange}
                min="1"
                className={`w-full px-3 py-2 border rounded-md ${
                  errors.numero_creditos ? 'border-red-500' : 'border-gray-300'
                }`}
                required
              />
              {errors.numero_creditos && (
                <p className="text-red-500 text-xs mt-1">{errors.numero_creditos}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Horario
              </label>
              <input
                type="text"
                name="horario"
                value={formData.horario}
                onChange={handleChange}
                placeholder="Ej: Lunes 8:00-10:00"
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Profesor *
              </label>
              <select
                name="profesor_id"
                value={formData.profesor_id}
                onChange={handleChange}
                className={`w-full px-3 py-2 border rounded-md ${
                  errors.profesor_id ? 'border-red-500' : 'border-gray-300'
                }`}
                required
                disabled={loading}
              >
                <option value="">Seleccione un profesor</option>
                {profesores.map((profesor) => (
                  <option key={profesor.id} value={profesor.id}>
                    {profesor.nombre} {profesor.apellido} - {profesor.codigo_institucional}
                  </option>
                ))}
              </select>
              {errors.profesor_id && (
                <p className="text-red-500 text-xs mt-1">{errors.profesor_id}</p>
              )}
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Descripción
              </label>
              <textarea
                name="descripcion"
                value={formData.descripcion}
                onChange={handleChange}
                rows="3"
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
          </div>

          <div className="flex justify-end space-x-2 mt-6">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-200 rounded hover:bg-gray-300"
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="px-4 py-2 text-white bg-blue-600 rounded hover:bg-blue-700"
            >
              {subject ? 'Actualizar' : 'Crear'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default SubjectModal
