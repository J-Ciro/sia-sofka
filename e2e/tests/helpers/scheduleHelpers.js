/**
 * Helper functions for Schedule E2E Tests
 * Provides utilities for generating test data, time calculations, and schedule validation
 */

/**
 * Generate test schedule data with unique identifiers
 * @param {number} index - Unique index for generating different schedules
 * @returns {Object} Schedule data object
 */
export function generateTestSchedule(index) {
  const subjects = [
    'Matemáticas Avanzadas',
    'Física Cuántica', 
    'Química Orgánica',
    'Biología Molecular',
    'Estadística Aplicada',
    'Cálculo Diferencial',
    'Álgebra Lineal',
    'Geometría Analítica',
    'Programación Avanzada',
    'Bases de Datos'
  ];

  const professors = [
    'Dr. Juan Pérez',
    'Dr. María García',
    'Dr. Carlos López',
    'Dr. Ana Rodríguez',
    'Dr. Pedro Martínez',
    'Dr. Laura Fernández',
    'Dr. Roberto Silva',
    'Dr. Carmen Ruiz',
    'Dr. Miguel Torres',
    'Dr. Elena Morales'
  ];

  const classrooms = [
    'Aula 301',
    'Aula 302',
    'Aula 303',
    'Laboratorio 1',
    'Laboratorio 2',
    'Auditorio A',
    'Auditorio B',
    'Sala de Conferencias',
    'Aula Magna',
    'Biblioteca'
  ];

  const days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];

  return {
    materia: subjects[index % subjects.length],
    profesor: professors[index % professors.length],
    salon: classrooms[index % classrooms.length],
    dia: days[index % days.length],
    horaInicio: generateTimeSlot(index).start,
    horaFin: generateTimeSlot(index).end
  };
}

/**
 * Generate time slots for testing
 * @param {number} index - Index to generate different time slots
 * @returns {Object} Time slot with start and end times
 */
export function generateTimeSlot(index) {
  const timeSlots = [
    { start: '08:00', end: '10:00' },
    { start: '10:00', end: '12:00' },
    { start: '14:00', end: '16:00' },
    { start: '16:00', end: '18:00' },
    { start: '18:00', end: '20:00' },
    { start: '07:00', end: '09:00' },
    { start: '09:00', end: '11:00' },
    { start: '11:00', end: '13:00' },
    { start: '13:00', end: '15:00' },
    { start: '15:00', end: '17:00' }
  ];

  return timeSlots[index % timeSlots.length];
}

/**
 * Generate conflicting schedule data (same classroom, overlapping time)
 * @param {Object} baseSchedule - Base schedule to create conflict with
 * @param {string} conflictType - Type of conflict: 'classroom', 'professor', or 'both'
 * @returns {Object} Conflicting schedule data
 */
export function generateConflictingSchedule(baseSchedule, conflictType = 'classroom') {
  const conflictSchedule = {
    materia: 'Materia Conflictiva',
    profesor: 'Dr. Conflicto Test',
    salon: 'Aula Conflicto',
    dia: baseSchedule.dia,
    horaInicio: addMinutesToTime(baseSchedule.horaInicio, 30), // 30 minutes overlap
    horaFin: addMinutesToTime(baseSchedule.horaFin, 30)
  };

  switch (conflictType) {
    case 'classroom':
      conflictSchedule.salon = baseSchedule.salon; // Same classroom
      break;
    case 'professor':
      conflictSchedule.profesor = baseSchedule.profesor; // Same professor
      break;
    case 'both':
      conflictSchedule.salon = baseSchedule.salon;
      conflictSchedule.profesor = baseSchedule.profesor;
      break;
  }

  return conflictSchedule;
}

/**
 * Generate non-conflicting schedule data
 * @param {Object} baseSchedule - Base schedule to avoid conflict with
 * @param {string} avoidanceType - How to avoid conflict: 'time', 'day', 'classroom', 'professor'
 * @returns {Object} Non-conflicting schedule data
 */
