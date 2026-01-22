# Design Document: Schedule System Enhancement

## Overview

This design extends the existing SIA SOFKA schedule system to fix the recurring schedule issue and add advanced calendar functionality. The current system already provides a solid foundation with Schedule and Classroom models, conflict validation, and a weekly calendar view using react-big-calendar. This enhancement adds date-specific scheduling capabilities, month view, and drag-and-drop functionality while maintaining full backward compatibility.

The core issue being addressed is that the current system uses only the `dia_semana` field (day of week) which causes schedules created for specific dates to appear on every occurrence of that weekday. The solution adds an optional `fecha_especifica` field that takes precedence when present.

## Architecture

The enhancement follows the existing clean architecture pattern:

```
Backend Enhancement:
├── models/schedule.py          # Add fecha_especifica field
├── schemas/schedule.py         # Add date fields to schemas  
├── services/schedule_service.py # Extend conflict validation
├── repositories/schedule_repository.py # Add date-specific queries
└── api/v1/endpoints/schedules.py # Extend existing endpoints

Frontend Enhancement:
├── components/schedule/
│   ├── WeeklyCalendar.jsx     # Add month view toggle
│   ├── MonthlyCalendar.jsx    # New month view component
│   ├── ScheduleForm.jsx       # Add date picker
│   └── CalendarContainer.jsx  # New container for view management
└── services/apiService.js     # Extend existing API calls
```

The design leverages existing infrastructure:
- Current SQLAlchemy models and Alembic migrations
- Existing FastAPI endpoints and dependency injection
- Current react-big-calendar integration
- Existing conflict validation logic in ScheduleService

## Components and Interfaces

### Backend Components

#### Enhanced Schedule Model
Extends the existing `Schedule` model in `backend/app/models/schedule.py`:

```python
class Schedule(Base):
    # ... existing fields ...
    dia_semana = Column(Integer, nullable=False, index=True)  # Existing
    hora_inicio = Column(Time, nullable=False)               # Existing
    hora_fin = Column(Time, nullable=False)                  # Existing
    
    # New field for specific date scheduling
    fecha_especifica = Column(Date, nullable=True, index=True)
    
    # Enhanced table args with new index
    __table_args__ = (
        # Existing constraints
        UniqueConstraint("subject_id", "dia_semana", "hora_inicio", 
                        name="uq_schedule_subject_dia_hora"),
        # New constraint for date-specific schedules
        UniqueConstraint("subject_id", "fecha_especifica", "hora_inicio",
                        name="uq_schedule_subject_fecha_hora"),
        # Existing indexes
        Index("ix_schedule_classroom_dia_hora", "classroom_id", "dia_semana", "hora_inicio"),
        # New index for date-specific queries
        Index("ix_schedule_classroom_fecha_hora", "classroom_id", "fecha_especifica", "hora_inicio"),
    )
```

#### Enhanced Schedule Schemas
Extends existing schemas in `backend/app/schemas/schedule.py`:

```python
class ScheduleBase(BaseModel):
    # ... existing fields ...
    subject_id: int = Field(..., gt=0)
    classroom_id: int = Field(..., gt=0)
    dia_semana: int = Field(..., ge=1, le=6, description="1=Lunes..6=Sábado")
    hora_inicio: time
    hora_fin: time
    
    # New optional field for specific dates
    fecha_especifica: Optional[date] = Field(None, description="Fecha específica (opcional)")
    
    @field_validator("fecha_especifica")
    @classmethod
    def validate_fecha_especifica(cls, v: Optional[date], info):
        if v is not None and "dia_semana" in info.data:
            # Validate that day of week matches if both are provided
            expected_dia = v.weekday() + 1  # Convert to 1-6 format
            if expected_dia == 7:  # Sunday becomes 7, but we use 1-6
                expected_dia = 7  # Keep as 7 or adjust based on system needs
            if info.data["dia_semana"] != expected_dia and expected_dia <= 6:
                raise ValueError("dia_semana must match the day of week of fecha_especifica")
        return v

class ScheduleResponse(BaseModel):
    # ... existing fields ...
    fecha_especifica: Optional[date] = None
    # Add computed field for display
    es_fecha_especifica: bool = Field(default=False, description="True if this is a date-specific schedule")
    
    @computed_field
    @property
    def es_fecha_especifica(self) -> bool:
        return self.fecha_especifica is not None
```

