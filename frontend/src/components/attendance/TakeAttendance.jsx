import { useState, useEffect } from 'react'
import { useAuth } from '../../context/AuthContext'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { attendanceService, profesorService } from '../../services/apiService'
import { 
  CheckCircle, 
  XCircle, 
  Clock, 
  Users, 
  Calendar,
  AlertCircle,
  Save,
  ArrowLeft,
  History,
  Search
} from 'lucide-react'
import Loading from '../common/Loading'
import { useStudentSearch } from '../../hooks/useStudentSearch'
import {
  AttendanceStatus,
  getNextAttendanceState,
  countByStatus,
  getAttendanceColorClasses,
  initializeAttendanceMap,
  formatAttendanceForSubmission
} from '../../utils/attendanceHelpers'

const TakeAttendance = () => {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const sessionIdFromUrl = searchParams.get('sessionId')
  
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
  const [searchTerm, setSearchTerm] = useState('')

  // Custom hook for student search
  const filteredStudents = useStudentSearch(students, searchTerm)

  useEffect(() => {
    if (user?.id) {
      fetchSubjects()
    }
  }, [user?.id])

  useEffect(() => {
    if (sessionIdFromUrl && subjects.length > 0) {
      loadExistingSession(sessionIdFromUrl)
    }
  }, [sessionIdFromUrl, subjects])

  useEffect(() => {
    if (selectedSubject?.id && !sessionIdFromUrl) {
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
      setAttendanceMap(initializeAttendanceMap(data, AttendanceStatus.AUSENTE))
    } catch (err) {
      console.error('Error fetching students:', err)
      setStudents([])
    }
  }

  const loadExistingSession = async (sessionId) => {
    try {
      setLoading(true)
      setError('')
      
      // Cargar datos de la sesión
      const session = await attendanceService.getSession(sessionId)
      setCurrentSessionId(session.id)
      setSessionCreated(true)
      
      // Encontrar la materia correspondiente
      const subject = subjects.find(s => s.id === session.subject_id)
      if (subject) {
        setSelectedSubject(subject)
      }
      
      // Configurar fecha y horarios
      setSessionDate(session.fecha)
      const horaInicio = new Date(session.hora_inicio).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', hour12: false })
      const horaFin = new Date(session.hora_fin).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', hour12: false })
      setSessionTime({ inicio: horaInicio, fin: horaFin })
      setDescripcion(session.descripcion || '')
      
      // Cargar estudiantes y asistencias existentes
      const studentsData = await profesorService.getStudentsBySubject(session.subject_id)
      setStudents(studentsData || [])
      
      // Cargar asistencias existentes
      const attendances = await attendanceService.getSessionAttendances(sessionId)
      const attendanceMapFromServer = {}
      
      studentsData.forEach(student => {
        const existingAttendance = attendances.find(a => a.estudiante_id === student.id)
        attendanceMapFromServer[student.id] = existingAttendance ? existingAttendance.estado : 'AUSENTE'
      })
      
      setAttendanceMap(attendanceMapFromServer)
      setSuccess('Sesión cargada exitosamente')
      setTimeout(() => setSuccess(''), 3000)
      
    } catch (err) {
      console.error('Error loading session:', err)
      setError('Error al cargar la sesión')
    } finally {
      setLoading(false)
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
      setError(
        err.response?.data?.detail || err.message
      )
    } finally {
      setSaving(false)
    }
  }

  const cycleAttendanceState = (studentId) => {
    setAttendanceMap(prev => ({
      ...prev,
      [studentId]: getNextAttendanceState(prev[studentId])
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

      const attendanceUpdates = formatAttendanceForSubmission(attendanceMap)
      await attendanceService.saveSessionAttendances(currentSessionId, attendanceUpdates)
      
      setSuccess('Asistencia guardada exitosamente')
      
      // Reset después de 2 segundos
      setTimeout(() => {
        setSessionCreated(false)
        setCurrentSessionId(null)
        setDescripcion('')
        setSuccess('')
        setAttendanceMap(initializeAttendanceMap(students, AttendanceStatus.AUSENTE))
      }, 2000)
      
    } catch (err) {
      console.error('Error saving attendance:', err)
      setError(
        err.response?.data?.detail || err.message || 'Error al guardar asistencia'
      )
    } finally {
      setSaving(false)
    }
  }

  const getAttendanceIcon = (estado) => {
    switch (estado) {
      case AttendanceStatus.PRESENTE:
        return <CheckCircle className="w-5 h-5" />
      case AttendanceStatus.AUSENTE:
        return <XCircle className="w-5 h-5" />
      case AttendanceStatus.TARDANZA:
        return <Clock className="w-5 h-5" />
      default:
        return null
    }
  }

  if (loading) {
    return <Loading />
  }

  const stats = countByStatus(attendanceMap)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-purple-800 bg-clip-text text-transparent mb-1">
            Tomar Asistencia
          </h1>
          <p className="text-gray-600 text-sm">Gestiona la asistencia de tus estudiantes</p>
        </div>
        <button
          onClick={() => navigate('/attendance/history')}
          className="flex items-center gap-2 px-4 py-2 bg-white border border-purple-600 text-purple-600 rounded-lg hover:bg-purple-50 transition-colors"
        >
          <History className="w-5 h-5" />
          Ver Historial
        </button>
      </div>

      {/* Alerts */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 text-red-700 px-4 py-3 rounded-lg shadow-md flex items-center space-x-2">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <p className="font-medium">{error}</p>
        </div>
      )}

      {/* Always show success message at the top after session creation */}
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
              <label className="block text-sm font-medium text-gray-700 mb-2" htmlFor="descripcion-input">
                Descripción (opcional)
              </label>
              <input
                id="descripcion-input"
                name="descripcion"
                aria-label="Descripción"
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
                onClick={() => markAll(AttendanceStatus.PRESENTE)}
                className="bg-gradient-to-r from-green-500 to-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-green-600 hover:to-green-700 transition-all flex items-center justify-center space-x-2"
              >
                <CheckCircle className="w-5 h-5" />
                <span>Marcar Todos Presentes</span>
              </button>

              <button
                onClick={() => markAll(AttendanceStatus.AUSENTE)}
                className="bg-gradient-to-r from-red-500 to-red-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-red-600 hover:to-red-700 transition-all flex items-center justify-center space-x-2"
              >
                <XCircle className="w-5 h-5" />
                <span>Marcar Todos Ausentes</span>
              </button>

              <button
                onClick={() => markAll(AttendanceStatus.TARDANZA)}
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
                  <p className="text-2xl font-bold text-green-800">{stats[AttendanceStatus.PRESENTE]}</p>
                </div>
                <CheckCircle className="w-10 h-10 text-green-600" />
              </div>
            </div>

            <div className="bg-red-50 rounded-xl shadow-md p-4 border border-red-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-red-700 font-medium">Ausentes</p>
                  <p className="text-2xl font-bold text-red-800">{stats[AttendanceStatus.AUSENTE]}</p>
                </div>
                <XCircle className="w-10 h-10 text-red-600" />
              </div>
            </div>

            <div className="bg-yellow-50 rounded-xl shadow-md p-4 border border-yellow-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-yellow-700 font-medium">Tardanzas</p>
                  <p className="text-2xl font-bold text-yellow-800">{stats[AttendanceStatus.TARDANZA]}</p>
                </div>
                <Clock className="w-10 h-10 text-yellow-600" />
              </div>
            </div>
          </div>

          {/* Students List: always show heading even if empty */}
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-800">
                Lista de Estudiantes ({filteredStudents.length})
              </h2>
            </div>

            {/* Search Bar */}
            <div className="relative mb-4">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Buscar por nombre o código..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>

            {students.length === 0 ? (
              <div className="text-center py-8">
                <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No hay estudiantes matriculados en esta materia</p>
              </div>
            ) : filteredStudents.length === 0 ? (
              <div className="text-center py-8">
                <Search className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No se encontraron estudiantes con "{searchTerm}"</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredStudents.map(student => (
                  <button
                    key={student.id}
                    onClick={() => cycleAttendanceState(student.id)}
                    className={`p-4 rounded-lg border-2 transition-all hover:shadow-md ${getAttendanceColorClasses(attendanceMap[student.id])}`}
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
