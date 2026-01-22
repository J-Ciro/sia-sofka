import { useState, useEffect } from 'react'
import { X } from 'lucide-react'
import { enrollmentService, profesorService } from '../../services'
import { useAuth } from '../../context/AuthContext'

const GradeModal = ({ isOpen, onClose, grade, subjectId, onSubmit }) => {
  const { user } = useAuth()
  const [formData, setFormData] = useState({
    enrollment_id: '',
    nota: '',
    periodo: '',
    fecha: '',
    observaciones: '',
  })
  const [enrollments, setEnrollments] = useState([])
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (isOpen && subjectId) {
      fetchEnrollments()
    }
  }, [isOpen, subjectId])

  useEffect(() => {
    if (grade) {
      setFormData({
        enrollment_id: grade.enrollment_id || '',
        nota: grade.nota || '',
        periodo: grade.periodo || '',
        fecha: grade.fecha || '',
        observaciones: grade.observaciones || '',
      })
    } else {
      setFormData({
        enrollment_id: '',
        nota: '',
        periodo: '',
        fecha: new Date().toISOString().split('T')[0],
        observaciones: '',
      })
    }
    setErrors({})
  }, [grade, isOpen])

  const fetchEnrollments = async () => {
    if (!subjectId) {
      setEnrollments([])
      return
    }
    
    try {
      setLoading(true)
      
      // Usar el nuevo endpoint para obtener enrollments de la materia
      if (user?.role === 'Profesor') {
        try {
          // Usar el endpoint específico para enrollments de la materia
          const enrollments = await profesorService.getEnrollmentsBySubject(subjectId)
          setEnrollments(enrollments || [])
        } catch (err) {
          console.error('Error fetching enrollments by subject:', err)
          setEnrollments([])
        }
      } else if (user?.role === 'Admin') {
        // Para Admin, usar el endpoint de enrollments por materia
        try {
          const enrollments = await profesorService.getEnrollmentsBySubject(subjectId)
          setEnrollments(enrollments || [])
        } catch (err) {
          console.error('Error fetching enrollments by subject:', err)
          // Fallback: obtener todos y filtrar
          try {
            const data = await enrollmentService.getAll()
            const filtered = subjectId
              ? data.filter((e) => e.subject_id === subjectId)
              : data
            setEnrollments(filtered)
          } catch (adminErr) {
            console.error('Error fetching enrollments as admin:', adminErr)
            setEnrollments([])
          }
        }
      } else {
        // Para otros roles, no se pueden obtener enrollments
        setEnrollments([])
      }
    } catch (error) {
      console.error('Error fetching enrollments:', error)
      setEnrollments([])
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
    
    if (!formData.enrollment_id) {
      newErrors.enrollment_id = 'Debe seleccionar una inscripción'
    }
    if (!formData.nota) {
      newErrors.nota = 'La nota es requerida'
    } else {
      const nota = parseFloat(formData.nota)
      if (isNaN(nota) || nota < 0 || nota > 5) {
        newErrors.nota = 'La nota debe estar entre 0 y 5'
      }
    }
    if (!formData.periodo) {
      newErrors.periodo = 'El período es requerido'
    }
    if (!formData.fecha) {
      newErrors.fecha = 'La fecha es requerida'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (validate()) {
      const dataToSubmit = {
        ...formData,
        enrollment_id: parseInt(formData.enrollment_id),
        nota: parseFloat(formData.nota),
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
            {grade ? 'Editar Nota' : 'Nueva Nota'}
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
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Inscripción *
              </label>
              <select
                name="enrollment_id"
                value={formData.enrollment_id}
                onChange={handleChange}
                className={`w-full px-3 py-2 border rounded-md ${
                  errors.enrollment_id ? 'border-red-500' : 'border-gray-300'
                }`}
                required
                disabled={loading || !!grade}
              >
                <option value="">Seleccione una inscripción</option>
                {enrollments.map((enrollment) => (
                  <option key={enrollment.id} value={enrollment.id}>
                    {enrollment.estudiante?.nombre} {enrollment.estudiante?.apellido} - {enrollment.subject?.nombre}
                  </option>
                ))}
              </select>
              {errors.enrollment_id && (
                <p className="text-red-500 text-xs mt-1">{errors.enrollment_id}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nota (0-5) *
              </label>
              <input
                type="number"
                name="nota"
                value={formData.nota}
                onChange={handleChange}
                min="0"
                max="5"
                step="0.01"
                className={`w-full px-3 py-2 border rounded-md ${
                  errors.nota ? 'border-red-500' : 'border-gray-300'
                }`}
                required
              />
              {errors.nota && (
                <p className="text-red-500 text-xs mt-1">{errors.nota}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Período *
              </label>
              <input
                type="text"
                name="periodo"
                value={formData.periodo}
                onChange={handleChange}
                placeholder="Ej: 2024-1"
                className={`w-full px-3 py-2 border rounded-md ${
                  errors.periodo ? 'border-red-500' : 'border-gray-300'
                }`}
                required
              />
              {errors.periodo && (
                <p className="text-red-500 text-xs mt-1">{errors.periodo}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Fecha *
              </label>
              <input
                type="date"
                name="fecha"
                value={formData.fecha}
                onChange={handleChange}
                className={`w-full px-3 py-2 border rounded-md ${
                  errors.fecha ? 'border-red-500' : 'border-gray-300'
                }`}
                required
              />
              {errors.fecha && (
                <p className="text-red-500 text-xs mt-1">{errors.fecha}</p>
              )}
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Observaciones
              </label>
              <textarea
                name="observaciones"
                value={formData.observaciones}
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
              {grade ? 'Actualizar' : 'Crear'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default GradeModal
