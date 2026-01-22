import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { 
  LayoutDashboard, 
  Users, 
  BookOpen, 
  UserCheck, 
  GraduationCap,
  FileText,
  LogOut,
  ClipboardCheck,
  Calendar,
  Building2
} from 'lucide-react'

const Sidebar = () => {
  const location = useLocation()
  const { user, logout } = useAuth()

  const menuItems = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/users', label: 'Usuarios', icon: Users, roles: ['Admin'] },
    { path: '/aulas', label: 'Aulas', icon: Building2, roles: ['Admin'] },
    { path: '/subjects', label: 'Materias', icon: BookOpen, roles: ['Admin', 'Profesor', 'Estudiante'] },
    { path: '/horarios', label: 'Horarios', icon: Calendar, roles: ['Admin', 'Profesor', 'Estudiante'] },
    { path: '/enrollments', label: 'Inscripciones', icon: UserCheck, roles: ['Admin'] },
    { path: '/grades', label: 'Notas', icon: GraduationCap, roles: ['Admin', 'Profesor'] },
    { path: '/attendance', label: 'Asistencia', icon: ClipboardCheck, roles: ['Profesor', 'Estudiante'] },
    { path: '/reports', label: 'Reportes', icon: FileText },
  ]

  const filteredMenuItems = menuItems.filter((item) => {
    if (!item.roles) return true
    return item.roles.includes(user?.role)
  })

  return (
    <div className="fixed inset-y-0 left-0 w-64 bg-gradient-to-b from-purple-900 via-purple-800 to-purple-900 text-white shadow-2xl">
      <div className="flex flex-col h-full">
        <div className="p-6 border-b border-purple-700/50 bg-gradient-to-r from-purple-800 to-purple-700">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-white to-purple-200 bg-clip-text text-transparent">
            SIA SOFKA U
          </h1>
          <p className="text-sm text-purple-200 mt-1">Sistema Académico</p>
        </div>

        <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
          {filteredMenuItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                  isActive
                    ? 'bg-gradient-to-r from-purple-600 to-purple-700 text-white shadow-lg transform scale-105'
                    : 'text-purple-100 hover:bg-purple-800/50 hover:translate-x-1'
                }`}
              >
                <Icon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-purple-300'}`} />
                <span className="font-medium">{item.label}</span>
              </Link>
            )
          })}
        </nav>

        <div className="p-4 border-t border-purple-700/50 bg-gradient-to-r from-purple-800 to-purple-900">
          <div className="mb-4 px-4 py-3 bg-purple-800/50 backdrop-blur-sm rounded-xl border border-purple-700/30">
            <p className="text-sm font-semibold text-white">{user?.nombre} {user?.apellido}</p>
            <p className="text-xs text-purple-200 mt-1">{user?.role}</p>
          </div>
          <button
            onClick={logout}
            className="w-full flex items-center justify-center space-x-3 px-4 py-3 rounded-xl text-purple-100 hover:bg-purple-800/70 hover:text-white transition-all duration-200 border border-purple-700/30 hover:border-purple-600 hover:shadow-lg"
          >
            <LogOut className="w-5 h-5" />
            <span className="font-medium">Cerrar sesión</span>
          </button>
        </div>
      </div>
    </div>
  )
}

export default Sidebar

