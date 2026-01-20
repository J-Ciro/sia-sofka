import { useState, useEffect } from 'react'
import { X } from 'lucide-react'
import { scheduleService, subjectService, classroomService } from '../../services/apiService'

const DIAS = [
  { value: 1, label: 'Lunes' },
  { value: 2, label: 'Martes' },
  { value: 3, label: 'Miércoles' },
  { value: 4, label: 'Jueves' },
  { value: 5, label: 'Viernes' },
  { value: 6, label: 'Sábado' },
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
  })
  const [subjects, setSubjects] = useState([])
  const [classrooms, setClassrooms] = useState([])
  const [loading, setLoading] = useState(false)
  const [loadOpts, setLoadOpts] = useState(true)
  const [errors, setErrors] = useState({})
  const [conflictError, setConflictError] = useState('')

  useEffect(() => {
    if (!isOpen) return
    setFormData({ subject_id: '', classroom_id: '', dia_semana: 1, hora_inicio: '08:00', hora_fin: '10:00' })
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
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: name === 'dia_semana' ? parseInt(value, 10) : value }))
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: '' }))
    setConflictError('')
  }

  const validate = () => {
    const e = {}
    if (!formData.subject_id) e.subject_id = 'Seleccione una materia'
    if (!formData.classroom_id) e.classroom_id = 'Seleccione un aula'
    if (!formData.hora_inicio) e.hora_inicio = 'Hora de inicio requerida'
    if (!formData.hora_fin) e.hora_fin = 'Hora de fin requerida'
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!validate()) return
    setConflictError('')
    setLoading(true)
    try {
      await scheduleService.create({
        subject_id: parseInt(formData.subject_id, 10),
        classroom_id: parseInt(formData.classroom_id, 10),
        dia_semana: formData.dia_semana,
        hora_inicio: toTimeStr(formData.hora_inicio),
        hora_fin: toTimeStr(formData.hora_fin),
      })
      onSuccess?.()
      onClose?.()
    } catch (err) {
      const data = err?.data || err
      if (err?.status === 422 && data?.detail) {
        const d = data.detail
        if (typeof d === 'object' && d.conflicts) {
          const parts = (d.conflicts || []).map((c) =>
            c.type === 'classroom' ? 'Aula ocupada en ese horario' : c.type === 'professor' ? 'El profesor tiene otra clase a esa hora' : `Conflicto: ${c.type}`
          )
          setConflictError(parts.join('. ') || d.message || 'Conflictos de horario.')
        } else {
          setConflictError(d.message || 'Conflictos de horario.')
        }
      } else {
        setConflictError(err?.message || 'Error al crear el horario.')
      }
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

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Día</label>
            <select
              name="dia_semana"
              value={formData.dia_semana}
              onChange={handleChange}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            >
              {DIAS.map((d) => (
                <option key={d.value} value={d.value}>{d.label}</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Hora inicio</label>
              <input
                type="time"
                name="hora_inicio"
                value={formData.hora_inicio}
                onChange={handleChange}
                min="06:00"
                max="22:00"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
              />
              {errors.hora_inicio && <p className="mt-1 text-sm text-red-600">{errors.hora_inicio}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Hora fin</label>
              <input
                type="time"
                name="hora_fin"
                value={formData.hora_fin}
                onChange={handleChange}
                min="06:00"
                max="22:00"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
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
