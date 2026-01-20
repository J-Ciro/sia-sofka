import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Login from './components/auth/Login'
import DashboardLayout from './components/layout/DashboardLayout'
import DashboardHome from './components/dashboard/DashboardHome'
import Users from './components/dashboard/Users'
import Subjects from './components/dashboard/Subjects'
import ProfesorSubjects from './components/dashboard/ProfesorSubjects'
import EstudianteSubjects from './components/dashboard/EstudianteSubjects'
import Enrollments from './components/dashboard/Enrollments'
import Grades from './components/dashboard/Grades'
import Reports from './components/dashboard/Reports'
import TakeAttendance from './components/attendance/TakeAttendance'
import StudentAttendanceHistory from './components/attendance/StudentAttendanceHistory'
import SessionHistory from './components/attendance/SessionHistory'

// Componente para renderizar Subjects según el rol
const SubjectsRoute = () => {
  const { user } = useAuth()
  
  if (user?.role === 'Profesor') {
    return <ProfesorSubjects />
  } else if (user?.role === 'Estudiante') {
    return <EstudianteSubjects />
  } else {
    return <Subjects />
  }
}

// Componente para renderizar Attendance según el rol
const AttendanceRoute = () => {
  const { user } = useAuth()
  
  if (user?.role === 'Profesor') {
    return <TakeAttendance />
  } else if (user?.role === 'Estudiante') {
    return <StudentAttendanceHistory />
  } else {
    return <Navigate to="/" replace />
  }
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<DashboardLayout />}>
            <Route index element={<DashboardHome />} />
            <Route path="users" element={<Users />} />
            <Route path="subjects" element={<SubjectsRoute />} />
            <Route path="enrollments" element={<Enrollments />} />
            <Route path="grades" element={<Grades />} />
            <Route path="reports" element={<Reports />} />
            <Route path="attendance" element={<AttendanceRoute />} />
            <Route path="attendance/history" element={<SessionHistory />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App

