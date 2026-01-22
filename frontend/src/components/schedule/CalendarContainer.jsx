import { useState, useCallback, useEffect } from 'react'
import WeeklyCalendar from './WeeklyCalendar'
import MonthlyCalendar from './MonthlyCalendar'

const CalendarContainer = ({ refreshKey = 0 }) => {
  const [currentView, setCurrentView] = useState(() => {
    // Get saved preference from session storage
    return sessionStorage.getItem('calendar-view-preference') || 'week'
  })
  const [currentDate, setCurrentDate] = useState(new Date())

  const handleViewChange = useCallback((view) => {
    setCurrentView(view)
    // Persist preference in session storage
    sessionStorage.setItem('calendar-view-preference', view)
  }, [])

  const handleDateChange = useCallback((date) => {
    setCurrentDate(date)
  }, [])

  // Initialize view preference on mount
  useEffect(() => {
    const savedView = sessionStorage.getItem('calendar-view-preference')
    if (savedView && (savedView === 'week' || savedView === 'month')) {
      setCurrentView(savedView)
    }
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