import { useState, useEffect, useMemo } from 'react'
import { Calendar, dateFnsLocalizer } from 'react-big-calendar'
import { format, parse, startOfWeek, getDay, addDays, setHours, setMinutes } from 'date-fns'
import { es } from 'date-fns/locale'
import { scheduleService } from '../../services/apiService'
import { X } from 'lucide-react'
import 'react-big-calendar/lib/css/react-big-calendar.css'

const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek: (d) => startOfWeek(d, { weekStartsOn: 1 }),
  getDay,
  locales: { es },
})

const CALENDAR_COLORS = [
  '#4F46E5', '#059669', '#DC2626', '#D97706', '#7C3AED', '#0891B2',
  '#BE185D', '#0D9488', '#CA8A04', '#2563EB',
]

const MESSAGES = {
  next: 'Sig',
  previous: 'Ant',
  today: 'Hoy',
  month: 'Mes',
  week: 'Semana',
  day: 'Día',
  agenda: 'Agenda',
  date: 'Fecha',
  time: 'Hora',
  event: 'Evento',
  noEventsInRange: 'No hay horarios en este rango.',
}

function scheduleToEvent(s, referenceMonday) {
  const d = addDays(referenceMonday, (s.dia_semana || 1) - 1)
  const [sh, sm] = String(s.hora_inicio || '08:00').split(':').map(Number)
  const [eh, em] = String(s.hora_fin || '10:00').split(':').map(Number)
  return {
    title: s.subject?.nombre || `Materia ${s.subject_id}`,
    start: setMinutes(setHours(d, sh || 8), sm || 0),
    end: setMinutes(setHours(d, eh || 10), em || 0),
    resource: { schedule: s },
  }
}

export default function WeeklyCalendar({ refreshKey = 0 }) {
  const [schedules, setSchedules] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedEvent, setSelectedEvent] = useState(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [currentDate, setCurrentDate] = useState(() => new Date())

  const referenceMonday = useMemo(
    () => startOfWeek(currentDate, { weekStartsOn: 1 }),
    [currentDate]
  )

  const events = useMemo(
    () => schedules.map((s) => scheduleToEvent(s, referenceMonday)),
    [schedules, referenceMonday]
  )

  useEffect(() => {
    let cancelled = false
    async function load() {
      setLoading(true)
      setError('')
      try {
        const data = await scheduleService.getWeekly()
        if (!cancelled) setSchedules(Array.isArray(data) ? data : [])
      } catch (e) {
        if (!cancelled) setError(e?.message || 'Error al cargar horarios')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => { cancelled = true }
  }, [refreshKey])

  const eventPropGetter = (event) => {
    const sid = event.resource?.schedule?.subject_id ?? 0
    const color = CALENDAR_COLORS[sid % CALENDAR_COLORS.length]
    return { style: { backgroundColor: color } }
  }

  const handleSelectEvent = (event) => {
    setSelectedEvent(event)
    setModalOpen(true)
  }

  const minTime = useMemo(() => new Date(2000, 0, 1, 6, 0, 0), [])
  const maxTime = useMemo(() => new Date(2000, 0, 1, 22, 0, 0), [])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600" />
      </div>
    )
  }

  return (
    <div className="h-[calc(100vh-12rem)]">
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}
      <Calendar
        localizer={localizer}
        events={events}
        date={currentDate}
        onNavigate={(d) => setCurrentDate(d)}
        defaultView="week"
        views={['week', 'day']}
        onSelectEvent={handleSelectEvent}
        eventPropGetter={eventPropGetter}
        messages={MESSAGES}
        min={minTime}
        max={maxTime}
        step={30}
        className="rounded-xl border border-purple-200 bg-white shadow-sm"
      />

      {modalOpen && selectedEvent && (
        <ScheduleDetailModal
          event={selectedEvent}
          onClose={() => { setModalOpen(false); setSelectedEvent(null) }}
        />
      )}
    </div>
  )
}

function ScheduleDetailModal({ event, onClose }) {
  const s = event?.resource?.schedule
  if (!s) return null

  const hi = String(s.hora_inicio || '').slice(0, 5)
  const hf = String(s.hora_fin || '').slice(0, 5)
  const duration = (s.hora_inicio && s.hora_fin)
    ? (() => {
        const [ah, am] = String(s.hora_inicio).split(':').map(Number)
        const [bh, bm] = String(s.hora_fin).split(':').map(Number)
        const m = (bh * 60 + bm) - (ah * 60 + am)
        return m >= 60 ? `${Math.floor(m / 60)} h ${m % 60 ? m % 60 + ' min' : ''}`.trim() : `${m} min`
      })()
    : '–'

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Detalle del horario</h3>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-gray-500 hover:bg-gray-100"
            aria-label="Cerrar"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <dl className="space-y-3 text-sm">
          <div>
            <dt className="text-gray-500">Código</dt>
            <dd className="font-medium">{s.codigo || '–'}</dd>
          </div>
          <div>
            <dt className="text-gray-500">Materia</dt>
            <dd className="font-medium">{s.subject?.nombre || `Materia ${s.subject_id}`}</dd>
          </div>
          <div>
            <dt className="text-gray-500">Aula</dt>
            <dd className="font-medium">{s.classroom?.nombre || s.classroom?.codigo || `Aula ${s.classroom_id}`}</dd>
          </div>
          <div>
            <dt className="text-gray-500">Hora</dt>
            <dd className="font-medium">{hi} – {hf}</dd>
          </div>
          <div>
            <dt className="text-gray-500">Duración</dt>
            <dd className="font-medium">{duration}</dd>
          </div>
        </dl>
      </div>
    </div>
  )
}
