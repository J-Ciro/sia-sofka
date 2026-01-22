import { useState, useEffect, useMemo } from 'react'
import { X } from 'lucide-react'
import { userService, subjectService } from '../../services'

const EnrollmentModal = ({ isOpen, onClose, onSubmit, existingEnrollments = [] }) => {
  const [formData, setFormData] = useState({
    estudiante_id: '',
    subject_id: '',
  })
  const [estudiantes, setEstudiantes] = useState([])
  const [subjects, setSubjects] = useState([])
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)
  
  // Asegurar que existingEnrollments sea un array
  const enrollments = Array.isArray(existingEnrollments) ? existingEnrollments : []

  useEffect(() => {
    if (isOpen) {
      fetchData()
    }
  }, [isOpen])

  useEffect(() => {
    if (!isOpen) {
      setFormData({
        estudiante_id: '',
        subject_id: '',
      })
      setErrors({})
    }
  }, [isOpen])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [users, subjectsData] = await Promise.all([
        userService.getAll(),
        subjectService.getAll(),
      ])
      const estudiantesList = users.filter((u) => u.role === 'Estudiante')
      setEstudiantes(estudiantesList)
      setSubjects(subjectsData)
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => {
      const newData = { ...prev, [name]: value }
      
      // Validar duplicado en tiempo real cuando ambos campos están llenos
      if (newData.estudiante_id && newData.subject_id && enrollments.length > 0) {
        const exists = enrollments.some(
          (e) => 
            e.estudiante_id === parseInt(newData.estudiante_id) && 
            e.subject_id === parseInt(newData.subject_id)
        )
        if (exists) {
          setErrors((prev) => ({
            ...prev,
            subject_id: 'El estudiante ya está inscrito en esta materia',
          }))
        } else {
          setErrors((prev) => {
            const newErrors = { ...prev }
            if (newErrors.subject_id === 'El estudiante ya está inscrito en esta materia') {
              delete newErrors.subject_id
            }
            return newErrors
          })
        }
      }
      
      return newData
    })
    
    // Limpiar error del campo que cambió (excepto si es el error de duplicado)
    if (errors[name] && errors[name] !== 'El estudiante ya está inscrito en esta materia') {
      setErrors((prev) => ({ ...prev, [name]: '' }))
    }
  }

  const validate = () => {
    const newErrors = {}
    
    if (!formData.estudiante_id) {
      newErrors.estudiante_id = 'Debe seleccionar un estudiante'
    }
    if (!formData.subject_id) {
      newErrors.subject_id = 'Debe seleccionar una materia'
    }
    
    // Validar si ya existe la inscripción
    if (formData.estudiante_id && formData.subject_id && enrollments.length > 0) {
      const exists = enrollments.some(
        (e) => 
          e.estudiante_id === parseInt(formData.estudiante_id) && 
          e.subject_id === parseInt(formData.subject_id)
      )
      if (exists) {
        newErrors.subject_id = 'El estudiante ya está inscrito en esta materia'
      }
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (validate()) {
      const dataToSubmit = {
        estudiante_id: parseInt(formData.estudiante_id),
        subject_id: parseInt(formData.subject_id),
      }
      onSubmit(dataToSubmit)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Nueva Inscripción</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Estudiante *
            </label>
            <select
              name="estudiante_id"
              value={formData.estudiante_id}
              onChange={handleChange}
              className={`w-full px-3 py-2 border rounded-md ${
                errors.estudiante_id ? 'border-red-500' : 'border-gray-300'
              }`}
              required
              disabled={loading}
            >
              <option value="">Seleccione un estudiante</option>
              {estudiantes.map((estudiante) => (
                <option key={estudiante.id} value={estudiante.id}>
                  {estudiante.nombre} {estudiante.apellido} - {estudiante.codigo_institucional}
                </option>
              ))}
            </select>
            {errors.estudiante_id && (
              <p className="text-red-500 text-xs mt-1">{errors.estudiante_id}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Materia *
            </label>
            <select
              name="subject_id"
              value={formData.subject_id}
              onChange={handleChange}
              className={`w-full px-3 py-2 border rounded-md ${
                errors.subject_id ? 'border-red-500' : 'border-gray-300'
              }`}
              required
              disabled={loading}
            >
              <option value="">Seleccione una materia</option>
              {subjects.map((subject) => (
                <option key={subject.id} value={subject.id}>
                  {subject.nombre} - {subject.codigo_institucional}
                </option>
              ))}
            </select>
            {errors.subject_id && (
              <p className="text-red-500 text-xs mt-1">{errors.subject_id}</p>
            )}
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
              Crear Inscripción
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default EnrollmentModal