export function generateNonConflictingSchedule(baseSchedule, avoidanceType = 'time') {
  const nonConflictSchedule = { ...baseSchedule };
  nonConflictSchedule.materia = 'Materia Sin Conflicto';

  switch (avoidanceType) {
    case 'time':
      // Consecutive time slot
      nonConflictSchedule.horaInicio = baseSchedule.horaFin;
      nonConflictSchedule.horaFin = addMinutesToTime(baseSchedule.horaFin, 120); // 2 hours later
      break;
    case 'day':
      // Different day
      const days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
      const currentDayIndex = days.indexOf(baseSchedule.dia);
      nonConflictSchedule.dia = days[(currentDayIndex + 1) % days.length];
      break;
    case 'classroom':
      // Different classroom
      nonConflictSchedule.salon = baseSchedule.salon === 'Aula 301' ? 'Aula 302' : 'Aula 301';
      break;
    case 'professor':
      // Different professor
      nonConflictSchedule.profesor = baseSchedule.profesor === 'Dr. Juan Pérez' ? 'Dr. María García' : 'Dr. Juan Pérez';
      break;
  }

  return nonConflictSchedule;
}

/**
 * Add minutes to a time string
 * @param {string} timeString - Time in HH:MM format
 * @param {number} minutes - Minutes to add
 * @returns {string} New time in HH:MM format
 */
export function addMinutesToTime(timeString, minutes) {
  const [hours, mins] = timeString.split(':').map(Number);
  const totalMinutes = hours * 60 + mins + minutes;
  
  const newHours = Math.floor(totalMinutes / 60) % 24;
  const newMins = totalMinutes % 60;
  
  return `${newHours.toString().padStart(2, '0')}:${newMins.toString().padStart(2, '0')}`;
}

/**
 * Calculate duration between two times
 * @param {string} startTime - Start time in HH:MM format
 * @param {string} endTime - End time in HH:MM format
 * @returns {number} Duration in minutes
 */
export function calculateDuration(startTime, endTime) {
  const [startHours, startMins] = startTime.split(':').map(Number);
  const [endHours, endMins] = endTime.split(':').map(Number);
  
  const startTotalMins = startHours * 60 + startMins;
  const endTotalMins = endHours * 60 + endMins;
  
  return endTotalMins - startTotalMins;
}

/**
 * Check if two time ranges overlap
 * @param {Object} range1 - First time range {start, end}
 * @param {Object} range2 - Second time range {start, end}
 * @returns {boolean} True if ranges overlap
 */
export function timeRangesOverlap(range1, range2) {
  const start1 = timeToMinutes(range1.start);
  const end1 = timeToMinutes(range1.end);
  const start2 = timeToMinutes(range2.start);
  const end2 = timeToMinutes(range2.end);
  
  return start1 < end2 && start2 < end1;
}

/**
 * Convert time string to minutes since midnight
 * @param {string} timeString - Time in HH:MM format
 * @returns {number} Minutes since midnight
 */
export function timeToMinutes(timeString) {
  const [hours, minutes] = timeString.split(':').map(Number);
  return hours * 60 + minutes;
}

/**
 * Generate boundary time test cases
 * @returns {Array} Array of boundary time test cases
 */
export function getBoundaryTimeCases() {
  return [
    {
      name: 'Earliest possible time',
      horaInicio: '00:00',
      horaFin: '01:00'
    },
    {
      name: 'Latest possible time',
      horaInicio: '23:00',
      horaFin: '23:59'
    },
    {
      name: 'Minimum duration (30 minutes)',
      horaInicio: '10:00',
      horaFin: '10:30'
    },
    {
      name: 'Maximum duration (6 hours)',
      horaInicio: '08:00',
      horaFin: '14:00'
    },
    {
      name: 'Invalid - end before start',
      horaInicio: '10:00',
      horaFin: '09:00',
      shouldFail: true
    },
    {
      name: 'Invalid - too short (15 minutes)',
      horaInicio: '10:00',
      horaFin: '10:15',
      shouldFail: true
    },
    {
      name: 'Invalid - too long (7 hours)',
      horaInicio: '08:00',
      horaFin: '15:00',
      shouldFail: true
    }
  ];
}

