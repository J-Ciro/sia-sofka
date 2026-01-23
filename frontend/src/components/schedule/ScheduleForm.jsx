import { useState, useEffect } from 'react'
import { X } from 'lucide-react'
import { scheduleService, subjectService, classroomService } from '../../services'
import TimeInput from '../common/TimeInput'

const DIAS = [
  { value: 1, label: 'Lunes' },
  { value: 2, label: 'Martes' },
  { value: 3, label: 'Miércoles' },
  { value: 4, label: 'Jueves' },
  { value: 5, label: 'Viernes' },
  { value: 6, label: 'Sábado' },
  { value: 7, label: 'Domingo' },
]

function toTimeStr(v) {
  if (!v) return ''
  const s = String(v).trim()
  if (/^\d{1,2}:\d{2}$/.test(s)) return `${s}:00`
  return s
}

export default function ScheduleForm({ isOpen, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    subject_id: '',
    classroom_id: '',
    dia_semana: 1,
    hora_inicio: '08:00',
    hora_fin: '10:00',
    fecha_especifica: '', // New field for specific date
    es_fecha_especifica: false, // Toggle for date-specific mode
  })
  const [subjects, setSubjects] = useState([])
  const [classrooms, setClassrooms] = useState([])
  const [loading, setLoading] = useState(false)
  const [loadOpts, setLoadOpts] = useState(true)
  const [errors, setErrors] = useState({})
  const [conflictError, setConflictError] = useState('')

  useEffect(() => {
    if (!isOpen) return
    setFormData({ 
      subject_id: '', 
      classroom_id: '', 
      dia_semana: 1, 
      hora_inicio: '08:00', // 8:00 AM
      hora_fin: '10:00',    // 10:00 AM
      fecha_especifica: '',
      es_fecha_especifica: false,
    })
    setErrors({})
    setConflictError('')
  }, [isOpen])

  useEffect(() => {
    if (!isOpen) return
    let cancelled = false
    async function load() {
      setLoadOpts(true)
      try {
        const [s, c] = await Promise.all([subjectService.getAll(), classroomService.getAll()])
        if (!cancelled) {
          setSubjects(Array.isArray(s) ? s : [])
          setClassrooms(Array.isArray(c) ? c : [])
        }
      } catch (e) {
        if (!cancelled) console.error('Error loading options:', e)
      } finally {
        if (!cancelled) setLoadOpts(false)
      }
    }
    load()
    return () => { cancelled = true }
  }, [isOpen])

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    
    setFormData((prev) => {
      const updates = { ...prev }
      
      if (type === 'checkbox') {
        updates[name] = checked
        // If toggling date-specific mode off, clear the specific date
        if (name === 'es_fecha_especifica' && !checked) {
          updates.fecha_especifica = ''
        }
      } else if (name === 'fecha_especifica') {
        updates[name] = value
        // Auto-calculate dia_semana from selected date
        if (value) {
          const selectedDate = new Date(value)
          const dayOfWeek = selectedDate.getDay() // 0 = Sunday, 1 = Monday, etc.
          // Convert to our format: 1 = Monday, 2 = Tuesday, ..., 6 = Saturday, 7 = Sunday
          updates.dia_semana = dayOfWeek === 0 ? 7 : dayOfWeek
        }
      } else {
        updates[name] = name === 'dia_semana' ? parseInt(value, 10) : value
      }
      
      return updates
    })
    
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: '' }))
    setConflictError('')
  }

  const validate = () => {
    const e = {}
    if (!formData.subject_id) e.subject_id = 'Seleccione una materia'
    if (!formData.classroom_id) e.classroom_id = 'Seleccione un aula'
    if (!formData.hora_inicio) e.hora_inicio = 'Hora de inicio requerida'
    if (!formData.hora_fin) e.hora_fin = 'Hora de fin requerida'
    
    // Validate date-specific mode requirements
    if (formData.es_fecha_especifica && !formData.fecha_especifica) {
      e.fecha_especifica = 'Fecha específica requerida'
    }
    
    // Validate that specific date is not in the past
    if (formData.fecha_especifica) {
      const selectedDate = new Date(formData.fecha_especifica)
      const today = new Date()
      today.setHours(0, 0, 0, 0) // Reset time to compare only dates
      if (selectedDate < today) {
        e.fecha_especifica = 'No se pueden crear horarios para fechas pasadas'
      }
    }
    
    // Validate time consistency
    if (formData.hora_inicio && formData.hora_fin) {
      const startTime = formData.hora_inicio.split(':').map(Number)
      const endTime = formData.hora_fin.split(':').map(Number)
      const startMinutes = startTime[0] * 60 + startTime[1]
      const endMinutes = endTime[0] * 60 + endTime[1]
      const duration = endMinutes - startMinutes
      
      // Check time consistency
      if (startMinutes >= endMinutes) {
        e.hora_fin = 'La hora de fin debe ser posterior a la hora de inicio'
      }
      
      // Check minimum duration (at least 1 hour / 60 minutes)
      if (duration < 60) {
        e.hora_fin = 'La clase debe durar al menos 1 hora'
      }
      
      // Check maximum duration (4 hours / 240 minutes)
      if (duration > 240) {
        e.hora_fin = 'La clase no puede durar más de 4 horas'
      }
    }
    
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!validate()) return
    setConflictError('')
    setLoading(true)
    try {
      const submitData = {
        subject_id: parseInt(formData.subject_id, 10),
        classroom_id: parseInt(formData.classroom_id, 10),
        dia_semana: formData.dia_semana,
        hora_inicio: toTimeStr(formData.hora_inicio),
        hora_fin: toTimeStr(formData.hora_fin),
      }

      // Add date-specific field if enabled
      if (formData.es_fecha_especifica && formData.fecha_especifica) {
        submitData.fecha_especifica = formData.fecha_especifica
      }

      await scheduleService.create(submitData)
      onSuccess?.()
      onClose?.()
    } catch (err) {
      console.error('Error creating schedule:', err)
      
      // Extract error message from different error formats
      let errorMessage = 'Error al crear el horario.'
      
      // Handle validation errors (400) - includes duration validation errors
      if (err?.status === 400 || err?.response?.status === 400) {
        const detail = err?.response?.data?.detail || err?.data?.detail || err?.detail
        if (typeof detail === 'string') {
          errorMessage = detail
        } else if (typeof detail === 'object' && detail?.message) {
          errorMessage = detail.message
        } else if (err?.message && !err.message.includes('Error de conexión')) {
          errorMessage = err.message
        }
      }
      // Handle conflict errors (422)
      else if (err?.status === 422 || err?.response?.status === 422) {
        const data = err?.response?.data || err?.data || err
        const d = data?.detail || data
        if (typeof d === 'object' && d.conflicts) {
          const parts = (d.conflicts || []).map((c) =>
            c.type === 'classroom' ? 'Aula ocupada en ese horario' : c.type === 'professor' ? 'El profesor tiene otra clase a esa hora' : `Conflicto: ${c.type}`
          )
          errorMessage = parts.join('. ') || d.message || 'Conflictos de horario.'
        } else if (typeof d === 'string') {
          errorMessage = d
        } else if (d?.message) {
          errorMessage = d.message
        }
      }
      // Handle other errors (but not network errors)
      else if (err?.message && !err.message.includes('Error de conexión') && !err?.isNetworkError) {
        const detail = err?.response?.data?.detail || err?.data?.detail || err?.detail
        if (detail) {
          errorMessage = typeof detail === 'string' ? detail : detail?.message || errorMessage
        } else {
          errorMessage = err.message
        }
      }
      
      setConflictError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Nuevo horario</h3>
          <button onClick={onClose} className="p-1 rounded-lg text-gray-500 hover:bg-gray-100" aria-label="Cerrar">
            <X className="w-5 h-5" />
          </button>
        </div>

        {loadOpts && (
          <div className="mb-4 text-sm text-gray-500">Cargando materias y aulas…</div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {conflictError && (
            <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-amber-800 text-sm">
              {conflictError}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Materia</label>
            <select
              name="subject_id"
              value={formData.subject_id}
              onChange={handleChange}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
              disabled={loadOpts}
            >
              <option value="">Seleccione</option>
              {subjects.map((s) => (
                <option key={s.id} value={s.id}>{s.nombre} ({s.codigo_institucional})</option>
              ))}
            </select>
            {errors.subject_id && <p className="mt-1 text-sm text-red-600">{errors.subject_id}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Aula</label>
            <select
              name="classroom_id"
              value={formData.classroom_id}
              onChange={handleChange}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
              disabled={loadOpts}
            >
              <option value="">Seleccione</option>
              {classrooms.map((c) => (
                <option key={c.id} value={c.id}>{c.nombre} ({c.codigo})</option>
              ))}
            </select>
            {errors.classroom_id && <p className="mt-1 text-sm text-red-600">{errors.classroom_id}</p>}
          </div>

          {/* New: Date-specific mode toggle */}
          <div className="border-t border-gray-200 pt-4">
            <div className="flex items-center space-x-3">
              <input
                type="checkbox"
                id="es_fecha_especifica"
                name="es_fecha_especifica"
                checked={formData.es_fecha_especifica}
                onChange={handleChange}
                className="h-4 w-4 rounded border-gray-300 text-purple-600 focus:ring-purple-500"
              />
              <label htmlFor="es_fecha_especifica" className="text-sm font-medium text-gray-700">
                Programar para fecha específica
              </label>
            </div>
            <p className="mt-1 text-xs text-gray-500">
              {formData.es_fecha_especifica 
                ? 'El horario se creará solo para la fecha seleccionada' 
                : 'El horario se repetirá semanalmente en el día seleccionado'
              }
            </p>
          </div>

          {/* New: Date picker (conditional) */}
          {formData.es_fecha_especifica && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Fecha específica
              </label>
              <input
                type="date"
                name="fecha_especifica"
                value={formData.fecha_especifica}
                onChange={handleChange}
                min={new Date().toISOString().split('T')[0]} // Prevent past dates
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                required={formData.es_fecha_especifica}
              />
              {errors.fecha_especifica && <p className="mt-1 text-sm text-red-600">{errors.fecha_especifica}</p>}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Día de la semana
              {formData.es_fecha_especifica && (
                <span className="text-xs text-gray-500 ml-1">(calculado automáticamente)</span>
              )}
            </label>
            <select
              name="dia_semana"
              value={formData.dia_semana}
              onChange={handleChange}
              disabled={formData.es_fecha_especifica}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 disabled:bg-gray-100 disabled:text-gray-500"
            >
              {DIAS.map((d) => (
                <option key={d.value} value={d.value}>{d.label}</option>
              ))}
            </select>
            {formData.es_fecha_especifica && (
              <p className="mt-1 text-xs text-gray-500">
                Se calcula automáticamente según la fecha seleccionada
              </p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Hora de inicio
              </label>
              <TimeInput
                name="hora_inicio"
                value={formData.hora_inicio}
                onChange={handleChange}
                className="w-full"
              />
              {errors.hora_inicio && <p className="mt-1 text-sm text-red-600">{errors.hora_inicio}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Hora de finalización
              </label>
              <TimeInput
                name="hora_fin"
                value={formData.hora_fin}
                onChange={handleChange}
                className="w-full"
              />
              {errors.hora_fin && <p className="mt-1 text-sm text-red-600">{errors.hora_fin}</p>}
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading || loadOpts}
              className="px-4 py-2 rounded-lg bg-purple-600 text-white hover:bg-purple-700 disabled:opacity-50"
            >
              {loading ? 'Guardando…' : 'Guardar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
