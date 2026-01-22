/**
 * Debug utility to check current user permissions and schedule ownership
 * Run this in the browser console to debug permission issues
 */

export const debugPermissions = async () => {
  try {
    console.log('=== DEBUGGING SCHEDULE PERMISSIONS ===');
    
    // Check current user
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    console.log('Current User:', {
      id: user.id,
      email: user.email,
      role: user.role,
      name: `${user.nombre} ${user.apellido}`,
      hasToken: !!token
    });
    
    if (!token) {
      console.error('❌ No authentication token found!');
      return;
    }
    
    // Import API service
    const { scheduleService, subjectService } = await import('../services');
    
    // Get user's subjects (if professor)
    if (user.role === 'Profesor') {
      console.log('\n--- Professor Subjects ---');
      try {
        const subjects = await subjectService.getAll();
        console.log('Subjects assigned to this professor:', subjects.map(s => ({
          id: s.id,
          name: s.nombre,
          professor_id: s.profesor_id,
          isOwned: s.profesor_id === user.id
        })));
      } catch (error) {
        console.error('Error fetching subjects:', error);
      }
    }
    
    // Get current schedules
    console.log('\n--- Current Schedules ---');
    try {
      const schedules = await scheduleService.getWeekly();
      console.log('Current schedules:', schedules.map(s => ({
        id: s.id,
        subject_name: s.subject?.nombre,
        subject_id: s.subject_id,
        professor_id: s.subject?.profesor_id,
        canUpdate: user.role === 'Admin' || (user.role === 'Profesor' && s.subject?.profesor_id === user.id),
        day: s.dia_semana,
        time: `${s.hora_inicio}-${s.hora_fin}`,
        specific_date: s.fecha_especifica
      })));
    } catch (error) {
      console.error('Error fetching schedules:', error);
    }
    
    console.log('\n=== END DEBUG ===');
    
  } catch (error) {
    console.error('Debug error:', error);
  }
};

// Make it available globally for console use
if (typeof window !== 'undefined') {
  window.debugPermissions = debugPermissions;
}