#### Enhanced Schedule Repository
Extends existing repository in `backend/app/repositories/schedule_repository.py`:

```python
class ScheduleRepository:
    # ... existing methods ...
    
    async def find_classroom_overlaps_by_date(
        self,
        classroom_id: int,
        fecha: date,
        hora_inicio: time,
        hora_fin: time,
        exclude_schedule_id: Optional[int] = None,
    ) -> List[Schedule]:
        """Find classroom conflicts for a specific date."""
        query = select(Schedule).where(
            Schedule.classroom_id == classroom_id,
            Schedule.fecha_especifica == fecha,
            Schedule.hora_inicio < hora_fin,
            Schedule.hora_fin > hora_inicio,
        )
        if exclude_schedule_id:
            query = query.where(Schedule.id != exclude_schedule_id)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def find_professor_overlaps_by_date(
        self,
        profesor_id: int,
        fecha: date,
        hora_inicio: time,
        hora_fin: time,
        exclude_schedule_id: Optional[int] = None,
    ) -> List[Schedule]:
        """Find professor conflicts for a specific date."""
        query = select(Schedule).join(Subject).where(
            Subject.profesor_id == profesor_id,
            Schedule.fecha_especifica == fecha,
            Schedule.hora_inicio < hora_fin,
            Schedule.hora_fin > hora_inicio,
        )
        if exclude_schedule_id:
            query = query.where(Schedule.id != exclude_schedule_id)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_schedules_by_date_range(
        self,
        start_date: date,
        end_date: date,
        user_id: Optional[int] = None,
        role: Optional[UserRole] = None,
    ) -> List[Schedule]:
        """Get schedules for a date range, including both weekly and date-specific."""
        # Base query for date-specific schedules
        date_query = select(Schedule).where(
            Schedule.fecha_especifica.between(start_date, end_date)
        )
        
        # Base query for weekly recurring schedules
        weekly_query = select(Schedule).where(
            Schedule.fecha_especifica.is_(None)
        )
        
        # Apply user/role filters if provided
        if user_id and role:
            if role == UserRole.PROFESOR:
                date_query = date_query.join(Subject).where(Subject.profesor_id == user_id)
                weekly_query = weekly_query.join(Subject).where(Subject.profesor_id == user_id)
            elif role == UserRole.ESTUDIANTE:
                date_query = date_query.join(Subject).join(Enrollment).where(
                    Enrollment.student_id == user_id
                )
                weekly_query = weekly_query.join(Subject).join(Enrollment).where(
                    Enrollment.student_id == user_id
                )
        
        # Execute both queries
        date_result = await self.db.execute(date_query)
        weekly_result = await self.db.execute(weekly_query)
        
        return list(date_result.scalars().all()) + list(weekly_result.scalars().all())
```

#### Enhanced Schedule Service
Extends existing service in `backend/app/services/schedule_service.py`:

