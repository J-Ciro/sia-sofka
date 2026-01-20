import { useState, useEffect } from 'react'
import { X } from 'lucide-react'

const ClassroomModal = ({ isOpen, onClose, classroom, onSubmit }) => {
  const [formData, setFormData] = useState({
    nombre: '',
    capacidad: '',
    ubicacion: '',
  })
  const [errors, setErrors] = useState({})

  useEffect(() => {
    if (classroom) {
      setFormData({
        nombre: classroom.nombre || '',
        capacidad: String(classroom.capacidad ?? ''),
        ubicacion: classroom.ubicacion || '',
      })
    } else {
      setFormData({ nombre: '', capacidad: '', ubicacion: '' })
    }
    setErrors({})
  }, [classroom, isOpen])

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: '' }))
  }

  const validate = () => {
    const e = {}
    if (!formData.nombre?.trim()) e.nombre = 'El nombre es requerido'
    const cap = parseInt(formData.capacidad, 10)
    if (!formData.capacidad || isNaN(cap) || cap < 1 || cap > 500) {
      e.capacidad = 'Capacidad entre 1 y 500'
    }
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!validate()) return
    onSubmit({
      nombre: formData.nombre.trim(),
      capacidad: parseInt(formData.capacidad, 10),
      ubicacion: formData.ubicacion?.trim() || null,
    })
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-900">
            {classroom ? 'Editar aula' : 'Nueva aula'}
          </h2>
          <button onClick={onClose} className="p-1 rounded-lg text-gray-500 hover:bg-gray-100">
            <X className="w-5 h-5" />
          </button>
        </div>
        {classroom?.codigo && (
          <p className="mb-4 text-sm text-gray-500">Código (asignado automáticamente): <strong>{classroom.codigo}</strong></p>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nombre *</label>
            <input
              type="text"
              name="nombre"
              value={formData.nombre}
              onChange={handleChange}
              placeholder="Ej. Aula 101"
              className={`w-full rounded-lg border px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 ${errors.nombre ? 'border-red-500' : 'border-gray-300'}`}
            />
            {errors.nombre && <p className="mt-1 text-sm text-red-600">{errors.nombre}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Capacidad *</label>
            <input
              type="number"
              name="capacidad"
              value={formData.capacidad}
              onChange={handleChange}
              min="1"
              max="500"
              placeholder="40"
              className={`w-full rounded-lg border px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 ${errors.capacidad ? 'border-red-500' : 'border-gray-300'}`}
            />
            {errors.capacidad && <p className="mt-1 text-sm text-red-600">{errors.capacidad}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Ubicación</label>
            <input
              type="text"
              name="ubicacion"
              value={formData.ubicacion}
              onChange={handleChange}
              placeholder="Ej. Edificio A, primer piso"
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            />
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50">
              Cancelar
            </button>
            <button type="submit" className="px-4 py-2 rounded-lg bg-purple-600 text-white hover:bg-purple-700">
              {classroom ? 'Actualizar' : 'Crear'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ClassroomModal
