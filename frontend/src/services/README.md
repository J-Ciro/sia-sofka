# Services Architecture

This directory contains the refactored API services following the Single Responsibility Principle. Each service is now responsible for a specific domain entity.

## Structure

```
services/
├── api.js                    # Base API configuration (axios instance)
├── index.js                  # Centralized exports for all services (MAIN ENTRY POINT)
├── authService.js           # Authentication operations
├── userService.js           # User management + bulk import/export
├── subjectService.js        # Subject management
├── enrollmentService.js     # Student enrollment operations
├── gradeService.js          # Grade management
├── reportService.js         # Report generation
├── profileService.js        # User profile operations
├── profesorService.js       # Professor-specific operations
├── estudianteService.js     # Student-specific operations
├── classroomService.js      # Classroom management
├── scheduleService.js       # Schedule management (enhanced for Task 11.1)
└── attendanceService.js     # Attendance management
```

## Usage

### Recommended (Current Standard)
Import specific services from the centralized index:

```javascript
import { userService, authService, gradeService } from '../services'

// Use the services
const users = await userService.getAll()
const currentUser = await authService.getCurrentUser()
const grades = await gradeService.getAll({ subject_id: 1 })
```

### Alternative (Direct Import)
Import specific services directly (useful for tree-shaking):

```javascript
import { userService } from '../services/userService'
import { authService } from '../services/authService'
import { gradeService } from '../services/gradeService'

// Use the services
const users = await userService.getAll()
const currentUser = await authService.getCurrentUser()
const grades = await gradeService.getAll({ subject_id: 1 })
```

## Migration Completed ✅

All imports have been migrated from the old `apiService.js` to use the centralized `index.js`. The old `apiService.js` file has been removed.

### What Changed
- ❌ `import { userService } from '../services/apiService'` (REMOVED)
- ✅ `import { userService } from '../services'` (CURRENT)

## Benefits

1. **Single Responsibility**: Each service handles one domain
2. **Better Organization**: Easier to find and maintain code
3. **Reduced Bundle Size**: Import only what you need
4. **Better Testing**: Easier to test individual services
5. **Clearer Dependencies**: Explicit imports show what each component uses
6. **Maintainability**: Changes to one service don't affect others
7. **Centralized Access**: Single entry point through index.js