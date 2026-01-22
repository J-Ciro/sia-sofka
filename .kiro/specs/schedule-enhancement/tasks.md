# Implementation Plan: Schedule System Enhancement

## Overview

This implementation plan extends the existing SIA SOFKA schedule system to fix the recurring schedule issue and add advanced calendar functionality. The plan builds upon the existing Python/FastAPI backend and React frontend, adding date-specific scheduling capabilities, month view, and drag-and-drop functionality while maintaining full backward compatibility.

## Tasks

- [x] 1. Database Schema Enhancement
  - Add `fecha_especifica` field to existing Schedule model
  - Create database migration using Alembic
  - Add new indexes for date-specific queries
  - Add constraints for data consistency
  - _Requirements: 2.1, 2.4, 2.5_

- [ ] 2. Backend Model and Schema Updates
  - [x] 2.1 Extend Schedule model in `backend/app/models/schedule.py`
    - Add `fecha_especifica` Date field with nullable=True
    - Add new unique constraint for date-specific schedules
    - Add new indexes for performance
    - _Requirements: 2.1, 2.4_
  
  - [ ]* 2.2 Write property test for Schedule model date consistency
    - **Property 2: Date and Day-of-Week Consistency**
    - **Validates: Requirements 1.4, 2.3, 2.4**
  
  - [x] 2.3 Extend ScheduleBase schema in `backend/app/schemas/schedule.py`
    - Add optional `fecha_especifica` field
    - Add validation for date-day consistency
    - Add computed field `es_fecha_especifica`
    - _Requirements: 1.4, 2.3, 2.4_
  
  - [ ]* 2.4 Write property test for schema validation
    - **Property 2: Date and Day-of-Week Consistency**
    - **Validates: Requirements 1.4, 2.3, 2.4**

- [ ] 3. Enhanced Repository Layer
  - [x] 3.1 Extend ScheduleRepository in `backend/app/repositories/schedule_repository.py`
    - Add `find_classroom_overlaps_by_date` method
    - Add `find_professor_overlaps_by_date` method
    - Add `get_schedules_by_date_range` method
    - _Requirements: 6.1, 6.2, 6.3, 7.2_
  
  - [ ]* 3.2 Write property test for date-specific conflict detection
    - **Property 4: Enhanced Conflict Detection for Date-Specific Schedules**
    - **Validates: Requirements 1.5, 6.1, 6.2, 6.3**
  
  - [ ]* 3.3 Write property test for date range queries
    - **Property 9: API Extension Compatibility**
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.5**

- [ ] 4. Enhanced Service Layer
  - [x] 4.1 Extend ScheduleService in `backend/app/services/schedule_service.py`
    - Enhance `validate_schedule_conflicts` to support date-specific schedules
    - Add `get_schedules_for_calendar` method for calendar display
    - Maintain backward compatibility with existing methods
    - _Requirements: 1.5, 6.1, 6.4, 7.1_
  
  - [ ]* 4.2 Write property test for enhanced conflict validation
    - **Property 4: Enhanced Conflict Detection for Date-Specific Schedules**
    - **Validates: Requirements 1.5, 6.1, 6.2, 6.3**
  
  - [ ]* 4.3 Write property test for backward compatibility
    - **Property 3: Backward Compatibility Preservation**
    - **Validates: Requirements 2.1, 2.2, 2.5**

- [ ] 5. API Endpoint Enhancements
  - [x] 5.1 Extend schedule endpoints in `backend/app/api/v1/endpoints/schedules.py`
    - Modify POST endpoint to accept `fecha_especifica`
    - Add GET endpoint for date range queries
    - Enhance existing endpoints to return date information
    - _Requirements: 7.1, 7.2, 7.3, 7.5_
  
  - [ ]* 5.2 Write integration tests for enhanced API endpoints
    - Test date-specific schedule creation
    - Test date range queries
    - Test backward compatibility
    - _Requirements: 7.1, 7.2, 7.3, 7.5_

- [x] 6. Checkpoint - Backend Enhancement Complete
  - Ensure all backend tests pass, ask the user if questions arise.

  - [ ]* 7.2 Write property test for view state preservation
    - **Property 5: Calendar View State Preservation**
    - **Validates: Requirements 4.2, 4.4, 4.5**

- [ ] 8. Enhanced Weekly Calendar Component
  - [x] 8.1 Extend WeeklyCalendar in `frontend/src/components/schedule/WeeklyCalendar.jsx`
    - Add drag-and-drop support using react-big-calendar
    - Enhance event transformation for date-specific schedules
    - Add visual indicators for date-specific vs recurring schedules
    - _Requirements: 5.2, 5.4, 5.5, 8.2, 8.4_
  
  - [ ]* 8.2 Write property test for drag-and-drop functionality
    - **Property 7: Drag-and-Drop Schedule Updates**
    - **Validates: Requirements 5.2, 5.4, 5.5**
  
  - [ ]* 8.3 Write property test for visual schedule distinction
    - **Property 11: Visual Schedule Distinction**
    - **Validates: Requirements 8.2, 8.4**


- [ ] 10. Enhanced Schedule Form Component
  - [x] 10.1 Extend ScheduleForm in `frontend/src/components/schedule/ScheduleForm.jsx`
    - Add date picker for specific date selection
    - Add toggle for date-specific vs recurring mode
    - Auto-calculate day-of-week from selected date
    - Enhance validation for date consistency
    - _Requirements: 8.1, 8.3, 8.5_
  
  - [ ]* 10.2 Write property test for form enhancement functionality
    - **Property 10: Form Enhancement Functionality**
    - **Validates: Requirements 8.1, 8.3, 8.5**

- [ ] 11. API Service Layer Updates
  - [x] 11.1 Extend scheduleService in `frontend/src/services/apiService.js`
    - Add methods for date range queries
    - Enhance existing methods to support date-specific data
    - Add drag-and-drop update methods
    - _Requirements: 7.1, 7.2, 7.3, 7.4_
  
  - [ ]* 11.2 Write property test for API service compatibility
    - **Property 9: API Extension Compatibility**
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.5**

- [ ] 12. Integration and Component Wiring
  - [x] 12.1 Update Horarios dashboard component
    - Replace WeeklyCalendar with CalendarContainer
    - Ensure existing functionality is preserved
    - _Requirements: 3.1, 4.1_
  
  - [x] 12.2 Update routing and navigation
    - Ensure calendar routes work with new components
    - Maintain existing navigation structure
    - _Requirements: 3.1_

- [ ] 13. Drag-and-Drop Validation Enhancement
  - [x] 13.1 Implement drag-and-drop validation logic
    - Add client-side validation for invalid drops
    - Integrate with existing conflict validation
    - Add error handling and user feedback
    - _Requirements: 5.3, 6.5_
  
  - [ ]* 13.2 Write property test for drag-and-drop validation
    - **Property 8: Drag-and-Drop Validation**
    - **Validates: Requirements 5.3, 6.5**

- [ ] 14. Date-Specific Schedule Creation Testing
  - [ ]* 14.1 Write property test for date-specific schedule behavior
    - **Property 1: Date-Specific Schedule Creation and Display**
    - **Validates: Requirements 1.1, 1.2, 1.3**

- [ ] 15. Final Integration Testing
  - [ ]* 15.1 Write end-to-end tests for complete workflow
    - Test creating date-specific schedule
    - Test month view navigation
    - Test drag-and-drop operations
    - Test view switching
    - _Requirements: All requirements_

- [x] 16. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Integration tests validate complete user workflows
- The implementation maintains full backward compatibility with existing functionality
- All new functionality extends rather than replaces existing features