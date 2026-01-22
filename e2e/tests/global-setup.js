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
    
    // 2. Login as profesor to get auth token
    console.log('🔐 Authenticating...');
    const loginResponse = await apiContext.post('/api/v1/auth/login', {
      data: {
        email: 'juan@mail.com',
        password: 'juan123'
      }
    });
    
    if (!loginResponse.ok()) {
      console.warn('⚠️  Could not authenticate. Tests will handle their own auth.');
    } else {
      const { access_token } = await loginResponse.json();
      
      // 3. Clean up existing test sessions
      console.log('🧹 Cleaning up existing test data...');
      const sessionsResponse = await apiContext.get('/api/v1/attendance/sessions', {
        headers: {
          'Authorization': `Bearer ${access_token}`
        }
      });
      
      if (sessionsResponse.ok()) {
        const sessions = await sessionsResponse.json();
        console.log(`   Found ${sessions.length} existing sessions`);
        
        // Delete all sessions
        let deleted = 0;
        for (const session of sessions) {
          const deleteResponse = await apiContext.delete(`/api/v1/attendance/sessions/${session.id}`, {
            headers: {
              'Authorization': `Bearer ${access_token}`
            }
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