/**
 * Generate filter test data
 * @returns {Object} Filter test scenarios
 */
export function getFilterTestData() {
  return {
    professors: ['Dr. Juan Pérez', 'Dr. María García', 'Dr. Carlos López'],
    classrooms: ['Aula 301', 'Aula 302', 'Laboratorio 1'],
    subjects: ['Matemáticas Avanzadas', 'Física Cuántica', 'Química Orgánica'],
    days: ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'],
    combinations: [
      { profesor: 'Dr. Juan Pérez', dia: 'Lunes' },
      { salon: 'Aula 301', materia: 'Matemáticas Avanzadas' },
      { profesor: 'Dr. María García', salon: 'Laboratorio 1', dia: 'Miércoles' }
    ]
  };
}

/**
 * Generate export test scenarios
 * @returns {Array} Export test configurations
 */
export function getExportTestScenarios() {
  return [
    {
      name: 'Weekly horizontal all schedules',
      vista: 'Semanal',
      orientacion: 'Horizontal',
      incluir: 'Todos',
      expectedFilename: /horarios_semana_\d+_2026\.pdf/
    },
    {
      name: 'Weekly vertical filtered schedules',
      vista: 'Semanal',
      orientacion: 'Vertical',
      incluir: 'Solo filtrados',
      expectedFilename: /horarios_filtrados_\d+\.pdf/
    },
    {
      name: 'Monthly horizontal all schedules',
      vista: 'Mensual',
      orientacion: 'Horizontal',
      incluir: 'Todos',
      expectedFilename: /horarios_mes_\d+_2026\.pdf/
    }
  ];
}

/**
 * Generate notification test data
 * @returns {Object} Notification test scenarios
 */
export function getNotificationTestData() {
  return {
    scheduleModified: {
      type: 'modification',
      message: /horario.*modificado/i,
      action: 'Ver Horario Actualizado'
    },
    scheduleDeleted: {
      type: 'deletion',
      message: /clase.*cancelada/i,
      action: null
    },
    scheduleCreated: {
      type: 'creation',
      message: /nuevo horario asignado/i,
      action: 'Ver Nuevo Horario'
    }
  };
}

/**
 * Validate schedule data completeness
 * @param {Object} scheduleData - Schedule data to validate
 * @returns {Object} Validation result with isValid and errors
 */
