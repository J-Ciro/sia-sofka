# 🎭 E2E Tests - SIA SOFKA U

End-to-End testing suite for the SIA SOFKA U academic management system using Playwright and JavaScript.

![Playwright](https://img.shields.io/badge/Playwright-1.40+-green.svg)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-yellow.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running Tests](#running-tests)
- [Test Structure](#test-structure)
- [Page Object Models](#page-object-models)
- [Test Data](#test-data)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## 🎯 Overview

This E2E testing suite validates the complete user workflows of the SIA SOFKA U application, including:

- **HU-01**: Create Attendance Session (3 scenarios)
- **HU-02**: Mark Attendance with Massive Buttons (3 scenarios)
- **HU-03**: Change Individual Student Status (3 scenarios)
- **HU-04**: Save Attendance with Validation (2 scenarios)
- **Edge Cases**: Error handling and validation (2 scenarios)

### Key Features

✅ **Page Object Model** pattern for maintainability  
✅ **Role-based locators** for accessibility  
✅ **Auto-retrying assertions** for stability  
✅ **Fixtures** for automatic setup/teardown  
✅ **Comprehensive reporting** (HTML, JSON)  
✅ **Database cleanup** between tests  

## 🏗️ Architecture

```
e2e/
├── tests/
│   ├── fixtures/              # Test fixtures
│   │   ├── auth.js           # Authentication & login
│   │   └── database.js       # Database cleanup
│   ├── pages/                # Page Object Models
│   │   └── AttendancePage.js # Attendance page POM
│   ├── helpers/              # Utility functions
│   │   └── dateHelpers.js    # Date/time utilities
│   ├── e2e/                  # Test specifications
│   │   └── attendance.spec.js
│   ├── global-setup.js       # Global setup (runs once)
│   └── global-teardown.js    # Global teardown
├── playwright.config.js      # Playwright configuration
├── package.json             # Dependencies & scripts
└── README.md               # This file
```

## 📦 Prerequisites

- **Node.js**: v18.0.0 or higher
- **npm**: v9.0.0 or higher
- **Running Services**:
  - Frontend: `http://localhost:3000`
  - Backend: `http://localhost:8000`
  - PostgreSQL: `localhost:5432`

## 🚀 Installation

### 1. Install Dependencies

```bash
cd e2e
npm install
```

### 2. Install Playwright Browsers

```bash
npx playwright install
```

Or install only Chromium for faster setup:

```bash
npx playwright install chromium
```

### 3. Verify Services are Running

```bash
# Backend (Terminal 1)
cd backend
uvicorn app.main:app --reload

# Frontend (Terminal 2)
cd frontend
npm run dev
```

## 🧪 Running Tests

### Run All Tests (Headless)

```bash
npm run test:e2e
```

### Run Tests in UI Mode (Recommended for Development)

```bash
npm run test:e2e:ui
```

### Run Tests in Headed Mode (Watch Browser)

```bash
npm run test:e2e:headed
```

### Run Specific Test File

```bash
npx playwright test tests/e2e/attendance.spec.js
```

### Debug Mode

```bash
npm run test:e2e:debug
```

### Generate Code (Codegen)

```bash
npm run codegen
```

## 📊 View Test Reports

After running tests, view the HTML report:

```bash
npm run test:e2e:report
```

Reports are generated in:
- **HTML**: `playwright-report/index.html`
- **JSON**: `playwright-results.json`

## 📝 Test Structure

### Test Organization

Tests follow the **Given-When-Then** pattern:

```javascript
test('should create attendance session successfully', async ({ profesorPage }) => {
  // Given: I am on the attendance page
  const attendancePage = new AttendancePage(profesorPage);
  await attendancePage.goto();
  await attendancePage.verifyPageLoaded();
  
  // When: I create a new session
  const timeSlot = getTestTimeSlot(1);
  await attendancePage.createSession({
    date: getTestDate(1),
    startTime: timeSlot.startTime,
    endTime: timeSlot.endTime,
    description: 'Test Session'
  });
  
  // Then: Session should be created successfully
  await attendancePage.verifySessionCreated();
});
```

### Test Categories

1. **Happy Path Tests**: Successful user workflows
2. **Validation Tests**: Form validation and error handling
3. **Edge Cases**: Boundary conditions and error scenarios

## 🎭 Page Object Models

### AttendancePage

Handles all attendance page interactions:

```javascript
import { AttendancePage } from '../pages/AttendancePage.js';

const attendancePage = new AttendancePage(page);

// Navigation
await attendancePage.goto();
await attendancePage.verifyPageLoaded();

// Create session
await attendancePage.createSession({
  date: '2026-01-20',
  startTime: '08:00',
  endTime: '09:00',
  description: 'Test Session'
});

// Mark attendance
await attendancePage.markAllStudents('present');
await attendancePage.changeStudentStatus(0);

// Search
await attendancePage.searchStudents('Sara');

// Save
await attendancePage.saveAttendance();

// Get statistics
const stats = await attendancePage.getStatistics();
```

## 📊 Test Data

### Using Helpers

```javascript
import { getTestDate, getTestTimeSlot, getFutureDate } from '../helpers/dateHelpers.js';

// Get unique date for test
const date = getTestDate(1); // Yesterday

// Get unique time slot
const timeSlot = getTestTimeSlot(1); // 08:00-09:00

// Get future date (for validation tests)
const futureDate = getFutureDate(1); // Tomorrow
```

### Using Test Data Builders

```javascript
import { testDataBuilder } from '../fixtures/auth.js';

const sessionData = testDataBuilder.session({
  descripcion: 'Custom description'
});

const userData = testDataBuilder.user({
  role: 'Profesor'
});
```

### Test Users

```javascript
import { TEST_USERS } from '../fixtures/auth.js';

// Available test users
TEST_USERS.admin      // admin@sofka.edu.co / admin123
TEST_USERS.profesor   // juan@mail.com / juan123
TEST_USERS.estudiante // sara@mail.com / sara123
```

## 🔧 Configuration

### Playwright Config (`playwright.config.js`)

Key configurations:

```javascript
{
  testDir: './tests/e2e',
  timeout: 30000,
  retries: process.env.CI ? 2 : 0,
  workers: 1, // Sequential execution for database isolation
  use: {
    baseURL: 'http://localhost:3000',
    apiURL: 'http://localhost:8000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure'
  }
}
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BASE_URL` | Frontend URL | `http://localhost:3000` |
| `API_URL` | Backend URL | `http://localhost:8000` |
| `CI` | CI environment flag | `false` |

## 🔍 Debugging

### Debug Failed Test

```bash
npx playwright test --debug tests/e2e/attendance.spec.js
```

### View Trace

```bash
npx playwright show-trace trace.zip
```

### Take Screenshot During Test

```javascript
await page.screenshot({ path: 'debug-screenshot.png' });
```

### Pause Test Execution

```javascript
await page.pause(); // Opens Playwright Inspector
```

## 🐛 Troubleshooting

### Services Not Starting

**Problem**: Frontend/Backend not responding

**Solution**:
```bash
# Verify services are running
curl http://localhost:3000
curl http://localhost:8000/api/v1/health

# Start services manually
cd backend && uvicorn app.main:app --reload
cd frontend && npm run dev
```

### Login Failures

**Problem**: "Error al iniciar sesión"

**Solution**:
- Verify user exists in database
- Check credentials in `tests/fixtures/auth.js`
- Run backend seed script: `python backend/create_admin.py`

### Browser Installation Issues

**Problem**: Playwright browsers not installed

**Solution**:
```bash
npx playwright install --with-deps chromium
```

### Timeout Errors

**Problem**: Tests timing out

**Solution**:
- Increase timeout in `playwright.config.js`
- Check if services are responsive
- Use `await page.waitForLoadState('networkidle')`

### Flaky Tests

**Problem**: Tests pass/fail inconsistently

**Solution**:
- Avoid hard-coded waits (`page.waitForTimeout`)
- Use Playwright's auto-waiting
- Add explicit wait conditions: `await expect(locator).toBeVisible()`
- Check for race conditions

### Database Conflicts

**Problem**: "Session already exists" errors

**Solution**:
- Global setup cleans database automatically
- Each test uses unique dates/times
- Fixtures clean database before each test

## 📚 Best Practices

1. **Use Page Objects**: Never interact directly with locators in tests
2. **Prefer Role-Based Locators**: `getByRole`, `getByLabel`, `getByText`
3. **Use data-testid**: For elements without semantic roles
4. **Write Descriptive Tests**: Use clear test names and comments
5. **Avoid Hard Waits**: Use `expect()` auto-retrying assertions
6. **Keep Tests Independent**: Each test should run in isolation
7. **Use Test Data Fixtures**: Centralize test data in fixtures
8. **Group Related Tests**: Use `test.describe()` blocks
9. **Follow Given-When-Then**: Structure tests clearly
10. **Clean Up After Tests**: Use fixtures for automatic cleanup

## 📖 INVEST Principles

Our tests follow INVEST principles:

- **Independent**: Each test uses unique data and cleans up
- **Negotiable**: Easy to modify via fixtures and helpers
- **Valuable**: Tests real user workflows
- **Estimable**: Predictable execution time (~30s per test)
- **Small**: One behavior per test
- **Testable**: Clear assertions and deterministic outcomes

## 📊 Scripts Available

```json
{
  "test:e2e": "playwright test",
  "test:e2e:ui": "playwright test --ui",
  "test:e2e:headed": "playwright test --headed",
  "test:e2e:debug": "playwright test --debug",
  "test:e2e:report": "playwright show-report",
  "codegen": "playwright codegen http://localhost:3000"
}
```

## ✅ Checklist Pre-Test

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] PostgreSQL database accessible
- [ ] Test users exist in database:
  - `juan@mail.com` (Profesor)
  - `sara@mail.com` (Estudiante)
- [ ] Subjects and enrollments seeded

## 🎯 Next Steps

1. Add more Page Objects for other pages (Users, Subjects, Grades)
2. Add API integration tests
3. Add accessibility tests
4. Configure CI/CD pipeline
5. Add visual regression testing

## 📄 License

MIT License - see [LICENSE](../LICENSE) for details

## 🔗 Related Documentation

- [User Stories](../HISTORIAS_USUARIO.md)
- [Architecture](../ARCHITECTURE.md)
- [Backend README](../backend/README.md)
- [Frontend README](../frontend/README.md)
- [Playwright Documentation](https://playwright.dev/)

## 🤝 Support

For issues or questions:

1. Check [Troubleshooting](#troubleshooting) section
2. Review [Playwright Docs](https://playwright.dev/docs/intro)
3. Open an issue in the repository

---

**Happy Testing! 🎭✨**
