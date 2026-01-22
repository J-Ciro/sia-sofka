import { useState, useEffect, useMemo, useCallback, useRef } from 'react'
import { Calendar, dateFnsLocalizer } from 'react-big-calendar'
import withDragAndDrop from 'react-big-calendar/lib/addons/dragAndDrop'
import { format, parse, startOfWeek, getDay, addDays, setHours, setMinutes } from 'date-fns'
import { es } from 'date-fns/locale'
import { scheduleService } from '../../services'
import { X } from 'lucide-react'
import 'react-big-calendar/lib/css/react-big-calendar.css'
import 'react-big-calendar/lib/addons/dragAndDrop/styles.css'

const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek: (d) => startOfWeek(d, { weekStartsOn: 1 }),
  getDay,
  locales: { es },
})

// Create the drag-and-drop enabled calendar
const DragAndDropCalendar = withDragAndDrop(Calendar)

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

function profesorLabel(s) {
  const p = s.subject?.profesor
  if (!p) return ''
  return [p.nombre, p.apellido].filter(Boolean).join(' ').trim() || ''
}

// Enhanced event transformation to handle date-specific schedules
function scheduleToEvent(s, referenceMonday) {
  // Use fecha_especifica if available, otherwise calculate from dia_semana
  let eventDate
  if (s.fecha_especifica) {
    // Parse date string manually to avoid timezone issues
    const [year, month, day] = s.fecha_especifica.split('-').map(Number)
    eventDate = new Date(year, month - 1, day) // month is 0-indexed
  } else {
    eventDate = addDays(referenceMonday, (s.dia_semana || 1) - 1)
  }
  
  const [sh, sm] = String(s.hora_inicio || '08:00').split(':').map(Number)
  const [eh, em] = String(s.hora_fin || '10:00').split(':').map(Number)
  const materia = s.subject?.nombre || `Materia ${s.subject_id}`
  const prof = profesorLabel(s)
  const title = prof ? `${materia} — ${prof}` : materia
  
  return {
    id: s.id,
    title,
    start: setMinutes(setHours(eventDate, sh || 8), sm || 0),
    end: setMinutes(setHours(eventDate, eh || 10), em || 0),
    resource: { 
      schedule: s,
      isDateSpecific: s.fecha_especifica !== null
    },
  }
}

