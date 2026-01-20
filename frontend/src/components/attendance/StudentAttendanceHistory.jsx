import { useState, useEffect } from 'react'
import { useAuth } from '../../context/AuthContext'
import { attendanceService, estudianteService } from '../../services/apiService'
import { 
  CheckCircle, 
  XCircle, 
  Clock,
  TrendingDown,
  AlertTriangle,
  Calendar,
  BookOpen,
  BarChart3
} from 'lucide-react'
import Loading from '../common/Loading'
import { AttendanceStatus, getAttendanceColorClasses } from '../../utils/attendanceHelpers'
import { formatDate, formatTime, getAlertLevel } from '../../utils/formatters'

const StudentAttendanceHistory = () => {
  const { user } = useAuth()
  const [subjects, setSubjects] = useState([])
  const [selectedSubject, setSelectedSubject] = useState(null)
  const [attendanceHistory, setAttendanceHistory] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (user?.id) {
      fetchSubjects()
    }
  }, [user?.id])

  useEffect(() => {
    if (selectedSubject?.id && user?.id) {
      fetchAttendanceHistory(selectedSubject.id)
    }
  }, [selectedSubject?.id, user?.id])

  const fetchSubjects = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await estudianteService.getEnrolledSubjects()
      setSubjects(data || [])
      if (data && data.length > 0) {
        setSelectedSubject(data[0])
      }
    } catch (err) {
      console.error('Error fetching subjects:', err)
      setError('Error al cargar materias matriculadas')
      setSubjects([])
    } finally {
      setLoading(false)
    }
  }

  const fetchAttendanceHistory = async (subjectId) => {
    try {
      setLoading(true)
      setError('')
      const data = await attendanceService.getStudentHistory(subjectId)
      const history = Array.isArray(data) ? data : []
      setAttendanceHistory(history)
      calculateStats(history)
    } catch (err) {
      console.error('Error fetching attendance history:', err)
      setError(err?.message || 'Error al cargar historial de asistencia')
      setAttendanceHistory([])
      calculateStats([])
    } finally {
      setLoading(false)
    }
  }

  const calculateStats = (history) => {
    const total = history.length
    const presente = history.filter(h => h.estado === AttendanceStatus.PRESENTE).length
    const ausente = history.filter(h => h.estado === AttendanceStatus.AUSENTE).length
    const tardanza = history.filter(h => h.estado === AttendanceStatus.TARDANZA).length
    
    // Fórmula: (Presente + Tardanza) / Total * 100
    const porcentaje = total > 0 ? ((presente + tardanza) / total * 100).toFixed(1) : 0
    const alertLevel = getAlertLevel(parseFloat(porcentaje))
    
    setStats({
      total,
      presente,
      ausente,
      tardanza,
      porcentaje: parseFloat(porcentaje),
      alertLevel
    })
  }

  const getAttendanceIcon = (estado) => {
    switch (estado) {
      case AttendanceStatus.PRESENTE:
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case AttendanceStatus.AUSENTE:
        return <XCircle className="w-5 h-5 text-red-600" />
      case AttendanceStatus.TARDANZA:
        return <Clock className="w-5 h-5 text-yellow-600" />
      default:
        return null
    }
  }

  const getAlertConfig = () => {
    if (!stats) return null
    
    switch (stats.alertLevel) {
      case 'critical':
        return {
          bg: 'bg-red-50',
          border: 'border-red-500',
          text: 'text-red-700',
          icon: <AlertTriangle className="w-6 h-6 text-red-600" />,
          message: '¡Alerta Crítica! Tu asistencia está por debajo del 70%. Contacta a tu profesor.',
          barColor: 'bg-red-600'
        }
      case 'warning':
        return {
          bg: 'bg-yellow-50',
          border: 'border-yellow-500',
          text: 'text-yellow-700',
          icon: <TrendingDown className="w-6 h-6 text-yellow-600" />,
          message: 'Advertencia: Tu asistencia está por debajo del 80%. Intenta mejorar tu asistencia.',
          barColor: 'bg-yellow-600'
        }
      default:
        return {
          bg: 'bg-green-50',
          border: 'border-green-500',
          text: 'text-green-700',
          icon: <CheckCircle className="w-6 h-6 text-green-600" />,
          message: '¡Excelente! Tu asistencia está en buen nivel.',
          barColor: 'bg-green-600'
        }
    }
  }

  if (loading) {
    return <Loading />
  }

  const alertConfig = getAlertConfig()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-purple-800 bg-clip-text text-transparent mb-1">
          Historial de Asistencia
        </h1>
        <p className="text-gray-600 text-sm">Consulta tu registro de asistencia por materia</p>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 text-red-700 px-4 py-3 rounded-lg shadow-md flex items-center space-x-2">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <p className="font-medium">{error}</p>
        </div>
      )}

      {/* Subject Selection */}
      <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Selecciona una Materia
        </label>
        <select
          value={selectedSubject?.id || ''}
          onChange={(e) => {
            const subject = subjects.find(s => s.id === parseInt(e.target.value))
            setSelectedSubject(subject)
          }}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
        >
          {subjects.map(subject => (
            <option key={subject.id} value={subject.id}>
              {subject.codigo_institucional} - {subject.nombre}
            </option>
          ))}
        </select>
      </div>

      {selectedSubject && stats && (
        <>
          {/* Alert Banner */}
          {alertConfig && (
            <div className={`${alertConfig.bg} border-l-4 ${alertConfig.border} ${alertConfig.text} px-6 py-4 rounded-lg shadow-md flex items-center space-x-3`}>
              {alertConfig.icon}
              <p className="font-medium">{alertConfig.message}</p>
            </div>
          )}

          {/* Statistics Overview */}
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <div className="flex items-center space-x-2 mb-4">
              <BarChart3 className="w-6 h-6 text-purple-600" />
              <h2 className="text-xl font-bold text-gray-800">Estadísticas de Asistencia</h2>
            </div>

            {/* Percentage Bar */}
            <div className="mb-6">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">Porcentaje de Asistencia</span>
                <span className="text-2xl font-bold text-purple-600">{stats.porcentaje}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
                <div 
                  className={`h-4 ${alertConfig.barColor} transition-all duration-500 rounded-full`}
                  style={{ width: `${stats.porcentaje}%` }}
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Incluye Presentes y Tardanzas
              </p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-purple-50 rounded-xl p-4 border border-purple-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-purple-700 font-medium">Total Clases</p>
                    <p className="text-2xl font-bold text-purple-800">{stats.total}</p>
                  </div>
                  <Calendar className="w-8 h-8 text-purple-600" />
                </div>
              </div>

              <div className="bg-green-50 rounded-xl p-4 border border-green-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-green-700 font-medium">Presentes</p>
                    <p className="text-2xl font-bold text-green-800">{stats.presente}</p>
                  </div>
                  <CheckCircle className="w-8 h-8 text-green-600" />
                </div>
              </div>

              <div className="bg-yellow-50 rounded-xl p-4 border border-yellow-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-yellow-700 font-medium">Tardanzas</p>
                    <p className="text-2xl font-bold text-yellow-800">{stats.tardanza}</p>
                  </div>
                  <Clock className="w-8 h-8 text-yellow-600" />
                </div>
              </div>

              <div className="bg-red-50 rounded-xl p-4 border border-red-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-red-700 font-medium">Ausentes</p>
                    <p className="text-2xl font-bold text-red-800">{stats.ausente}</p>
                  </div>
                  <XCircle className="w-8 h-8 text-red-600" />
                </div>
              </div>
            </div>
          </div>

          {/* History List */}
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <div className="flex items-center space-x-2 mb-4">
              <BookOpen className="w-6 h-6 text-purple-600" />
              <h2 className="text-xl font-bold text-gray-800">Historial Detallado</h2>
            </div>

            {attendanceHistory.length === 0 ? (
              <div className="text-center py-8">
                <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No hay registros de asistencia disponibles</p>
              </div>
            ) : (
              <div className="space-y-3">
                {attendanceHistory.map(record => (
                  <div 
                    key={record.id}
                    className={`p-4 rounded-lg border-2 ${getAttendanceColorClasses(record.estado)} transition-all`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3 flex-1">
                        {getAttendanceIcon(record.estado)}
                        <div>
                          <p className="font-semibold text-gray-800">
                            {formatDate(record.fecha)}
                          </p>
                          <p className="text-sm opacity-75">
                            {record.hora_inicio} - {record.hora_fin}
                          </p>
                          {record.descripcion && (
                            <p className="text-sm mt-1">{record.descripcion}</p>
                          )}
                        </div>
                      </div>
                      <span className="px-3 py-1 rounded-full text-xs font-bold">
                        {record.estado}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}

      {/* Empty State */}
      {subjects.length === 0 && (
        <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 text-center">
          <BookOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-700 mb-2">No tienes materias matriculadas</h3>
          <p className="text-gray-500">Debes estar matriculado en una materia para ver tu asistencia.</p>
        </div>
      )}
    </div>
  )
}

export default StudentAttendanceHistory