```python
class ScheduleService:
    # ... existing methods ...
    
    async def validate_schedule_conflicts(
        self,
        subject_id: int,
        classroom_id: int,
        dia_semana: int,
        hora_inicio: time,
        hora_fin: time,
        fecha_especifica: Optional[date] = None,
        exclude_schedule_id: Optional[int] = None,
    ) -> List[dict]:
        """Enhanced conflict validation supporting both weekly and date-specific schedules."""
        result = await self.db.execute(select(Subject).where(Subject.id == subject_id))
        subject = result.scalar_one_or_none()
        if not subject:
            raise ValueError("Subject not found")
        profesor_id = subject.profesor_id

        conflicts: List[dict] = []

        if fecha_especifica:
            # Check conflicts for specific date
            classroom_conflicts = await self.repo.find_classroom_overlaps_by_date(
                classroom_id, fecha_especifica, hora_inicio, hora_fin, exclude_schedule_id
            )
            if classroom_conflicts:
                conflicts.append({"type": "classroom", "schedules": classroom_conflicts})

            professor_conflicts = await self.repo.find_professor_overlaps_by_date(
                profesor_id, fecha_especifica, hora_inicio, hora_fin, exclude_schedule_id
            )
            if professor_conflicts:
                conflicts.append({"type": "professor", "schedules": professor_conflicts})
            
            # Also check against weekly recurring schedules for the same day
            weekly_classroom_conflicts = await self.repo.find_classroom_overlaps(
                classroom_id, dia_semana, hora_inicio, hora_fin, exclude_schedule_id
            )
            weekly_professor_conflicts = await self.repo.find_professor_overlaps(
                profesor_id, dia_semana, hora_inicio, hora_fin, exclude_schedule_id
            )
            
            # Filter weekly conflicts to only those without fecha_especifica
            weekly_classroom_conflicts = [s for s in weekly_classroom_conflicts if s.fecha_especifica is None]
            weekly_professor_conflicts = [s for s in weekly_professor_conflicts if s.fecha_especifica is None]
            
            if weekly_classroom_conflicts:
                conflicts.append({"type": "classroom_weekly", "schedules": weekly_classroom_conflicts})
            if weekly_professor_conflicts:
                conflicts.append({"type": "professor_weekly", "schedules": weekly_professor_conflicts})
        else:
            # Use existing weekly conflict validation
            co = await self.repo.find_classroom_overlaps(
                classroom_id, dia_semana, hora_inicio, hora_fin, exclude_schedule_id
            )
            if co:
                conflicts.append({"type": "classroom", "schedules": co})

            po = await self.repo.find_professor_overlaps(
                profesor_id, dia_semana, hora_inicio, hora_fin, exclude_schedule_id
            )
            if po:
                conflicts.append({"type": "professor", "schedules": po})

        return conflicts
    
    async def get_schedules_for_calendar(
        self,
        start_date: date,
        end_date: date,
        user_id: Optional[int] = None,
        role: Optional[UserRole] = None,
    ) -> List[Schedule]:
        """Get schedules for calendar display, expanding weekly schedules to specific dates."""
        schedules = await self.repo.get_schedules_by_date_range(
            start_date, end_date, user_id, role
        )
        
        # Expand weekly schedules to specific dates within the range
        expanded_schedules = []
        current_date = start_date
        
        while current_date <= end_date:
            day_of_week = current_date.weekday() + 1  # Convert to 1-6 format
            if day_of_week == 7:  # Handle Sunday if needed
                day_of_week = 7
            
            # Add date-specific schedules for this date
            for schedule in schedules:
                if schedule.fecha_especifica == current_date:
                    expanded_schedules.append(schedule)
                elif schedule.fecha_especifica is None and schedule.dia_semana == day_of_week:
                    # Create a virtual schedule instance for this specific date
                    virtual_schedule = Schedule(
                        id=schedule.id,
                        codigo=schedule.codigo,
                        subject_id=schedule.subject_id,
                        classroom_id=schedule.classroom_id,
                        dia_semana=schedule.dia_semana,
                        hora_inicio=schedule.hora_inicio,
                        hora_fin=schedule.hora_fin,
                        fecha_especifica=current_date,  # Virtual date for display
                        subject=schedule.subject,
                        classroom=schedule.classroom,
                    )
                    expanded_schedules.append(virtual_schedule)
            
            current_date += timedelta(days=1)
        
        return expanded_schedules
```

### Frontend Components

#### Enhanced Calendar Container
New component `frontend/src/components/schedule/CalendarContainer.jsx`:

