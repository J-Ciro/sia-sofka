/**
 * Services Index
 * Centralized export of all services for easy importing
 */

// Import all services
import { authService } from './authService'
import { userService } from './userService'
import { subjectService } from './subjectService'
import { enrollmentService } from './enrollmentService'
import { gradeService } from './gradeService'
import { reportService } from './reportService'
import { profileService } from './profileService'
import { profesorService } from './profesorService'
import { estudianteService } from './estudianteService'
import { classroomService } from './classroomService'
import { scheduleService } from './scheduleService'
import { attendanceService } from './attendanceService'

// Export individual services
export { authService }
export { userService }
export { subjectService }
export { enrollmentService }
export { gradeService }
export { reportService }
export { profileService }
export { profesorService }
export { estudianteService }
export { classroomService }
export { scheduleService }
export { attendanceService }

// For backward compatibility, also export as default object
export default {
  authService,
  userService,
  subjectService,
  enrollmentService,
  gradeService,
  reportService,
  profileService,
  profesorService,
  estudianteService,
  classroomService,
  scheduleService,
  attendanceService,
}