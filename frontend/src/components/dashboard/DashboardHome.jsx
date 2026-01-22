import { useState, useEffect } from 'react'
import { Users, BookOpen, GraduationCap, UserCheck } from 'lucide-react'
import StatsCard from '../common/StatsCard'
import { userService, subjectService, enrollmentService, gradeService, profesorService, estudianteService } from '../../services'
import { useAuth } from '../../context/AuthContext'
import Loading from '../common/Loading'

const DashboardHome = () => {
  const { user } = useAuth()
  const [stats, setStats] = useState({
    users: 0,
    subjects: 0,
    enrollments: 0,
    grades: 0,
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (user?.id) {
      fetchStats()
    }
  }, [user?.id])

  const fetchStats = async () => {
    try {
      setLoading(true)
      
      if (user?.role === 'Admin') {
        // Admin: todas las estadísticas
        const [users, subjects, enrollments, grades] = await Promise.all([
          userService.getAll(),
          subjectService.getAll(),
          enrollmentService.getAll(),
          gradeService.getAll(),
        ])

        setStats({
          users: users.length || 0,
          subjects: subjects.length || 0,
          enrollments: enrollments.length || 0,
          grades: grades.length || 0,
        })
      } else if (user?.role === 'Profesor') {
        // Profesor: sus materias y estudiantes inscritos en sus materias
        try {
          const mySubjects = await profesorService.getAssignedSubjects(user.id)
          if (!mySubjects || mySubjects.length === 0) {
            setStats({ users: 0, subjects: 0, enrollments: 0, grades: 0 })
            return
          }
          
          // Obtener estudiantes únicos inscritos en las materias del profesor
          const uniqueStudents = new Set()
          let totalEnrollments = 0
          let totalGrades = 0
          
          for (const subject of mySubjects) {
            if (subject?.id) {
              try {
                // Obtener inscripciones de la materia
                const enrollments = await profesorService.getEnrollmentsBySubject(subject.id)
                totalEnrollments += (enrollments?.length || 0)
                
                // Agregar estudiantes únicos
                enrollments?.forEach(enrollment => {
                  if (enrollment.estudiante_id) {
                    uniqueStudents.add(enrollment.estudiante_id)
                  }
                })
                
                // Obtener notas de la materia
                const grades = await gradeService.getAll({ subject_id: subject.id })
                totalGrades += (grades?.length || 0)
              } catch (err) {
                // Silenciar errores individuales, solo loguear
                console.warn(`No se pudieron obtener datos para materia ${subject.id}:`, err)
              }
            }
          }
          
          setStats({
            users: uniqueStudents.size, // Total de estudiantes únicos
            subjects: mySubjects.length || 0,
            enrollments: totalEnrollments,
            grades: totalGrades,
          })
        } catch (err) {
          console.error('Error fetching profesor stats:', err)
          setStats({ users: 0, subjects: 0, enrollments: 0, grades: 0 })
        }
      } else if (user?.role === 'Estudiante') {
        // Estudiante: sus materias y notas
        try {
          const enrollments = await estudianteService.getMyEnrollments(user.id)
          if (!enrollments || enrollments.length === 0) {
            setStats({ users: 0, subjects: 0, enrollments: 0, grades: 0 })
            return
          }
          
          // Obtener notas del estudiante
          let totalGrades = 0
          for (const enrollment of enrollments) {
            const subjectId = enrollment.subject_id || enrollment.subject?.id
            if (subjectId) {
              try {
                const grades = await gradeService.getAll({ subject_id: subjectId })
                // Filtrar solo las notas del estudiante
                const myGrades = (grades || []).filter(
                  (g) => g.enrollment?.estudiante_id === user.id
                )
                totalGrades += myGrades.length
              } catch (err) {
                // Silenciar errores individuales, solo loguear
                console.warn(`No se pudieron obtener notas para materia ${subjectId}:`, err)
              }
            }
          }
          
          setStats({
            users: 0,
            subjects: enrollments.length || 0,
            enrollments: enrollments.length || 0,
            grades: totalGrades,
          })
        } catch (err) {
          // Silenciar errores 403, ya que el servicio los maneja
          if (err.response?.status !== 403 && err.response?.status !== 401) {
            console.error('Error fetching estudiante stats:', err)
          }
          setStats({ users: 0, subjects: 0, enrollments: 0, grades: 0 })
        }
      }
    } catch (error) {
      console.error('Error fetching stats:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <Loading />
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-purple-800 bg-clip-text text-transparent mb-2">
          Dashboard
        </h1>
        <p className="text-gray-600">Bienvenido al Sistema de Información Académica</p>
      </div>
      
      <div className={`grid grid-cols-1 md:grid-cols-2 ${user?.role === 'Estudiante' ? 'lg:grid-cols-2' : 'lg:grid-cols-4'} gap-6 mb-8`}>
        {/* Solo mostrar Total Usuarios para Admin y Profesor */}
        {(user?.role === 'Admin' || user?.role === 'Profesor') && (
          <StatsCard
            title={user?.role === 'Admin' ? 'Total Usuarios' : 'Mis Estudiantes'}
            value={stats.users}
            icon={Users}
            color="purple"
          />
        )}
        <StatsCard
          title={user?.role === 'Estudiante' ? 'Mis Materias' : user?.role === 'Profesor' ? 'Materias Asignadas' : 'Materias'}
          value={stats.subjects}
          icon={BookOpen}
          color="blue"
        />
        {(user?.role === 'Admin' || user?.role === 'Profesor') && (
          <StatsCard
            title="Inscripciones"
            value={stats.enrollments}
            icon={UserCheck}
            color="green"
          />
        )}
        <StatsCard
          title={user?.role === 'Estudiante' ? 'Mis Notas' : 'Notas Registradas'}
          value={stats.grades}
          icon={GraduationCap}
          color="purple"
        />
      </div>

      <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 hover:shadow-xl transition-shadow duration-300">
        <div className="flex items-center space-x-4 mb-4">
          <div className="p-3 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl">
            <GraduationCap className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Sistema de Información Académica SOFKA U</h2>
            <p className="text-gray-600 mt-1">Gestión académica integral</p>
          </div>
        </div>
        <div className="mt-6 pt-6 border-t border-gray-200">
          <p className="text-gray-600 leading-relaxed">
            {user?.role === 'Admin'
              ? 'Administra usuarios, materias, inscripciones y notas de manera eficiente y centralizada.'
              : user?.role === 'Profesor'
              ? 'Gestiona tus materias asignadas, estudiantes y calificaciones académicas.'
              : 'Consulta tus materias inscritas, calificaciones y genera reportes académicos.'}
          </p>
        </div>
      </div>
    </div>
  )
}

export default DashboardHome