```javascript
import { useState, useCallback } from 'react'
import WeeklyCalendar from './WeeklyCalendar'
import MonthlyCalendar from './MonthlyCalendar'

const CalendarContainer = ({ refreshKey = 0 }) => {
  const [currentView, setCurrentView] = useState('week') // 'week' or 'month'
  const [currentDate, setCurrentDate] = useState(new Date())

  const handleViewChange = useCallback((view) => {
    setCurrentView(view)
    // Persist preference in session storage
    sessionStorage.setItem('calendar-view-preference', view)
  }, [])

  const handleDateChange = useCallback((date) => {
    setCurrentDate(date)
  }, [])

  return (
    <div className="space-y-4">
      {/* View Toggle Controls */}
      <div className="flex items-center justify-between">
        <div className="flex bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => handleViewChange('week')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              currentView === 'week'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Vista Semanal
          </button>
          <button
            onClick={() => handleViewChange('month')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              currentView === 'month'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Vista Mensual
          </button>
        </div>
      </div>

      {/* Calendar Views */}
      {currentView === 'week' ? (
        <WeeklyCalendar
          refreshKey={refreshKey}
          currentDate={currentDate}
          onDateChange={handleDateChange}
        />
      ) : (
        <MonthlyCalendar
          refreshKey={refreshKey}
          currentDate={currentDate}
          onDateChange={handleDateChange}
        />
      )}
    </div>
  )
}

export default CalendarContainer
```

#### Enhanced Weekly Calendar
Extends existing `frontend/src/components/schedule/WeeklyCalendar.jsx`:

```javascript
// Add drag and drop support
import { DragDropContext } from 'react-beautiful-dnd'

export default function WeeklyCalendar({ refreshKey = 0, currentDate, onDateChange }) {
  // ... existing state ...
  const [isDragging, setIsDragging] = useState(false)

  // Enhanced event transformation to handle date-specific schedules
  const scheduleToEvent = useCallback((s, referenceDate) => {
    const eventDate = s.fecha_especifica 
      ? new Date(s.fecha_especifica)
      : addDays(referenceDate, (s.dia_semana || 1) - 1)
    
    const [sh, sm] = String(s.hora_inicio || '08:00').split(':').map(Number)
    const [eh, em] = String(s.hora_fin || '10:00').split(':').map(Number)

    return {
      id: s.id,
      title: `${s.subject?.nombre || 'Sin materia'} - ${s.classroom?.nombre || 'Sin aula'}`,
      start: setMinutes(setHours(eventDate, sh || 8), sm || 0),
      end: setMinutes(setHours(eventDate, eh || 10), em || 0),
      resource: { 
        schedule: s,
        isDateSpecific: s.fecha_especifica !== null
      },
    }
  }, [])

  // Add drag and drop handlers
  const handleEventDrop = useCallback(async ({ event, start, end }) => {
    if (!event.resource?.schedule) return

    setIsDragging(true)
    try {
      const schedule = event.resource.schedule
      const newDate = format(start, 'yyyy-MM-dd')
      const newStartTime = format(start, 'HH:mm')
      const newEndTime = format(end, 'HH:mm')
      const newDayOfWeek = start.getDay() === 0 ? 7 : start.getDay() // Convert Sunday

      await scheduleService.update(schedule.id, {
        fecha_especifica: newDate,
        dia_semana: newDayOfWeek,
        hora_inicio: newStartTime,
        hora_fin: newEndTime,
      })

      // Refresh calendar
      fetchSchedules()
    } catch (error) {
      setError(error?.message || 'Error al mover el horario')
    } finally {
      setIsDragging(false)
    }
  }, [fetchSchedules])

  // Enhanced event prop getter to show date-specific vs recurring
  const eventPropGetter = useCallback((event) => {
    const sid = event.resource?.schedule?.subject_id ?? 0
    const isDateSpecific = event.resource?.isDateSpecific
    const color = CALENDAR_COLORS[sid % CALENDAR_COLORS.length]
    
    return {
      style: {
        backgroundColor: color,
        border: isDateSpecific ? '2px solid #059669' : '1px solid transparent',
        opacity: isDragging ? 0.7 : 1,
      }
    }
  }, [isDragging])

  return (
    <div className="bg-white rounded-lg shadow p-4">
      {/* ... existing loading/error states ... */}
      
      <Calendar
        localizer={localizer}
        events={events}
        startAccessor="start"
        endAccessor="end"
        style={{ height: 600 }}
        view="week"
        views={['week']}
        date={currentDate}
        onNavigate={onDateChange}
        eventPropGetter={eventPropGetter}
        onSelectEvent={handleEventClick}
        onEventDrop={handleEventDrop}
        resizable={false}
        draggableAccessor={() => true}
        messages={messages}
      />
      
      {/* ... existing modal ... */}
    </div>
  )
}
```

