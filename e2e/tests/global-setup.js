/**
 * Global setup for Playwright tests
 * Runs once before all tests
 * 
 * This setup ensures the test environment is ready by:
 * 1. Verifying backend is running
 * 2. Cleaning up any existing test data via API
 * 
 * No external scripts needed - everything via API calls
 */

import { request } from '@playwright/test';

export default async function globalSetup() {
  console.log('\n🔧 Setting up test environment...\n');
  
  const apiContext = await request.newContext({
    baseURL: process.env.API_URL || 'http://localhost:8000',
  });
  
  try {
    // 1. Verify backend is running
    console.log('📡 Checking backend connection...');
    const healthCheck = await apiContext.get('/health').catch(() => null);
    
    if (!healthCheck || !healthCheck.ok()) {
      console.warn('⚠️  Backend not responding. Make sure backend is running on port 8000');
      console.warn('   Start backend with: cd backend && uvicorn app.main:app --reload');
    } else {
      console.log('✅ Backend is running');
    }
    
    // 2. Ensure test users exist (create if needed via API)
    console.log('👥 Ensuring test users exist...');
    try {
      // First, login as admin to create test users
      const adminLogin = await apiContext.post('/api/v1/auth/login', {
        data: new URLSearchParams({
          username: 'admin@sofka.edu.co',
          password: 'admin123'
        }),
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      
      let adminHeaders = null;
      if (adminLogin.ok()) {
        const { access_token } = await adminLogin.json();
        adminHeaders = {
          'Authorization': `Bearer ${access_token}`,
          'Content-Type': 'application/json'
        };
        
        // Test users to create (matching UserCreate schema)
        const testUsers = [
          {
            email: 'juan@mail.com',
            password: 'juan123',
            role: 'Profesor',  // Must match UserRole enum value
            nombre: 'Juan',
            apellido: 'Pérez',
            fecha_nacimiento: '1985-05-15',
            area_ensenanza: 'Matemáticas',
            numero_contacto: '3001234567'
          },
          {
            email: 'sara@mail.com',
            password: 'sara123',
            role: 'Estudiante',  // Must match UserRole enum value
            nombre: 'Sara',
            apellido: 'García',
            fecha_nacimiento: '2000-03-20',
            programa_academico: 'Ingeniería de Sistemas',
            ciudad_residencia: 'Bogotá',
            numero_contacto: '3001234567'
          }
        ];
        
        // Get all users to check if test users exist
        const usersResponse = await apiContext.get('/api/v1/users', {
          headers: adminHeaders
        }).catch(() => null);
        
        if (usersResponse && usersResponse.ok()) {
          const existingUsers = await usersResponse.json();
          const existingEmails = new Set(existingUsers.map(u => u.email));
          
          // Create test users that don't exist
          for (const userData of testUsers) {
            if (existingEmails.has(userData.email)) {
              console.log(`   ✓ User ${userData.email} already exists`);
            } else {
              try {
                const createResponse = await apiContext.post('/api/v1/users', {
                  data: userData,
                  headers: adminHeaders
                });
                
                if (createResponse.ok()) {
                  console.log(`   ✓ Created test user: ${userData.email} (${userData.role})`);
                } else {
                  const errorBody = await createResponse.text().catch(() => 'Unknown error');
                  console.warn(`   ⚠️  Failed to create ${userData.email}: ${createResponse.status()} - ${errorBody}`);
                }
              } catch (error) {
                console.warn(`   ⚠️  Error creating ${userData.email}:`, error.message);
              }
            }
          }
        } else {
          console.warn('   ⚠️  Could not fetch users list. Test users may need to be created manually.');
        }
      } else {
        console.warn('   ⚠️  Could not login as admin. Test users may need to be created manually.');
        console.warn('   Run: cd backend && python create_test_users.py');
      }
    } catch (error) {
      console.warn('⚠️  Could not verify/create test users:', error.message);
      console.warn('   Run: cd backend && python create_test_users.py');
    }
    
    // 3. Login as profesor to get auth token
    console.log('🔐 Authenticating...');
    const loginResponse = await apiContext.post('/api/v1/auth/login', {
      data: new URLSearchParams({
        username: 'juan@mail.com',
        password: 'juan123'
      }),
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
    
    if (!loginResponse.ok()) {
      console.warn('⚠️  Could not authenticate as juan@mail.com');
      console.warn('   Make sure test users exist. Run: cd backend && python create_test_users.py');
      console.warn('   Tests will handle their own auth.');
    } else {
      const { access_token } = await loginResponse.json();
      const profesorHeaders = {
        'Authorization': `Bearer ${access_token}`,
        'Content-Type': 'application/json'
      };
      
      // 3. Ensure test subject and enrollment exist for attendance tests
      console.log('📚 Ensuring test subject and enrollment exist...');
      try {
        // Re-login as admin to get admin token (needed for creating subjects/enrollments)
        const adminLoginAgain = await apiContext.post('/api/v1/auth/login', {
          data: new URLSearchParams({
            username: 'admin@sofka.edu.co',
            password: 'admin123'
          }),
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        });
        
        if (!adminLoginAgain.ok()) {
          console.warn('   ⚠️  Could not login as admin for subject/enrollment setup');
        } else {
          const { access_token: adminToken } = await adminLoginAgain.json();
          const adminHeadersForSetup = {
            'Authorization': `Bearer ${adminToken}`,
            'Content-Type': 'application/json'
          };
          
          // Get profesor and estudiante IDs
          const usersResponse = await apiContext.get('/api/v1/users', {
            headers: adminHeadersForSetup
          });
        
          if (usersResponse && usersResponse.ok()) {
          const allUsers = await usersResponse.json();
          const profesor = allUsers.find(u => u.email === 'juan@mail.com');
          const estudiante = allUsers.find(u => u.email === 'sara@mail.com');
          
          if (profesor && estudiante) {
            // Check if subject exists for this profesor
            const subjectsResponse = await apiContext.get('/api/v1/subjects', {
              headers: profesorHeaders
            });
            
            let testSubject = null;
            if (subjectsResponse && subjectsResponse.ok()) {
              const subjects = await subjectsResponse.json();
              // Find a subject assigned to this profesor
              testSubject = subjects.find(s => s.profesor_id === profesor.id);
            }
            
            // Create subject if it doesn't exist
            if (!testSubject) {
              const subjectData = {
                nombre: 'Cálculo Diferencial',
                codigo_institucional: 'CALC-001',
                numero_creditos: 4,
                horario: 'Lunes y Miércoles 08:00-10:00',
                descripcion: 'Materia de prueba para tests de asistencia',
                profesor_id: profesor.id
              };
              
              const createSubjectResponse = await apiContext.post('/api/v1/subjects', {
                data: subjectData,
                headers: adminHeadersForSetup
              });
              
              if (createSubjectResponse.ok()) {
                testSubject = await createSubjectResponse.json();
                console.log(`   ✓ Created test subject: ${testSubject.nombre} (ID: ${testSubject.id})`);
              } else {
                const errorBody = await createSubjectResponse.text().catch(() => 'Unknown error');
                console.warn(`   ⚠️  Failed to create subject: ${createSubjectResponse.status()} - ${errorBody}`);
              }
            } else {
              console.log(`   ✓ Test subject already exists: ${testSubject.nombre} (ID: ${testSubject.id})`);
            }
            
            // Create enrollment if subject exists
            if (testSubject) {
              // Check if enrollment already exists
              const enrollmentsResponse = await apiContext.get('/api/v1/enrollments', {
                headers: adminHeadersForSetup
              });
              
              let enrollmentExists = false;
              if (enrollmentsResponse && enrollmentsResponse.ok()) {
                const enrollments = await enrollmentsResponse.json();
                enrollmentExists = enrollments.some(
                  e => e.estudiante_id === estudiante.id && e.subject_id === testSubject.id
                );
              }
              
              if (!enrollmentExists) {
                const enrollmentData = {
                  estudiante_id: estudiante.id,
                  subject_id: testSubject.id
                };
                
                const createEnrollmentResponse = await apiContext.post('/api/v1/enrollments', {
                  data: enrollmentData,
                  headers: adminHeadersForSetup
                });
                
                if (createEnrollmentResponse.ok()) {
                  console.log(`   ✓ Created enrollment: estudiante ${estudiante.id} → subject ${testSubject.id}`);
                } else {
                  const errorBody = await createEnrollmentResponse.text().catch(() => 'Unknown error');
                  console.warn(`   ⚠️  Failed to create enrollment: ${createEnrollmentResponse.status()} - ${errorBody}`);
                }
              } else {
                console.log(`   ✓ Enrollment already exists: estudiante ${estudiante.id} → subject ${testSubject.id}`);
              }
            }
          } else {
            console.warn('   ⚠️  Could not find profesor or estudiante users. Skipping subject/enrollment setup.');
          }
          } else {
            console.warn('   ⚠️  Could not fetch users list for subject/enrollment setup.');
          }
        }
      } catch (error) {
        console.warn('⚠️  Could not setup test subject/enrollment:', error.message);
      }
      
      // 4. Clean up existing test sessions
      console.log('🧹 Cleaning up existing test data...');
      const sessionsResponse = await apiContext.get('/api/v1/attendance/sessions', {
        headers: profesorHeaders
      });
      
      if (sessionsResponse.ok()) {
        const sessions = await sessionsResponse.json();
        console.log(`   Found ${sessions.length} existing sessions`);
        
        // Delete all sessions
        let deleted = 0;
        for (const session of sessions) {
          const deleteResponse = await apiContext.delete(`/api/v1/attendance/sessions/${session.id}`, {
            headers: profesorHeaders
          }).catch(() => null);
          
          if (deleteResponse && (deleteResponse.ok() || deleteResponse.status() === 204)) {
            deleted++;
          }
        }
        
        console.log(`   Deleted ${deleted} sessions`);
      }
    }
    
    console.log('\n✅ Test environment ready!\n');
    
  } catch (error) {
    console.error('\n❌ Setup error:', error.message);
    console.log('⚠️  Tests will continue but may fail if environment is not ready\n');
  } finally {
    await apiContext.dispose();
  }
}
