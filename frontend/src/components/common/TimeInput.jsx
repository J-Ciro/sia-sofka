import { useState, useEffect } from 'react'

/**
 * Custom Time Input Component with AM/PM display and no time limits
 * Uses native HTML time input with scroll functionality like in Attendance page
 */
const TimeInput = ({ 
  value = '', 
  onChange, 
  name, 
  className = '', 
  disabled = false,
  ...props 
}) => {
  const [displayTime, setDisplayTime] = useState('')

  // Convert 24-hour format to 12-hour format with AM/PM for display
  const formatTimeDisplay = (time24) => {
    if (!time24) return ''
    const [hours, minutes] = time24.split(':').map(Number)
    const period = hours >= 12 ? 'PM' : 'AM'
    const displayHours = hours === 0 ? 12 : hours > 12 ? hours - 12 : hours
    return `${displayHours}:${minutes.toString().padStart(2, '0')} ${period}`
  }

  // Update display time when value changes
  useEffect(() => {
    if (value) {
      setDisplayTime(formatTimeDisplay(value))
    } else {
      setDisplayTime('')
    }
  }, [value])

  const handleTimeChange = (e) => {
    const newTime = e.target.value
    onChange?.({ target: { name, value: newTime } })
  }

  return (
    <div className="relative">
      {/* Native Time Input - same style as Attendance page */}
      <input
        type="time"
        name={name}
        value={value}
        onChange={handleTimeChange}
        disabled={disabled}
        className={`w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent disabled:bg-gray-100 disabled:text-gray-500 ${className}`}
        {...props}
      />
      
      {/* Display AM/PM format below */}
      {displayTime && (
        <div className="mt-1 text-xs text-gray-600 font-medium">
          {displayTime}
        </div>
      )}
    </div>
  )
}

export default TimeInput