#### New Monthly Calendar Component
New component `frontend/src/components/schedule/MonthlyCalendar.jsx`:

```javascript
import { useState, useEffect, useMemo, useCallback } from 'react'
import { Calendar, momentLocalizer } from 'react-big-calendar'
import moment from 'moment'
import 'moment/locale/es'
import { scheduleService } from '../../services/apiService'
import { format, startOfMonth, endOfMonth } from 'date-fns'
import { es } from 'date-fns/locale'

moment.locale('es')
const localizer = momentLocalizer(moment)

const CALENDAR_COLORS = [
  '#3B82F6', '#EF4444', '#10B981', '#F59E0B', 
  '#8B5CF6', '#06B6D4', '#84CC16', '#F97316'
]

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
      const eventDate = s.fecha_especifica 
        ? new Date(s.fecha_especifica)
        : new Date() // This shouldn't happen in month view with date range API
      
      const [sh, sm] = String(s.hora_inicio || '08:00').split(':').map(Number)
      const [eh, em] = String(s.hora_fin || '10:00').split(':').map(Number)

      return {
        id: s.id,
        title: `${s.subject?.nombre || 'Sin materia'}`,
        start: new Date(eventDate.getFullYear(), eventDate.getMonth(), eventDate.getDate(), sh, sm),
        end: new Date(eventDate.getFullYear(), eventDate.getMonth(), eventDate.getDate(), eh, em),
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
        border: isDateSpecific ? '2px solid #059669' : '1px solid transparent',
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
    return <div className="flex justify-center p-8">Cargando calendario mensual...</div>
  }

  if (error) {
    return <div className="text-red-600 p-4 bg-red-50 rounded-lg">{error}</div>
  }

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <Calendar
        localizer={localizer}
        events={events}
        startAccessor="start"
        endAccessor="end"
        style={{ height: 600 }}
        view="month"
        views={['month']}
        date={currentDate}
        onNavigate={onDateChange}
        eventPropGetter={eventPropGetter}
        onSelectEvent={handleEventClick}
        messages={{
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
        }}
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
```

#### Enhanced Schedule Form
Extends existing `frontend/src/components/schedule/ScheduleForm.jsx`:

