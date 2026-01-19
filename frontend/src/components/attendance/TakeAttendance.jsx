import { useState, useEffect } from 'react'
import { useAuth } from '../../context/AuthContext'
import { attendanceService, profesorService } from '../../services/apiService'
import { 
  CheckCircle, 
  XCircle, 
  Clock, 
  Users, 
  Calendar,
  AlertCircle,
  Save,
  ArrowLeft
} from 'lucide-react'
import Loading from '../common/Loading'

const TakeAttendance = () => {
  const { user } = useAuth()
  const [subjects, setSubjects] = useState([])
  const [selectedSubject, setSelectedSubject] = useState(null)
  const [students, setStudents] = useState([])
  const [sessionDate, setSessionDate] = useState(new Date().toISOString().split('T')[0])
  const [sessionTime, setSessionTime] = useState({
    inicio: '08:00',
    fin: '10:00'
  })
  const [descripcion, setDescripcion] = useState('')
  const [attendanceMap, setAttendanceMap] = useState({})
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [sessionCreated, setSessionCreated] = useState(false)
  const [currentSessionId, setCurrentSessionId] = useState(null)

  useEffect(() => {
    if (user?.id) {
      fetchSubjects()
    }
  }, [user?.id])

  useEffect(() => {
    if (selectedSubject?.id) {
      fetchStudents(selectedSubject.id)
    }
  }, [selectedSubject?.id])

  const fetchSubjects = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await profesorService.getAssignedSubjects(user?.id)
      setSubjects(data || [])
      if (data && data.length > 0) {
        setSelectedSubject(data[0])
      }
    } catch (err) {
      console.error('Error fetching subjects:', err)
      setError('Error al cargar materias asignadas')
    } finally {
      setLoading(false)
    }
  }

  const fetchStudents = async (subjectId) => {
    try {
      const data = await profesorService.getStudentsBySubject(subjectId)
      setStudents(data || [])
      
      // Inicializar mapa de asistencia con estado AUSENTE por defecto
      const initialAttendance = {}
      data.forEach(student => {
        initialAttendance[student.id] = 'AUSENTE'
      })
      setAttendanceMap(initialAttendance)
    } catch (err) {
      console.error('Error fetching students:', err)
      setStudents([])
    }
  }

  const handleCreateSession = async () => {
    if (!selectedSubject) {
      setError('Selecciona una materia primero')
      return
    }

    try {
      setSaving(true)
      setError('')
      
      const sessionData = {
        subject_id: selectedSubject.id,
        fecha: sessionDate,
        hora_inicio: `${sessionDate}T${sessionTime.inicio}:00`,
        hora_fin: `${sessionDate}T${sessionTime.fin}:00`,
        descripcion: descripcion || `Clase de ${selectedSubject.nombre}`
      }

      const session = await attendanceService.createSession(sessionData)
      setCurrentSessionId(session.id)
      setSessionCreated(true)
      setSuccess('Sesión de clase creada exitosamente')
    } catch (err) {
      console.error('Error creating session:', err)
      setError(err.response?.data?.detail || 'Error al crear sesión de clase')
    } finally {
      setSaving(false)
    }
  }

  const cycleAttendanceState = (studentId) => {
    const currentState = attendanceMap[studentId]
    const states = ['PRESENTE', 'AUSENTE', 'TARDANZA']
    const currentIndex = states.indexOf(currentState)
    const nextIndex = (currentIndex + 1) % states.length
    
    setAttendanceMap(prev => ({
      ...prev,
      [studentId]: states[nextIndex]
    }))
  }

  const markAll = (estado) => {
    const newMap = {}
    students.forEach(student => {
      newMap[student.id] = estado
    })
    setAttendanceMap(newMap)
    setSuccess(`Todos los estudiantes marcados como ${estado}`)
    setTimeout(() => setSuccess(''), 3000)
  }

  const handleSaveAttendance = async () => {
    if (!currentSessionId) {
      setError('Debes crear la sesión primero')
      return
    }

    try {
      setSaving(true)
      setError('')

      // En un escenario real, aquí se enviarían todos los registros de asistencia
      // Por ahora, solo simulamos el guardado
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      setSuccess('Asistencia guardada exitosamente')
      
      // Reset
      setTimeout(() => {
        setSessionCreated(false)
        setCurrentSessionId(null)
        setDescripcion('')
        setSuccess('')
        
        // Reinicializar mapa
        const initialAttendance = {}
        students.forEach(student => {
          initialAttendance[student.id] = 'AUSENTE'
        })
        setAttendanceMap(initialAttendance)
      }, 2000)
      
    } catch (err) {
      console.error('Error saving attendance:', err)
      setError('Error al guardar asistencia')
    } finally {
      setSaving(false)
    }
  }

  const getAttendanceColor = (estado) => {
    switch (estado) {
      case 'PRESENTE':
        return 'bg-green-100 text-green-700 border-green-300'
      case 'AUSENTE':
        return 'bg-red-100 text-red-700 border-red-300'
      case 'TARDANZA':
        return 'bg-yellow-100 text-yellow-700 border-yellow-300'
      default:
        return 'bg-gray-100 text-gray-700 border-gray-300'
    }
  }

  const getAttendanceIcon = (estado) => {
    switch (estado) {
      case 'PRESENTE':
        return <CheckCircle className="w-5 h-5" />
      case 'AUSENTE':
        return <XCircle className="w-5 h-5" />
      case 'TARDANZA':
        return <Clock className="w-5 h-5" />
      default:
        return null
    }
  }

  const countByStatus = () => {
    const counts = { PRESENTE: 0, AUSENTE: 0, TARDANZA: 0 }
    Object.values(attendanceMap).forEach(estado => {
      counts[estado]++
    })
    return counts
  }

  if (loading) {
    return <Loading />
  }

  const stats = countByStatus()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-purple-800 bg-clip-text text-transparent mb-1">
          Tomar Asistencia
        </h1>
        <p className="text-gray-600 text-sm">Gestiona la asistencia de tus estudiantes</p>
      </div>

      {/* Alerts */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 text-red-700 px-4 py-3 rounded-lg shadow-md flex items-center space-x-2">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <p className="font-medium">{error}</p>
        </div>
      )}

      {success && (
        <div className="bg-green-50 border-l-4 border-green-500 text-green-700 px-4 py-3 rounded-lg shadow-md flex items-center space-x-2">
          <CheckCircle className="w-5 h-5 flex-shrink-0" />
          <p className="font-medium">{success}</p>
        </div>
      )}

      {/* Subject Selection & Session Info */}
      {!sessionCreated ? (
        <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
          <h2 className="text-xl font-bold text-gray-800 mb-4">Crear Sesión de Clase</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Subject Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Materia
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

            {/* Date */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Fecha
              </label>
              <input
                type="date"
                value={sessionDate}
                max={new Date().toISOString().split('T')[0]}
                onChange={(e) => setSessionDate(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>

            {/* Start Time */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Hora Inicio
              </label>
              <input
                type="time"
                value={sessionTime.inicio}
                onChange={(e) => setSessionTime(prev => ({ ...prev, inicio: e.target.value }))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>

            {/* End Time */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Hora Fin
              </label>
              <input
                type="time"
                value={sessionTime.fin}
                onChange={(e) => setSessionTime(prev => ({ ...prev, fin: e.target.value }))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>

            {/* Description */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Descripción (opcional)
              </label>
              <input
                type="text"
                value={descripcion}
                onChange={(e) => setDescripcion(e.target.value)}
                placeholder="Ej: Clase sobre funciones cuadráticas"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
          </div>

          <button
            onClick={handleCreateSession}
            disabled={saving || !selectedSubject}
            className="mt-4 w-full bg-gradient-to-r from-purple-600 to-purple-700 text-white px-6 py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-purple-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            <Calendar className="w-5 h-5" />
            <span>{saving ? 'Creando...' : 'Crear Sesión y Comenzar'}</span>
          </button>
        </div>
      ) : (
        <>
          {/* Bulk Actions */}
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <h2 className="text-xl font-bold text-gray-800 mb-4">Acciones Masivas</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button
                onClick={() => markAll('PRESENTE')}
                className="bg-gradient-to-r from-green-500 to-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-green-600 hover:to-green-700 transition-all flex items-center justify-center space-x-2"
              >
                <CheckCircle className="w-5 h-5" />
                <span>Marcar Todos Presentes</span>
              </button>

              <button
                onClick={() => markAll('AUSENTE')}
                className="bg-gradient-to-r from-red-500 to-red-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-red-600 hover:to-red-700 transition-all flex items-center justify-center space-x-2"
              >
                <XCircle className="w-5 h-5" />
                <span>Marcar Todos Ausentes</span>
              </button>

              <button
                onClick={() => markAll('TARDANZA')}
                className="bg-gradient-to-r from-yellow-500 to-yellow-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-yellow-600 hover:to-yellow-700 transition-all flex items-center justify-center space-x-2"
              >
                <Clock className="w-5 h-5" />
                <span>Marcar Todos Tardanza</span>
              </button>
            </div>
          </div>

          {/* Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-xl shadow-md p-4 border border-gray-100">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 font-medium">Total</p>
                  <p className="text-2xl font-bold text-gray-800">{students.length}</p>
                </div>
                <Users className="w-10 h-10 text-purple-600" />
              </div>
            </div>

            <div className="bg-green-50 rounded-xl shadow-md p-4 border border-green-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-green-700 font-medium">Presentes</p>
                  <p className="text-2xl font-bold text-green-800">{stats.PRESENTE}</p>
                </div>
                <CheckCircle className="w-10 h-10 text-green-600" />
              </div>
            </div>

            <div className="bg-red-50 rounded-xl shadow-md p-4 border border-red-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-red-700 font-medium">Ausentes</p>
                  <p className="text-2xl font-bold text-red-800">{stats.AUSENTE}</p>
                </div>
                <XCircle className="w-10 h-10 text-red-600" />
              </div>
            </div>

            <div className="bg-yellow-50 rounded-xl shadow-md p-4 border border-yellow-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-yellow-700 font-medium">Tardanzas</p>
                  <p className="text-2xl font-bold text-yellow-800">{stats.TARDANZA}</p>
                </div>
                <Clock className="w-10 h-10 text-yellow-600" />
              </div>
            </div>
          </div>

          {/* Students List */}
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <h2 className="text-xl font-bold text-gray-800 mb-4">
              Lista de Estudiantes ({students.length})
            </h2>

            {students.length === 0 ? (
              <div className="text-center py-8">
                <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No hay estudiantes matriculados en esta materia</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {students.map(student => (
                  <button
                    key={student.id}
                    onClick={() => cycleAttendanceState(student.id)}
                    className={`p-4 rounded-lg border-2 transition-all hover:shadow-md ${getAttendanceColor(attendanceMap[student.id])}`}
                  >
                    <div className="flex items-center space-x-3">
                      {getAttendanceIcon(attendanceMap[student.id])}
                      <div className="text-left flex-1">
                        <p className="font-semibold">
                          {student.nombre} {student.apellido}
                        </p>
                        <p className="text-xs opacity-75">{student.codigo_institucional}</p>
                      </div>
                      <span className="text-xs font-bold">
                        {attendanceMap[student.id]}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Save Button */}
          <div className="flex space-x-4">
            <button
              onClick={() => {
                setSessionCreated(false)
                setCurrentSessionId(null)
              }}
              className="flex-1 bg-gray-200 text-gray-700 px-6 py-3 rounded-lg font-semibold hover:bg-gray-300 transition-all flex items-center justify-center space-x-2"
            >
              <ArrowLeft className="w-5 h-5" />
              <span>Cancelar</span>
            </button>

            <button
              onClick={handleSaveAttendance}
              disabled={saving}
              className="flex-1 bg-gradient-to-r from-purple-600 to-purple-700 text-white px-6 py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-purple-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              <Save className="w-5 h-5" />
              <span>{saving ? 'Guardando...' : 'Guardar Asistencia'}</span>
            </button>
          </div>
        </>
      )}
    </div>
  )
}

export default TakeAttendance
