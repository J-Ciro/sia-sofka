import { useState, useEffect } from 'react'
import { userService } from '../../services/apiService'
import { Plus, Edit, Trash2, GraduationCap, Users as UsersIcon, FileSpreadsheet } from 'lucide-react'
import UserModal from '../modals/UserModal'
import BulkImportModal from '../modals/BulkImportModal'
import Loading from '../common/Loading'

const Users = () => {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isBulkModalOpen, setIsBulkModalOpen] = useState(false)
  const [selectedUser, setSelectedUser] = useState(null)
  const [deleteConfirm, setDeleteConfirm] = useState(null)

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await userService.getAll()
      setUsers(data)
    } catch (err) {
      setError(err.message || 'Error al cargar usuarios')
      console.error('Error fetching users:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    setSelectedUser(null)
    setIsModalOpen(true)
  }

  const handleEdit = (user) => {
    setSelectedUser(user)
    setIsModalOpen(true)
  }

  const handleDelete = async (userId) => {
    if (!window.confirm('¿Estás seguro de que deseas eliminar este usuario?')) {
      return
    }

    try {
      await userService.delete(userId)
      setSuccess('Usuario eliminado exitosamente')
      fetchUsers()
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(err.message || 'Error al eliminar usuario')
      setTimeout(() => setError(''), 5000)
    }
  }

  const handleModalSubmit = async (userData) => {
    try {
      setError('')
      if (selectedUser) {
        await userService.update(selectedUser.id, userData)
        setSuccess('Usuario actualizado exitosamente')
      } else {
        await userService.create(userData)
        setSuccess('Usuario creado exitosamente')
      }
      setIsModalOpen(false)
      fetchUsers()
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(err.message || 'Error al guardar usuario')
      setTimeout(() => setError(''), 5000)
    }
  }

  if (loading) {
    return <Loading />
  }

  // Separar usuarios por rol
  const profesores = users.filter(user => user.role === 'Profesor')
  const estudiantes = users.filter(user => user.role === 'Estudiante')
  const admins = users.filter(user => user.role === 'Admin')

  // Componente para renderizar una tabla de usuarios
  const UserTable = ({ users, emptyMessage }) => {
    if (users.length === 0) {
      return (
        <tr>
          <td colSpan="5" className="px-6 py-8 text-center text-gray-500">
            <div className="flex flex-col items-center justify-center">
              <UsersIcon className="w-12 h-12 text-gray-300 mb-2" />
              <p className="text-sm">{emptyMessage}</p>
            </div>
          </td>
        </tr>
      )
    }

    return (
      <>
        {users.map((user) => (
          <tr key={user.id} className="hover:bg-purple-50 transition-colors duration-150">
            <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">
              {user.nombre} {user.apellido}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-gray-700">{user.email}</td>
            <td className="px-6 py-4 whitespace-nowrap">
              <span className={`px-3 py-1.5 text-xs font-semibold rounded-full ${
                user.role === 'Admin' ? 'bg-gradient-to-r from-purple-500 to-purple-600 text-white shadow-md' :
                user.role === 'Profesor' ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-md' :
                'bg-gradient-to-r from-green-500 to-green-600 text-white shadow-md'
              }`}>
                {user.role}
              </span>
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-gray-700">
              {user.codigo_institucional}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => handleEdit(user)}
                  className="p-2 text-purple-600 hover:text-white hover:bg-purple-600 rounded-lg transition-all duration-200 hover:scale-110"
                  title="Editar"
                >
                  <Edit className="w-5 h-5" />
                </button>
                <button
                  onClick={() => handleDelete(user.id)}
                  className="p-2 text-red-600 hover:text-white hover:bg-red-600 rounded-lg transition-all duration-200 hover:scale-110"
                  title="Eliminar"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            </td>
          </tr>
        ))}
      </>
    )
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-purple-800 bg-clip-text text-transparent mb-1">
            Usuarios
          </h1>
          <p className="text-gray-600 text-sm">Gestiona los usuarios del sistema</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsBulkModalOpen(true)}
            className="flex items-center space-x-2 px-4 py-3 bg-white border-2 border-purple-600 text-purple-600 rounded-xl hover:bg-purple-50 shadow transition-all duration-200 font-semibold"
          >
            <FileSpreadsheet className="w-5 h-5" />
            <span>Importar Excel</span>
          </button>
          <button
            onClick={handleCreate}
            className="flex items-center space-x-2 px-5 py-3 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-xl hover:from-purple-700 hover:to-purple-800 shadow-lg hover:shadow-xl transition-all duration-200 font-semibold transform hover:scale-105"
          >
            <Plus className="w-5 h-5" />
            <span>Nuevo Usuario</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 text-red-700 px-4 py-3 rounded-lg mb-4 shadow-md">
          <p className="font-medium">{error}</p>
        </div>
      )}

      {success && (
        <div className="bg-green-50 border-l-4 border-green-500 text-green-700 px-4 py-3 rounded-lg mb-4 shadow-md">
          <p className="font-medium">{success}</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Sección de Profesores */}
        <div className="bg-white rounded-2xl shadow-lg overflow-hidden border border-gray-100 hover:shadow-xl transition-shadow duration-300">
          <div className="bg-gradient-to-r from-blue-500 to-blue-600 px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-white/20 rounded-lg">
                  <GraduationCap className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">Profesores</h2>
                  <p className="text-blue-100 text-sm">{profesores.length} {profesores.length === 1 ? 'profesor' : 'profesores'}</p>
                </div>
              </div>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-blue-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-blue-900 uppercase tracking-wider">
                    Nombre
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-blue-900 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-blue-900 uppercase tracking-wider">
                    Código
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-blue-900 uppercase tracking-wider">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {profesores.length === 0 ? (
                  <tr>
                    <td colSpan="4" className="px-6 py-8 text-center text-gray-500">
                      <div className="flex flex-col items-center justify-center">
                        <GraduationCap className="w-12 h-12 text-gray-300 mb-2" />
                        <p className="text-sm">No hay profesores registrados</p>
                      </div>
                    </td>
                  </tr>
                ) : (
                  profesores.map((user) => (
                    <tr key={user.id} className="hover:bg-blue-50 transition-colors duration-150">
                      <td className="px-4 py-3 whitespace-nowrap font-medium text-gray-900">
                        {user.nombre} {user.apellido}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-gray-700 text-sm">{user.email}</td>
                      <td className="px-4 py-3 whitespace-nowrap text-gray-700 text-sm">
                        {user.codigo_institucional}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm font-medium">
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => handleEdit(user)}
                            className="p-2 text-blue-600 hover:text-white hover:bg-blue-600 rounded-lg transition-all duration-200 hover:scale-110"
                            title="Editar"
                          >
                            <Edit className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDelete(user.id)}
                            className="p-2 text-red-600 hover:text-white hover:bg-red-600 rounded-lg transition-all duration-200 hover:scale-110"
                            title="Eliminar"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Sección de Estudiantes */}
        <div className="bg-white rounded-2xl shadow-lg overflow-hidden border border-gray-100 hover:shadow-xl transition-shadow duration-300">
          <div className="bg-gradient-to-r from-green-500 to-green-600 px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-white/20 rounded-lg">
                  <UsersIcon className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">Estudiantes</h2>
                  <p className="text-green-100 text-sm">{estudiantes.length} {estudiantes.length === 1 ? 'estudiante' : 'estudiantes'}</p>
                </div>
              </div>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-green-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-green-900 uppercase tracking-wider">
                    Nombre
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-green-900 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-green-900 uppercase tracking-wider">
                    Código
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-green-900 uppercase tracking-wider">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {estudiantes.length === 0 ? (
                  <tr>
                    <td colSpan="4" className="px-6 py-8 text-center text-gray-500">
                      <div className="flex flex-col items-center justify-center">
                        <UsersIcon className="w-12 h-12 text-gray-300 mb-2" />
                        <p className="text-sm">No hay estudiantes registrados</p>
                      </div>
                    </td>
                  </tr>
                ) : (
                  estudiantes.map((user) => (
                    <tr key={user.id} className="hover:bg-green-50 transition-colors duration-150">
                      <td className="px-4 py-3 whitespace-nowrap font-medium text-gray-900">
                        {user.nombre} {user.apellido}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-gray-700 text-sm">{user.email}</td>
                      <td className="px-4 py-3 whitespace-nowrap text-gray-700 text-sm">
                        {user.codigo_institucional}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm font-medium">
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => handleEdit(user)}
                            className="p-2 text-green-600 hover:text-white hover:bg-green-600 rounded-lg transition-all duration-200 hover:scale-110"
                            title="Editar"
                          >
                            <Edit className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDelete(user.id)}
                            className="p-2 text-red-600 hover:text-white hover:bg-red-600 rounded-lg transition-all duration-200 hover:scale-110"
                            title="Eliminar"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Sección de Administradores (si existen) */}
      {admins.length > 0 && (
        <div className="bg-white rounded-2xl shadow-lg overflow-hidden border border-gray-100 hover:shadow-xl transition-shadow duration-300 mt-6">
          <div className="bg-gradient-to-r from-purple-500 to-purple-600 px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-white/20 rounded-lg">
                  <UsersIcon className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">Administradores</h2>
                  <p className="text-purple-100 text-sm">{admins.length} {admins.length === 1 ? 'administrador' : 'administradores'}</p>
                </div>
              </div>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-purple-50">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-purple-900 uppercase tracking-wider">
                    Nombre
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-purple-900 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-purple-900 uppercase tracking-wider">
                    Código Institucional
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-purple-900 uppercase tracking-wider">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {admins.map((user) => (
                  <tr key={user.id} className="hover:bg-purple-50 transition-colors duration-150">
                    <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">
                      {user.nombre} {user.apellido}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-700">{user.email}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-700">
                      {user.codigo_institucional}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex items-center space-x-3">
                        <button
                          onClick={() => handleEdit(user)}
                          className="p-2 text-purple-600 hover:text-white hover:bg-purple-600 rounded-lg transition-all duration-200 hover:scale-110"
                          title="Editar"
                        >
                          <Edit className="w-5 h-5" />
                        </button>
                        <button
                          onClick={() => handleDelete(user.id)}
                          className="p-2 text-red-600 hover:text-white hover:bg-red-600 rounded-lg transition-all duration-200 hover:scale-110"
                          title="Eliminar"
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <UserModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          setSelectedUser(null)
        }}
        user={selectedUser}
        onSubmit={handleModalSubmit}
      />

      <BulkImportModal
        isOpen={isBulkModalOpen}
        onClose={() => setIsBulkModalOpen(false)}
        onSuccess={fetchUsers}
      />
    </div>
  )
}

export default Users
