import { useState, useEffect, useMemo, useCallback } from 'react'
import { Calendar, dateFnsLocalizer } from 'react-big-calendar'
import { format, parse, startOfWeek, getDay, startOfMonth, endOfMonth, setHours, setMinutes } from 'date-fns'
import { es } from 'date-fns/locale'
import { scheduleService } from '../../services'
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
  next: 'Siguiente',
  previous: 'Anterior',
  today: 'Hoy',
  month: 'Mes',
  week: 'Semana',
  day: 'Día',
  agenda: 'Agenda',
  date: 'Fecha',
  time: 'Hora',
  event: 'Evento',
  noEventsInRange: 'No hay horarios en este mes.',
}

export default function MonthlyCalendar({ refreshKey = 0, currentDate, onDateChange }) {
  const [schedules, setSchedules] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedEvent, setSelectedEvent] = useState(null)
  const [modalOpen, setModalOpen] = useState(false)

  const monthStart = useMemo(() => startOfMonth(currentDate), [currentDate])
  const monthEnd = useMemo(() => endOfMonth(currentDate), [currentDate])

  const fetchSchedules = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      // Use new API endpoint that supports date ranges
      const data = await scheduleService.getByDateRange(
        format(monthStart, 'yyyy-MM-dd'),
        format(monthEnd, 'yyyy-MM-dd')
      )
      setSchedules(Array.isArray(data) ? data : [])
    } catch (e) {
      setError(e?.message || 'Error al cargar horarios del mes')
    } finally {
      setLoading(false)
    }
  }, [monthStart, monthEnd])

  useEffect(() => {
    fetchSchedules()
  }, [fetchSchedules, refreshKey])

  const events = useMemo(() => {
    return schedules.map((s) => {
      let eventDate
      if (s.fecha_especifica) {
        // Parse date string manually to avoid timezone issues
        const [year, month, day] = s.fecha_especifica.split('-').map(Number)
        eventDate = new Date(year, month - 1, day) // month is 0-indexed
      } else {
        eventDate = new Date() // This shouldn't happen in month view with date range API
      }
      
      const [sh, sm] = String(s.hora_inicio || '08:00').split(':').map(Number)
      const [eh, em] = String(s.hora_fin || '10:00').split(':').map(Number)

      return {
        id: s.id,
        title: `${s.subject?.nombre || 'Sin materia'}`,
        start: setMinutes(setHours(eventDate, sh || 8), sm || 0),
        end: setMinutes(setHours(eventDate, eh || 10), em || 0),
        resource: { 
          schedule: s,
          isDateSpecific: s.fecha_especifica !== null
        },
      }
    })
  }, [schedules])

  const eventPropGetter = useCallback((event) => {
    const sid = event.resource?.schedule?.subject_id ?? 0
    const isDateSpecific = event.resource?.isDateSpecific
    const color = CALENDAR_COLORS[sid % CALENDAR_COLORS.length]
    
    return {
      style: {
        backgroundColor: color,
        border: isDateSpecific ? '2px solid #1F2937' : '1px solid transparent',
        fontSize: '12px',
        padding: '2px 4px',
      }
    }
  }, [])

  const handleEventClick = useCallback((event) => {
    setSelectedEvent(event)
    setModalOpen(true)
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
        {error}
      </div>
    )
  }

  return (
    <div className="h-[calc(100vh-12rem)]">
      <Calendar
        localizer={localizer}
        events={events}
        startAccessor="start"
        endAccessor="end"
        date={currentDate}
        onNavigate={onDateChange}
        defaultView="month"
        views={['month']}
        eventPropGetter={eventPropGetter}
        onSelectEvent={handleEventClick}
        messages={MESSAGES}
        className="rounded-xl border border-purple-200 bg-white shadow-sm"
      />

      {/* Reuse existing modal from WeeklyCalendar */}
      {modalOpen && selectedEvent && (
        <ScheduleDetailModal
          event={selectedEvent}
          onClose={() => { setModalOpen(false); setSelectedEvent(null) }}
        />
      )}
    </div>
  )
}

// Reuse the modal component from WeeklyCalendar
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
            <dt className="text-gray-500">Aula ocupada</dt>
            <dd className="font-medium">{s.classroom?.nombre || s.classroom?.codigo || `Aula ${s.classroom_id}`}</dd>
          </div>
          <div>
            <dt className="text-gray-500">Horario (aula ocupada)</dt>
            <dd className="font-medium">{hi} – {hf}</dd>
          </div>
          <div>
            <dt className="text-gray-500">Profesor</dt>
            <dd className="font-medium">
              {s.subject?.profesor
                ? [s.subject.profesor.nombre, s.subject.profesor.apellido].filter(Boolean).join(' ')
                : '–'}
            </dd>
          </div>
          <div>
            <dt className="text-gray-500">Duración</dt>
            <dd className="font-medium">{duration}</dd>
          </div>
          {s.fecha_especifica && (
            <div>
              <dt className="text-gray-500">Tipo</dt>
              <dd className="font-medium">
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  Fecha específica
                </span>
              </dd>
            </div>
          )}
        </dl>
      </div>
    </div>
  )
}