export default function WeeklyCalendar({ refreshKey = 0, currentDate: propCurrentDate, onDateChange }) {
  const [schedules, setSchedules] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedEvent, setSelectedEvent] = useState(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [currentDate, setCurrentDate] = useState(() => propCurrentDate || new Date())
  const [isDragging, setIsDragging] = useState(false)
  const calendarRef = useRef(null)

  // Sync with prop changes
  useEffect(() => {
    if (propCurrentDate) {
      setCurrentDate(propCurrentDate)
    }
  }, [propCurrentDate])

  const referenceMonday = useMemo(
    () => startOfWeek(currentDate, { weekStartsOn: 1 }),
    [currentDate]
  )

  const events = useMemo(
    () => schedules.map((s) => scheduleToEvent(s, referenceMonday)),
    [schedules, referenceMonday]
  )

  const fetchSchedules = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      // Calculate the current week range
      const startOfWeekDate = startOfWeek(currentDate, { weekStartsOn: 1 })
      const endOfWeekDate = addDays(startOfWeekDate, 6)
      
      const startDate = format(startOfWeekDate, 'yyyy-MM-dd')
      const endDate = format(endOfWeekDate, 'yyyy-MM-dd')
      
      // Use the date-range endpoint for better date-specific schedule support
      const data = await scheduleService.getByDateRange(startDate, endDate)
      setSchedules(Array.isArray(data) ? data : [])
    } catch (e) {
      console.error('Error fetching schedules:', e)
      // Fallback to weekly endpoint if date-range fails
      try {
        console.log('Falling back to weekly endpoint...')
        const fallbackData = await scheduleService.getWeekly()
        setSchedules(Array.isArray(fallbackData) ? fallbackData : [])
        setError('') // Clear error if fallback works
      } catch (fallbackError) {
        console.error('Fallback also failed:', fallbackError)
        setError(e?.message || 'Error al cargar horarios')
      }
    } finally {
      setLoading(false)
    }
  }, [currentDate])

  useEffect(() => {
    fetchSchedules()
  }, [fetchSchedules, refreshKey])

  // Enhanced event prop getter to show date-specific vs recurring schedules
  const eventPropGetter = useCallback((event) => {
    const sid = event.resource?.schedule?.subject_id ?? 0
    const isDateSpecific = event.resource?.isDateSpecific
    const color = CALENDAR_COLORS[sid % CALENDAR_COLORS.length]
    
    return {
      style: {
        backgroundColor: color,
        border: isDateSpecific ? '3px solid #1F2937' : '2px solid transparent',
        borderRadius: '4px',
        opacity: isDragging ? 0.7 : 1,
        boxShadow: isDateSpecific ? '0 2px 4px rgba(5, 150, 105, 0.3)' : 'none',
      }
    }
  }, [isDragging])

  // Drag and drop handlers with enhanced validation and optimistic updates
  const handleEventDrop = useCallback(async ({ event, start, end }) => {
    if (!event.resource?.schedule) return

    // Client-side validation before attempting the move
    const newDate = new Date(start)
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    
    // Validate that the new date is not in the past
    if (newDate < today) {
      setError('No se pueden mover horarios a fechas pasadas')
      return
    }
    
    // Validate that it's not Sunday (day 0)
    if (newDate.getDay() === 0) {
      setError('No se permiten horarios los domingos')
      return
    }
    
    // Validate time range (6:00 AM to 10:00 PM)
    const startHour = start.getHours()
    const endHour = end.getHours()
    if (startHour < 6 || endHour > 22) {
      setError('Los horarios deben estar entre las 6:00 AM y 10:00 PM')
      return
    }
    
    // Validate minimum duration (1 hour)
    const durationMs = end.getTime() - start.getTime()
    const durationHours = durationMs / (1000 * 60 * 60)
    if (durationHours < 1) {
      setError('Los horarios deben tener una duración mínima de 1 hora')
      return
    }
    
    // Validate maximum duration (4 hours)
    if (durationHours > 4) {
      setError('Los horarios no pueden durar más de 4 horas')
      return
    }

    setIsDragging(true)
    
    // Prepare update data
    const year = start.getFullYear()
    const month = String(start.getMonth() + 1).padStart(2, '0')
    const day = String(start.getDate()).padStart(2, '0')
    const newDateStr = `${year}-${month}-${day}`
    const newStartTime = format(start, 'HH:mm')
    const newEndTime = format(end, 'HH:mm')
    const newDayOfWeek = start.getDay() === 0 ? 7 : start.getDay()

    // Optimistic update - update the schedule in state immediately
    const originalSchedule = event.resource.schedule
    const updatedSchedule = {
      ...originalSchedule,
      fecha_especifica: newDateStr,
      dia_semana: newDayOfWeek,
      hora_inicio: newStartTime,
      hora_fin: newEndTime,
    }

    // Update schedules state optimistically
    setSchedules(prevSchedules => 
      prevSchedules.map(s => 
        s.id === originalSchedule.id ? updatedSchedule : s
      )
    )

    try {
      // Send update to server
      await scheduleService.update(originalSchedule.id, {
        fecha_especifica: newDateStr,
        dia_semana: newDayOfWeek,
        hora_inicio: newStartTime,
        hora_fin: newEndTime,
      })

      setError('') // Clear any previous errors on success
    } catch (error) {
      // Revert optimistic update on error
      setSchedules(prevSchedules => 
        prevSchedules.map(s => 
          s.id === originalSchedule.id ? originalSchedule : s
        )
      )

      // Handle server-side validation errors
      const errorMessage = error?.response?.data?.detail || error?.message || 'Error al mover el horario'
      if (errorMessage.includes('conflict') || errorMessage.includes('ocupada') || errorMessage.includes('otra clase')) {
        setError('Conflicto de horario: ' + errorMessage)
      } else {
        setError(errorMessage)
      }
    } finally {
      setIsDragging(false)
    }
  }, [])

  const handleEventResize = useCallback(async ({ event, start, end }) => {
    if (!event.resource?.schedule) return

    // Client-side validation for resize
    const startHour = start.getHours()
    const endHour = end.getHours()
    
    // Validate time range (6:00 AM to 10:00 PM)
    if (startHour < 6 || endHour > 22) {
      setError('Los horarios deben estar entre las 6:00 AM y 10:00 PM')
      return
    }
    
    // Validate minimum duration (1 hour)
    const durationMs = end.getTime() - start.getTime()
    const durationHours = durationMs / (1000 * 60 * 60)
    if (durationHours < 1) {
      setError('Los horarios deben tener una duración mínima de 1 hora')
      return
    }
    
    // Validate maximum duration (4 hours)
    if (durationHours > 4) {
      setError('Los horarios no pueden durar más de 4 horas')
      return
    }

    setIsDragging(true)
    
    // Prepare update data
    const originalSchedule = event.resource.schedule
    const newStartTime = format(start, 'HH:mm')
    const newEndTime = format(end, 'HH:mm')

    // Optimistic update - update the schedule in state immediately
    const updatedSchedule = {
      ...originalSchedule,
      hora_inicio: newStartTime,
      hora_fin: newEndTime,
    }

    // Update schedules state optimistically
    setSchedules(prevSchedules => 
      prevSchedules.map(s => 
        s.id === originalSchedule.id ? updatedSchedule : s
      )
    )

    try {
      // Send update to server
      await scheduleService.update(originalSchedule.id, {
        hora_inicio: newStartTime,
        hora_fin: newEndTime,
      })

      setError('') // Clear any previous errors on success
    } catch (error) {
      // Revert optimistic update on error
      setSchedules(prevSchedules => 
        prevSchedules.map(s => 
          s.id === originalSchedule.id ? originalSchedule : s
        )
      )

      // Handle server-side validation errors
      const errorMessage = error?.response?.data?.detail || error?.message || 'Error al redimensionar el horario'
      if (errorMessage.includes('conflict') || errorMessage.includes('ocupada') || errorMessage.includes('otra clase')) {
        setError('Conflicto de horario: ' + errorMessage)
      } else {
        setError(errorMessage)
      }
    } finally {
      setIsDragging(false)
    }
  }, [])

  const handleSelectEvent = useCallback((event) => {
    setSelectedEvent(event)
    setModalOpen(true)
  }, [])

  const handleNavigate = useCallback((date) => {
    setCurrentDate(date)
    if (onDateChange) {
      onDateChange(date)
    }
  }, [onDateChange])

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
      
      {/* Visual Legend */}
      <div className="mb-4 flex items-center gap-6 text-sm text-gray-600">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-purple-500 rounded border-2 border-transparent"></div>
          <span>Horario recurrente</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-purple-500 rounded border-2 border-green-600 shadow-sm"></div>
          <span>Fecha específica</span>
        </div>
        {isDragging && (
          <div className="flex items-center gap-2 text-blue-600">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
            <span>Moviendo horario...</span>
          </div>
        )}
      </div>
      
      <div ref={calendarRef}>
        <DragAndDropCalendar
          localizer={localizer}
          events={events}
          date={currentDate}
          onNavigate={handleNavigate}
          defaultView="week"
          views={['week', 'day']}
          onSelectEvent={handleSelectEvent}
          eventPropGetter={eventPropGetter}
          onEventDrop={handleEventDrop}
          onEventResize={handleEventResize}
          resizable={true}
          draggableAccessor={() => true}
          messages={MESSAGES}
          min={minTime}
          max={maxTime}
          step={30}
          className="rounded-xl border border-purple-200 bg-white shadow-sm"
        />
      </div>

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
                  Fecha específica: {format(new Date(s.fecha_especifica), 'dd/MM/yyyy', { locale: es })}
                </span>
              </dd>
            </div>
          )}
          {!s.fecha_especifica && (
            <div>
              <dt className="text-gray-500">Tipo</dt>
              <dd className="font-medium">
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  Recurrente semanal
                </span>
              </dd>
            </div>
          )}
        </dl>
      </div>
    </div>
  )
}