export function validateScheduleData(scheduleData) {
  const errors = [];
  const requiredFields = ['materia', 'profesor', 'salon', 'dia', 'horaInicio', 'horaFin'];
  
  // Check required fields
  for (const field of requiredFields) {
    if (!scheduleData[field]) {
      errors.push(`Campo requerido faltante: ${field}`);
    }
  }
  
  // Validate time format
  const timeRegex = /^([01]?[0-9]|2[0-3]):[0-5][0-9]$/;
  if (scheduleData.horaInicio && !timeRegex.test(scheduleData.horaInicio)) {
    errors.push('Formato de hora inicio inválido');
  }
  if (scheduleData.horaFin && !timeRegex.test(scheduleData.horaFin)) {
    errors.push('Formato de hora fin inválido');
  }
  
  // Validate time logic
  if (scheduleData.horaInicio && scheduleData.horaFin) {
    const duration = calculateDuration(scheduleData.horaInicio, scheduleData.horaFin);
    
    if (duration <= 0) {
      errors.push('La hora de fin debe ser posterior a la hora de inicio');
    }
    if (duration < 30) {
      errors.push('La clase debe durar al menos 30 minutos');
    }
    if (duration > 360) { // 6 hours
      errors.push('La clase no puede durar más de 6 horas');
    }
  }
  
  // Validate day
  const validDays = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
  if (scheduleData.dia && !validDays.includes(scheduleData.dia)) {
    errors.push('Día de la semana inválido');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
}

/**
 * Generate performance test data (many schedules)
 * @param {number} count - Number of schedules to generate
 * @returns {Array} Array of schedule data objects
 */
export function generateManySchedules(count = 50) {
  const schedules = [];
  
  for (let i = 0; i < count; i++) {
    schedules.push(generateTestSchedule(i));
  }
  
  return schedules;
}

/**
 * Get week date range for calendar navigation tests
 * @param {number} weekOffset - Weeks from current week (negative for past, positive for future)
 * @returns {Object} Week range with start and end dates
 */
export function getWeekRange(weekOffset = 0) {
  const now = new Date();
  const currentDay = now.getDay(); // 0 = Sunday, 1 = Monday, etc.
  const mondayOffset = currentDay === 0 ? -6 : 1 - currentDay; // Get Monday of current week
  
  const monday = new Date(now);
  monday.setDate(now.getDate() + mondayOffset + (weekOffset * 7));
  
  const saturday = new Date(monday);
  saturday.setDate(monday.getDate() + 5);
  
  return {
    start: monday.toISOString().split('T')[0], // YYYY-MM-DD format
    end: saturday.toISOString().split('T')[0],
    label: `${monday.getDate()} ${getMonthName(monday.getMonth())} - ${saturday.getDate()} ${getMonthName(saturday.getMonth())} ${saturday.getFullYear()}`
  };
}

/**
 * Get month name in Spanish
 * @param {number} monthIndex - Month index (0-11)
 * @returns {string} Month name in Spanish
 */
function getMonthName(monthIndex) {
  const months = [
    'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
    'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'
  ];
  return months[monthIndex];
}

/**
 * Generate calendar color test data
 * @returns {Array} Expected color mappings for subjects
 */
export function getSubjectColorMappings() {
  return [
    { subject: 'Matemáticas Avanzadas', expectedColorClass: 'bg-blue-500' },
    { subject: 'Física Cuántica', expectedColorClass: 'bg-green-500' },
    { subject: 'Química Orgánica', expectedColorClass: 'bg-red-500' },
    { subject: 'Biología Molecular', expectedColorClass: 'bg-purple-500' },
    { subject: 'Estadística Aplicada', expectedColorClass: 'bg-yellow-500' }
  ];
}

/**
 * Generate conflict resolution test scenarios
 * @returns {Array} Conflict resolution scenarios
 */
export function getConflictResolutionScenarios() {
  return [
    {
      name: 'Resolve classroom conflict by changing classroom',
      originalSchedule: {
        materia: 'Matemáticas',
        profesor: 'Dr. Pérez',
        salon: 'Aula 301',
        dia: 'Lunes',
        horaInicio: '08:00',
        horaFin: '10:00'
      },
      conflictingSchedule: {
        materia: 'Física',
        profesor: 'Dr. García',
        salon: 'Aula 301', // Same classroom
        dia: 'Lunes',
        horaInicio: '09:00',
        horaFin: '11:00'
      },
      resolution: {
        salon: 'Aula 302' // Change classroom
      }
    },
    {
      name: 'Resolve professor conflict by changing time',
      originalSchedule: {
        materia: 'Matemáticas',
        profesor: 'Dr. Pérez',
        salon: 'Aula 301',
        dia: 'Lunes',
        horaInicio: '08:00',
        horaFin: '10:00'
      },
      conflictingSchedule: {
        materia: 'Álgebra',
        profesor: 'Dr. Pérez', // Same professor
        salon: 'Aula 302',
        dia: 'Lunes',
        horaInicio: '09:00',
        horaFin: '11:00'
      },
      resolution: {
        horaInicio: '10:00', // Change time to be consecutive
        horaFin: '12:00'
      }
    }
  ];
}