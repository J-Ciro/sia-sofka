import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Calendar, Clock, Users, TrendingUp, Edit, Eye, BookOpen } from 'lucide-react'
import { attendanceService } from '../../services/apiService'
import { formatDate, formatTime, getAttendancePercentageColor } from '../../utils/formatters'

const SessionHistory = () => {
  const navigate = useNavigate()
  const [sessions, setSessions] = useState([])
  const [subjects, setSubjects] = useState([])
  const [selectedSubject, setSelectedSubject] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchSubjects()
  }, [])

  useEffect(() => {
    if (selectedSubject) {
      fetchSessions()
    }
  }, [selectedSubject])

  const fetchSubjects = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/subjects', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      const data = await response.json()
      setSubjects(data)
      
      if (data.length > 0) {
        setSelectedSubject(data[0].id.toString())
      }
    } catch (err) {
      setError('Error al cargar materias')
      console.error(err)
    }
  }

  const fetchSessions = async () => {
    setLoading(true)
    setError('')
    
    try {
      const data = await attendanceService.getSessionsBySubject(parseInt(selectedSubject))
      setSessions(data)
    } catch (err) {
      setError('Error al cargar sesiones')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleViewSession = async (sessionId) => {
    // Redirigir a TakeAttendance con la sesión cargada
    navigate(`/attendance?sessionId=${sessionId}`)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-purple-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-purple-100 rounded-lg">
                <Calendar className="w-8 h-8 text-purple-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">Historial de Sesiones</h1>
                <p className="text-gray-600">Revisa las sesiones de clase creadas</p>
              </div>
            </div>
            <button
              onClick={() => navigate('/attendance')}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              Nueva Sesión
            </button>
          </div>

          {/* Subject Filter */}
          <div className="flex items-center gap-4">
            <BookOpen className="w-5 h-5 text-gray-600" />
            <select
              value={selectedSubject}
              onChange={(e) => setSelectedSubject(e.target.value)}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="">Seleccionar materia...</option>
              {subjects.map((subject) => (
                <option key={subject.id} value={subject.id}>
                  {subject.nombre}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
            <p className="text-gray-600 mt-4">Cargando sesiones...</p>
          </div>
        )}

        {/* Sessions List */}
        {!loading && !error && sessions.length === 0 && (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-700 mb-2">No hay sesiones</h3>
            <p className="text-gray-600 mb-6">No se han creado sesiones para esta materia</p>
            <button
              onClick={() => navigate('/attendance')}
              className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              Crear Primera Sesión
            </button>
          </div>
        )}

        {!loading && !error && sessions.length > 0 && (
          <div className="space-y-4">
            {sessions.map((session) => (
              <SessionCard
                key={session.id}
                session={session}
                onView={handleViewSession}
                getAttendanceColor={getAttendancePercentageColor}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

// Componente para cada tarjeta de sesión
const SessionCard = ({ session, onView, getAttendanceColor }) => {
  const [stats, setStats] = useState(null)
  const [loadingStats, setLoadingStats] = useState(true)

  useEffect(() => {
    fetchStats()
  }, [session.id])

  const fetchStats = async () => {
    try {
      const data = await attendanceService.getSessionStats(session.id)
      setStats(data)
    } catch (err) {
      console.error('Error fetching stats:', err)
    } finally {
      setLoadingStats(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between">
        {/* Left Side - Info */}
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-3">
            <div className="flex items-center gap-2 text-gray-700">
              <Calendar className="w-5 h-5 text-purple-600" />
              <span className="font-semibold">{formatDate(session.fecha)}</span>
            </div>
            <div className="flex items-center gap-2 text-gray-600">
              <Clock className="w-4 h-4" />
              <span className="text-sm">
                {formatTime(session.hora_inicio)} - {formatTime(session.hora_fin)}
              </span>
            </div>
          </div>

          {session.descripcion && (
            <p className="text-gray-600 mb-4">{session.descripcion}</p>
          )}

          {/* Statistics */}
          {loadingStats ? (
            <div className="flex items-center gap-2 text-gray-500">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600"></div>
              <span className="text-sm">Cargando estadísticas...</span>
            </div>
          ) : stats ? (
            <div className="grid grid-cols-4 gap-4">
              <StatBadge
                label="Total"
                value={stats.total}
                icon={Users}
                color="bg-blue-100 text-blue-700"
              />
              <StatBadge
                label="Presentes"
                value={stats.presentes}
                icon={TrendingUp}
                color="bg-green-100 text-green-700"
              />
              <StatBadge
                label="Ausentes"
                value={stats.ausentes}
                icon={Users}
                color="bg-red-100 text-red-700"
              />
              <StatBadge
                label="Tardanzas"
                value={stats.tardanzas}
                icon={Clock}
                color="bg-yellow-100 text-yellow-700"
              />
            </div>
          ) : null}
        </div>

        {/* Right Side - Actions & Percentage */}
        <div className="flex flex-col items-end gap-4 ml-6">
          {stats && (
            <div className={`px-4 py-2 rounded-lg font-semibold ${getAttendanceColor(stats.porcentaje_asistencia)}`}>
              {stats.porcentaje_asistencia.toFixed(1)}%
            </div>
          )}

          <button
            onClick={() => onView(session.id)}
            className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            <Edit className="w-4 h-4" />
            Ver/Editar
          </button>
        </div>
      </div>
    </div>
  )
}

// Componente para badges de estadísticas
const StatBadge = ({ label, value, icon: Icon, color }) => (
  <div className={`flex flex-col items-center p-3 rounded-lg ${color}`}>
    <Icon className="w-5 h-5 mb-1" />
    <span className="text-2xl font-bold">{value}</span>
    <span className="text-xs">{label}</span>
  </div>
)

export default SessionHistory
