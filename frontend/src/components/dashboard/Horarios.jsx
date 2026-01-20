import { useState } from 'react'
import { useAuth } from '../../context/AuthContext'
import { Plus } from 'lucide-react'
import WeeklyCalendar from '../schedule/WeeklyCalendar'
import ScheduleForm from '../schedule/ScheduleForm'

export default function Horarios() {
  const { user } = useAuth()
  const [formOpen, setFormOpen] = useState(false)
  const [refreshKey, setRefreshKey] = useState(0)

  const isAdmin = user?.role === 'Admin'

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-2xl font-bold text-gray-900">Horarios</h1>
        {isAdmin && (
          <button
            onClick={() => setFormOpen(true)}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-purple-600 text-white hover:bg-purple-700 shadow-sm"
          >
            <Plus className="w-5 h-5" />
            Nuevo horario
          </button>
        )}
      </div>

      <WeeklyCalendar refreshKey={refreshKey} />

      <ScheduleForm
        isOpen={formOpen}
        onClose={() => setFormOpen(false)}
        onSuccess={() => setRefreshKey((k) => k + 1)}
      />
    </div>
  )
}