```javascript
export default function ScheduleForm({ isOpen, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    subject_id: '',
    classroom_id: '',
    dia_semana: 1,
    hora_inicio: '',
    hora_fin: '',
    fecha_especifica: '', // New field
    es_fecha_especifica: false, // Toggle for date-specific mode
  })

  // ... existing state ...

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setConflictError('')
    
    try {
      const submitData = {
        subject_id: parseInt(formData.subject_id, 10),
        classroom_id: parseInt(formData.classroom_id, 10),
        dia_semana: parseInt(formData.dia_semana, 10),
        hora_inicio: formData.hora_inicio,
        hora_fin: formData.hora_fin,
      }

      // Add date-specific field if enabled
      if (formData.es_fecha_especifica && formData.fecha_especifica) {
        submitData.fecha_especifica = formData.fecha_especifica
        // Auto-calculate dia_semana from date
        const selectedDate = new Date(formData.fecha_especifica)
        submitData.dia_semana = selectedDate.getDay() === 0 ? 7 : selectedDate.getDay()
      }

      await scheduleService.create(submitData)
      onSuccess()
      onClose()
    } catch (err) {
      // ... existing error handling ...
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={`fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 ${isOpen ? '' : 'hidden'}`}>
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Nuevo horario</h3>
          <button onClick={onClose} className="p-1 rounded-lg text-gray-500 hover:bg-gray-100">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* ... existing fields ... */}

          {/* New: Date-specific toggle */}
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="es_fecha_especifica"
              checked={formData.es_fecha_especifica}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                es_fecha_especifica: e.target.checked,
                fecha_especifica: e.target.checked ? prev.fecha_especifica : ''
              }))}
              className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
            />
            <label htmlFor="es_fecha_especifica" className="text-sm font-medium text-gray-700">
              Programar para fecha específica
            </label>
          </div>

          {/* New: Date picker (conditional) */}
          {formData.es_fecha_especifica && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Fecha específica
              </label>
              <input
                type="date"
                value={formData.fecha_especifica}
                onChange={(e) => {
                  const newDate = e.target.value
                  setFormData(prev => {
                    const updates = { ...prev, fecha_especifica: newDate }
                    
                    // Auto-update dia_semana based on selected date
                    if (newDate) {
                      const selectedDate = new Date(newDate)
                      updates.dia_semana = selectedDate.getDay() === 0 ? 7 : selectedDate.getDay()
                    }
                    
                    return updates
                  })
                }}
                min={new Date().toISOString().split('T')[0]} // Prevent past dates
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                required={formData.es_fecha_especifica}
              />
            </div>
          )}

          {/* Modified: Day of week (auto-filled when date is selected) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Día de la semana
              {formData.es_fecha_especifica && (
                <span className="text-xs text-gray-500 ml-1">(calculado automáticamente)</span>
              )}
            </label>
            <select
              value={formData.dia_semana}
              onChange={(e) => setFormData(prev => ({ ...prev, dia_semana: parseInt(e.target.value) }))}
              disabled={formData.es_fecha_especifica}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent disabled:bg-gray-100"
              required
            >
              {DIAS.map(dia => (
                <option key={dia.value} value={dia.value}>{dia.label}</option>
              ))}
            </select>
          </div>

          {/* ... existing time fields and submit button ... */}
        </form>
      </div>
    </div>
  )
}
```

## Data Models

### Enhanced Schedule Model Schema

```sql
-- Migration to add fecha_especifica field
ALTER TABLE schedules 
ADD COLUMN fecha_especifica DATE NULL;

-- Add index for date-specific queries
CREATE INDEX ix_schedule_fecha_especifica ON schedules(fecha_especifica);
CREATE INDEX ix_schedule_classroom_fecha_hora ON schedules(classroom_id, fecha_especifica, hora_inicio);

-- Add constraint for date-specific schedules
ALTER TABLE schedules 
ADD CONSTRAINT uq_schedule_subject_fecha_hora 
UNIQUE (subject_id, fecha_especifica, hora_inicio);

-- Add check constraint to ensure data consistency
ALTER TABLE schedules 
ADD CONSTRAINT chk_schedule_date_consistency 
CHECK (
  fecha_especifica IS NULL OR 
  EXTRACT(DOW FROM fecha_especifica) + 1 = dia_semana OR
  (EXTRACT(DOW FROM fecha_especifica) = 0 AND dia_semana = 7)
);
```

### API Response Format

Enhanced schedule responses include date information:

```json
{
  "id": 123,
  "codigo": "HOR-ABC123",
  "subject_id": 45,
  "classroom_id": 12,
  "dia_semana": 1,
  "hora_inicio": "08:00",
  "hora_fin": "10:00",
  "fecha_especifica": "2024-01-15",
  "es_fecha_especifica": true,
  "subject": {
    "id": 45,
    "nombre": "Matemáticas Avanzadas",
    "codigo_institucional": "MAT-301"
  },
  "classroom": {
    "id": 12,
    "codigo": "AULA-A1B2",
    "nombre": "Aula 301",
    "capacidad": 30
  }
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

Before writing the correctness properties, I need to analyze the acceptance criteria to determine which ones are testable as properties.

### Property 1: Date-Specific Schedule Creation and Display
*For any* specific date and schedule data, when a schedule is created with that date, the schedule should only appear on that exact date and not on other weeks with the same day-of-week.
**Validates: Requirements 1.1, 1.2, 1.3**

### Property 2: Date and Day-of-Week Consistency
*For any* schedule with both a specific date and day-of-week field, the day-of-week should match the actual day of the specific date, and the specific date should take priority for all operations.
**Validates: Requirements 1.4, 2.3, 2.4**

### Property 3: Backward Compatibility Preservation
*For any* existing weekly schedule without a specific date, all current functionality (creation, display, conflict validation, updates) should work exactly as before the enhancement.
**Validates: Requirements 2.1, 2.2, 2.5**

### Property 4: Enhanced Conflict Detection for Date-Specific Schedules
*For any* two schedules on the same specific date, if they have overlapping times and share either the same classroom or professor, a conflict should be detected and the creation/update should be prevented.
**Validates: Requirements 1.5, 6.1, 6.2, 6.3**

### Property 5: Calendar View State Preservation
*For any* date context and view switching operation, the current date context should be preserved when switching between weekly and monthly views, showing the appropriate week or month containing the selected date.
**Validates: Requirements 4.2, 4.4, 4.5**

### Property 6: Month View Display Accuracy
*For any* set of schedules and month period, the month view should display all schedules that fall within that month period with abbreviated information, and clicking any event should show the same details as weekly view.
**Validates: Requirements 3.2, 3.3, 3.4, 3.5**

### Property 7: Drag-and-Drop Schedule Updates
*For any* valid drag-and-drop operation, the schedule should be updated with the new date and time using existing APIs and conflict validation, and the calendar should refresh to show the change.
**Validates: Requirements 5.2, 5.4, 5.5**

### Property 8: Drag-and-Drop Validation
*For any* invalid drag-and-drop operation (conflicting time/classroom/professor), the operation should be prevented and existing conflict validation should be used to determine validity.
**Validates: Requirements 5.3, 6.5**

### Property 9: API Extension Compatibility
*For any* schedule operation (create, read, update), the enhanced APIs should support both existing weekly functionality and new date-specific functionality while maintaining existing response formats with additional date fields.
**Validates: Requirements 7.1, 7.2, 7.3, 7.5**

### Property 10: Form Enhancement Functionality
*For any* schedule creation or editing operation, the enhanced form should support both date-specific and weekly recurring modes with proper validation, and users should be able to switch between modes during editing.
**Validates: Requirements 8.1, 8.3, 8.5**

### Property 11: Visual Schedule Distinction
*For any* schedule displayed in the calendar, date-specific schedules should have distinct visual indicators compared to weekly recurring schedules, allowing users to easily distinguish between the two types.
**Validates: Requirements 8.2, 8.4**

## Error Handling

The enhanced system maintains existing error handling patterns while adding new error cases:

### Date-Specific Schedule Errors
- **Invalid Date Format**: Return 400 with clear message about expected date format
- **Past Date Selection**: Return 400 when attempting to create schedules for past dates
- **Date-Day Mismatch**: Return 400 when provided date doesn't match the specified day-of-week
- **Date-Specific Conflicts**: Use existing conflict error format but include date information

### Drag-and-Drop Errors
- **Invalid Drop Target**: Client-side validation prevents invalid drops
- **Conflict During Move**: Use existing conflict validation and return structured error
- **Network Errors**: Graceful fallback with error message and calendar refresh

### Calendar View Errors
- **Month Loading Failure**: Display error message and fallback to weekly view
- **Date Range Too Large**: Limit month queries to reasonable ranges
- **View State Corruption**: Reset to default weekly view with current date

### Backward Compatibility Errors
- **Migration Failures**: Comprehensive rollback procedures for database changes
- **API Breaking Changes**: Maintain existing endpoint behavior for legacy clients
- **Data Inconsistency**: Validation and repair procedures for inconsistent date/day-of-week data

## Testing Strategy

The testing strategy follows the existing dual approach while adding property-based testing for the new functionality:

### Unit Testing
- **Model Validation**: Test new date field validation and constraints
- **Service Logic**: Test enhanced conflict detection with date-specific scenarios
- **Repository Queries**: Test new date-range and date-specific query methods
- **Form Validation**: Test date picker integration and validation logic
- **Calendar Logic**: Test event transformation for both weekly and date-specific schedules

### Property-Based Testing
Each correctness property will be implemented as a property-based test with minimum 100 iterations:

- **Property 1 Test**: Generate random dates and schedule data, verify date-specific behavior
  - **Tag**: Feature: schedule-enhancement, Property 1: Date-Specific Schedule Creation and Display
- **Property 2 Test**: Generate schedules with date/day combinations, verify consistency
  - **Tag**: Feature: schedule-enhancement, Property 2: Date and Day-of-Week Consistency
- **Property 3 Test**: Generate traditional weekly schedules, verify unchanged behavior
  - **Tag**: Feature: schedule-enhancement, Property 3: Backward Compatibility Preservation
- **Property 4 Test**: Generate conflicting date-specific schedules, verify conflict detection
  - **Tag**: Feature: schedule-enhancement, Property 4: Enhanced Conflict Detection for Date-Specific Schedules
- **Property 5 Test**: Generate view switching scenarios, verify date context preservation
  - **Tag**: Feature: schedule-enhancement, Property 5: Calendar View State Preservation
- **Property 6 Test**: Generate month periods and schedules, verify month view accuracy
  - **Tag**: Feature: schedule-enhancement, Property 6: Month View Display Accuracy
- **Property 7 Test**: Generate valid drag-and-drop operations, verify updates
  - **Tag**: Feature: schedule-enhancement, Property 7: Drag-and-Drop Schedule Updates
- **Property 8 Test**: Generate invalid drag-and-drop operations, verify prevention
  - **Tag**: Feature: schedule-enhancement, Property 8: Drag-and-Drop Validation
- **Property 9 Test**: Generate API operations, verify compatibility and response formats
  - **Tag**: Feature: schedule-enhancement, Property 9: API Extension Compatibility
- **Property 10 Test**: Generate form operations, verify enhanced functionality
  - **Tag**: Feature: schedule-enhancement, Property 10: Form Enhancement Functionality
- **Property 11 Test**: Generate different schedule types, verify visual distinction
  - **Tag**: Feature: schedule-enhancement, Property 11: Visual Schedule Distinction

### Integration Testing
- **API Endpoints**: Test enhanced endpoints with both weekly and date-specific data
- **Database Operations**: Test migration and new queries with existing data
- **Calendar Integration**: Test react-big-calendar with enhanced event data
- **Conflict Resolution**: Test end-to-end conflict detection and resolution

### End-to-End Testing
- **Date-Specific Schedule Creation**: Create schedule for specific date, verify it appears only on that date
- **Month View Navigation**: Navigate through months, verify correct schedules are displayed
- **Drag-and-Drop Operations**: Perform drag-and-drop in both views, verify updates
- **View Switching**: Switch between weekly and monthly views, verify state preservation
- **Backward Compatibility**: Verify existing weekly schedules continue to work unchanged

### Performance Testing
- **Month View Loading**: Ensure month view loads efficiently with large datasets
- **Date Range Queries**: Test performance of new date-range query methods
- **Calendar Rendering**: Verify calendar performance with mixed weekly/date-specific schedules
- **Drag-and-Drop Responsiveness**: Ensure drag operations remain responsive

The testing approach ensures that all new functionality works correctly while maintaining the reliability of existing features. Property-based tests provide comprehensive coverage of the enhanced logic, while integration and E2E tests verify the complete user experience.