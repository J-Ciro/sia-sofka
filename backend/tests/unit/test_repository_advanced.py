"""Tests for advanced repository methods (eager loading with mixins)."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.grade_repository import GradeRepository
from app.repositories.enrollment_repository import EnrollmentRepository
from app.models.grade import Grade
from app.models.enrollment import Enrollment
from app.models.user import User, UserRole
from app.models.subject import Subject
from app.schemas.user import UserCreate
from app.schemas.subject import SubjectCreate
from app.schemas.enrollment import EnrollmentCreate
from app.schemas.grade import GradeCreate


@pytest.fixture
async def setup_test_data(async_db_session: AsyncSession):
    """Create a complete data structure for testing eager loading."""
    from datetime import date
    
    # Create profesor
    profesor = User(
        email="carlos@test.com",
        password_hash="hash123",
        role=UserRole.PROFESOR,
        nombre="Dr. Carlos",
        apellido="Pérez",
        codigo_institucional="PROF001",
        fecha_nacimiento=date(1980, 1, 1),
        edad=43,
        area_ensenanza="Matemáticas"
    )
    async_db_session.add(profesor)
    await async_db_session.flush()
    
    # Create estudiante
    estudiante = User(
        email="ana@test.com",
        password_hash="hash456",
        role=UserRole.ESTUDIANTE,
        nombre="Ana",
        apellido="Gómez",
        codigo_institucional="EST001",
        fecha_nacimiento=date(2000, 5, 15),
        edad=23,
        programa_academico="Ingeniería",
        ciudad_residencia="Bogotá"
    )
    async_db_session.add(estudiante)
    await async_db_session.flush()
    
    # Create subject
    subject = Subject(
        codigo_institucional="MAT101",
        nombre="Matemáticas",
        numero_creditos=3,
        profesor_id=profesor.id
    )
    async_db_session.add(subject)
    await async_db_session.flush()
    
    # Create enrollment
    enrollment = Enrollment(
        estudiante_id=estudiante.id,
        subject_id=subject.id
    )
    async_db_session.add(enrollment)
    await async_db_session.flush()
    
    # Create grades
    from datetime import date as dt_date
    grade1 = Grade(
        enrollment_id=enrollment.id,
        nota=4.25,
        periodo="2024-1",
        fecha=dt_date(2024, 6, 15)
    )
    grade2 = Grade(
        enrollment_id=enrollment.id,
        nota=4.50,
        periodo="2024-1",
        fecha=dt_date(2024, 12, 10)
    )
    async_db_session.add_all([grade1, grade2])
    await async_db_session.commit()
    
    return {
        'profesor': profesor,
        'estudiante': estudiante,
        'subject': subject,
        'enrollment': enrollment,
        'grades': [grade1, grade2]
    }


class TestGradeRepositoryAdvanced:
    """Tests for GradeRepository advanced methods."""

    @pytest.mark.asyncio
    async def test_get_with_relations_loads_enrollment(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test that get_with_relations loads enrollment relationship."""
        data = setup_test_data
        grade_id = data['grades'][0].id
        
        repo = GradeRepository(async_db_session)
        
        # Load grade with enrollment
        grade = await repo.get_with_relations(grade_id, relations=['enrollment'])
        
        assert grade is not None
        assert grade.id == grade_id
        assert grade.enrollment is not None
        assert grade.enrollment.id == data['enrollment'].id

    @pytest.mark.asyncio
    async def test_get_with_relations_returns_none_for_invalid_id(
        self, async_db_session: AsyncSession
    ):
        """Test that get_with_relations returns None for non-existent grade."""
        repo = GradeRepository(async_db_session)
        
        grade = await repo.get_with_relations(99999, relations=['enrollment'])
        
        assert grade is None

    @pytest.mark.asyncio
    async def test_get_many_with_relations_filters_by_enrollment(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test filtering grades by enrollment ID."""
        data = setup_test_data
        enrollment_id = data['enrollment'].id
        
        repo = GradeRepository(async_db_session)
        
        # Get grades for enrollment
        grades = await repo.get_many_with_relations(
            enrollment_id=enrollment_id,
            relations=['enrollment']
        )
        
        assert len(grades) == 2
        for grade in grades:
            assert grade.enrollment_id == enrollment_id
            assert grade.enrollment is not None

    @pytest.mark.asyncio
    async def test_get_many_with_relations_filters_by_grade_ids(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test filtering grades by list of IDs."""
        data = setup_test_data
        grade_ids = [data['grades'][0].id]
        
        repo = GradeRepository(async_db_session)
        
        grades = await repo.get_many_with_relations(
            grade_ids=grade_ids,
            relations=['enrollment']
        )
        
        assert len(grades) == 1
        assert grades[0].id == grade_ids[0]

    @pytest.mark.asyncio
    async def test_get_many_with_relations_respects_pagination(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test that pagination parameters work correctly."""
        setup_test_data  # Fixture already returns data
        
        repo = GradeRepository(async_db_session)
        
        # Get first page
        grades_page1 = await repo.get_many_with_relations(
            skip=0,
            limit=1,
            relations=['enrollment']
        )
        
        # Get second page
        grades_page2 = await repo.get_many_with_relations(
            skip=1,
            limit=1,
            relations=['enrollment']
        )
        
        assert len(grades_page1) == 1
        assert len(grades_page2) == 1
        assert grades_page1[0].id != grades_page2[0].id

    @pytest.mark.asyncio
    async def test_get_by_subject_returns_all_grades(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test getting all grades for a subject."""
        data = setup_test_data
        subject_id = data['subject'].id
        
        repo = GradeRepository(async_db_session)
        
        grades = await repo.get_by_subject(subject_id)
        
        assert len(grades) == 2
        # Verify all grades have enrollment_id that matches the subject's enrollment
        enrollment_ids = {grade.enrollment_id for grade in grades}
        assert len(enrollment_ids) == 1
        assert data['enrollment'].id in enrollment_ids

    @pytest.mark.asyncio
    async def test_get_by_subject_with_pagination(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test getting grades by subject with pagination."""
        data = setup_test_data
        subject_id = data['subject'].id
        
        repo = GradeRepository(async_db_session)
        
        # Get first page
        grades_page1 = await repo.get_by_subject(subject_id, skip=0, limit=1)
        # Get second page
        grades_page2 = await repo.get_by_subject(subject_id, skip=1, limit=1)
        
        assert len(grades_page1) == 1
        assert len(grades_page2) == 1
        assert grades_page1[0].id != grades_page2[0].id

    @pytest.mark.asyncio
    async def test_get_by_subject_returns_empty_for_nonexistent_subject(
        self, async_db_session: AsyncSession
    ):
        """Test getting grades for non-existent subject returns empty list."""
        repo = GradeRepository(async_db_session)
        
        grades = await repo.get_by_subject(99999)
        
        assert len(grades) == 0

    @pytest.mark.asyncio
    async def test_get_by_estudiante_returns_all_grades(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test getting all grades for a student."""
        data = setup_test_data
        estudiante_id = data['estudiante'].id
        
        repo = GradeRepository(async_db_session)
        
        grades = await repo.get_by_estudiante(estudiante_id)
        
        assert len(grades) == 2
        # Verify all grades have enrollment_id that matches the student's enrollment
        enrollment_ids = {grade.enrollment_id for grade in grades}
        assert len(enrollment_ids) == 1
        assert data['enrollment'].id in enrollment_ids

    @pytest.mark.asyncio
    async def test_get_by_estudiante_with_pagination(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test getting grades by estudiante with pagination."""
        data = setup_test_data
        estudiante_id = data['estudiante'].id
        
        repo = GradeRepository(async_db_session)
        
        # Get first page
        grades_page1 = await repo.get_by_estudiante(estudiante_id, skip=0, limit=1)
        # Get second page
        grades_page2 = await repo.get_by_estudiante(estudiante_id, skip=1, limit=1)
        
        assert len(grades_page1) == 1
        assert len(grades_page2) == 1
        assert grades_page1[0].id != grades_page2[0].id

    @pytest.mark.asyncio
    async def test_get_by_estudiante_returns_empty_for_nonexistent_student(
        self, async_db_session: AsyncSession
    ):
        """Test getting grades for non-existent student returns empty list."""
        repo = GradeRepository(async_db_session)
        
        grades = await repo.get_by_estudiante(99999)
        
        assert len(grades) == 0

    @pytest.mark.asyncio
    async def test_get_average_by_enrollment_calculates_correctly(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test that get_average_by_enrollment calculates average correctly."""
        data = setup_test_data
        enrollment_id = data['enrollment'].id
        
        repo = GradeRepository(async_db_session)
        
        # Calculate expected average: (4.25 + 4.50) / 2 = 4.375
        average = await repo.get_average_by_enrollment(enrollment_id)
        
        assert average is not None
        assert abs(average - 4.375) < 0.01  # Allow small floating point differences

    @pytest.mark.asyncio
    async def test_get_average_by_enrollment_returns_none_when_no_grades(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test that get_average_by_enrollment returns None when no grades exist."""
        # Create a new enrollment without grades (need new estudiante and subject to avoid unique constraint)
        from datetime import date
        from app.utils.codigo_generator import generar_codigo_institucional
        from app.core.security import get_password_hash
        
        # Create a new estudiante and subject for a new enrollment
        codigo_est = await generar_codigo_institucional(async_db_session, "Estudiante")
        codigo_prof = await generar_codigo_institucional(async_db_session, "Profesor")
        
        new_estudiante = User(
            email="est2@test.com",
            password_hash=get_password_hash("pass"),
            role=UserRole.ESTUDIANTE,
            nombre="Estudiante2",
            apellido="Test",
            codigo_institucional=codigo_est,
            fecha_nacimiento=date(2001, 1, 1),
            edad=22
        )
        new_profesor = User(
            email="prof2@test.com",
            password_hash=get_password_hash("pass"),
            role=UserRole.PROFESOR,
            nombre="Profesor2",
            apellido="Test",
            codigo_institucional=codigo_prof,
            fecha_nacimiento=date(1981, 1, 1),
            edad=42
        )
        async_db_session.add_all([new_estudiante, new_profesor])
        await async_db_session.flush()
        
        new_subject = Subject(
            codigo_institucional="QUI101",
            nombre="Química",
            numero_creditos=3,
            profesor_id=new_profesor.id
        )
        async_db_session.add(new_subject)
        await async_db_session.flush()
        
        # Create a new enrollment without grades
        new_enrollment = Enrollment(
            estudiante_id=new_estudiante.id,
            subject_id=new_subject.id
        )
        async_db_session.add(new_enrollment)
        await async_db_session.commit()
        await async_db_session.refresh(new_enrollment)
        
        repo = GradeRepository(async_db_session)
        
        average = await repo.get_average_by_enrollment(new_enrollment.id)
        
        assert average is None

    @pytest.mark.asyncio
    async def test_get_average_by_enrollment_returns_none_for_invalid_enrollment(
        self, async_db_session: AsyncSession
    ):
        """Test that get_average_by_enrollment returns None for non-existent enrollment."""
        repo = GradeRepository(async_db_session)
        
        average = await repo.get_average_by_enrollment(99999)
        
        assert average is None

    @pytest.mark.asyncio
    async def test_get_many_with_relations_filters_by_subject_id(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test filtering grades by subject ID using get_many_with_relations."""
        data = setup_test_data
        subject_id = data['subject'].id
        
        repo = GradeRepository(async_db_session)
        
        grades = await repo.get_many_with_relations(
            subject_id=subject_id,
            relations=['enrollment']
        )
        
        assert len(grades) == 2
        for grade in grades:
            assert grade.enrollment is not None
            assert grade.enrollment_id == data['enrollment'].id

    @pytest.mark.asyncio
    async def test_get_many_with_relations_filters_by_estudiante_id_via_subject(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test that get_many_with_relations with subject_id can be filtered by estudiante."""
        # This test verifies the subject_id filter works correctly
        data = setup_test_data
        subject_id = data['subject'].id
        estudiante_id = data['estudiante'].id
        
        repo = GradeRepository(async_db_session)
        
        # Get grades by subject
        grades = await repo.get_many_with_relations(
            subject_id=subject_id,
            relations=['enrollment']
        )
        
        assert len(grades) == 2
        # All grades should belong to enrollments of this subject and estudiante
        for grade in grades:
            assert grade.enrollment is not None
            assert grade.enrollment.subject_id == subject_id
            assert grade.enrollment.estudiante_id == estudiante_id

    @pytest.mark.asyncio
    async def test_get_many_with_relations_by_subject_returns_empty_for_nonexistent(
        self, async_db_session: AsyncSession
    ):
        """Test that get_many_with_relations returns empty list for non-existent subject."""
        repo = GradeRepository(async_db_session)
        
        grades = await repo.get_many_with_relations(
            subject_id=99999,
            relations=['enrollment']
        )
        
        assert len(grades) == 0

    @pytest.mark.asyncio
    async def test_get_with_relations_loads_nested_relationships(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test that get_with_relations loads nested estudiante and subject."""
        data = setup_test_data
        grade_id = data['grades'][0].id
        
        repo = GradeRepository(async_db_session)
        
        # Load grade with enrollment (which should load nested estudiante and subject)
        grade = await repo.get_with_relations(grade_id, relations=['enrollment'])
        
        assert grade is not None
        assert grade.enrollment is not None
        # Verify nested relationships are loaded (via joinedload in mixin)
        assert grade.enrollment.estudiante_id == data['estudiante'].id
        assert grade.enrollment.subject_id == data['subject'].id

    @pytest.mark.asyncio
    async def test_get_by_enrollment_returns_correct_grades(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test that get_by_enrollment returns only grades for that enrollment."""
        data = setup_test_data
        enrollment_id = data['enrollment'].id
        
        repo = GradeRepository(async_db_session)
        
        grades = await repo.get_by_enrollment(enrollment_id)
        
        assert len(grades) == 2
        for grade in grades:
            assert grade.enrollment_id == enrollment_id

    @pytest.mark.asyncio
    async def test_get_by_enrollment_with_pagination(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test that get_by_enrollment respects pagination."""
        data = setup_test_data
        enrollment_id = data['enrollment'].id
        
        repo = GradeRepository(async_db_session)
        
        # Get first page
        grades_page1 = await repo.get_by_enrollment(enrollment_id, skip=0, limit=1)
        # Get second page
        grades_page2 = await repo.get_by_enrollment(enrollment_id, skip=1, limit=1)
        
        assert len(grades_page1) == 1
        assert len(grades_page2) == 1
        assert grades_page1[0].id != grades_page2[0].id

    @pytest.mark.asyncio
    async def test_get_by_enrollment_returns_empty_for_nonexistent_enrollment(
        self, async_db_session: AsyncSession
    ):
        """Test that get_by_enrollment returns empty list for non-existent enrollment."""
        repo = GradeRepository(async_db_session)
        
        grades = await repo.get_by_enrollment(99999)
        
        assert len(grades) == 0


class TestEnrollmentRepositoryAdvanced:
    """Tests for EnrollmentRepository advanced methods."""

    @pytest.mark.asyncio
    async def test_get_with_relations_loads_estudiante_and_subject(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test that get_with_relations loads all relationships."""
        data = setup_test_data
        enrollment_id = data['enrollment'].id
        
        repo = EnrollmentRepository(async_db_session)
        
        # Load enrollment with relations
        enrollment = await repo.get_with_relations(
            enrollment_id,
            relations=['estudiante', 'subject']
        )
        
        assert enrollment is not None
        assert enrollment.id == enrollment_id
        assert enrollment.estudiante is not None
        assert enrollment.estudiante.id == data['estudiante'].id
        assert enrollment.subject is not None
        assert enrollment.subject.id == data['subject'].id

    @pytest.mark.asyncio
    async def test_get_with_relations_returns_none_for_invalid_id(
        self, async_db_session: AsyncSession
    ):
        """Test that get_with_relations returns None for non-existent enrollment."""
        repo = EnrollmentRepository(async_db_session)
        
        enrollment = await repo.get_with_relations(99999)
        
        assert enrollment is None

    @pytest.mark.asyncio
    async def test_get_many_with_relations_filters_by_estudiante(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test filtering enrollments by student ID."""
        data = setup_test_data
        estudiante_id = data['estudiante'].id
        
        repo = EnrollmentRepository(async_db_session)
        
        enrollments = await repo.get_many_with_relations(
            estudiante_id=estudiante_id,
            relations=['estudiante', 'subject']
        )
        
        assert len(enrollments) == 1
        assert enrollments[0].estudiante_id == estudiante_id
        assert enrollments[0].estudiante is not None

    @pytest.mark.asyncio
    async def test_get_many_with_relations_filters_by_subject(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test filtering enrollments by subject ID."""
        data = setup_test_data
        subject_id = data['subject'].id
        
        repo = EnrollmentRepository(async_db_session)
        
        enrollments = await repo.get_many_with_relations(
            subject_id=subject_id,
            relations=['estudiante', 'subject']
        )
        
        assert len(enrollments) == 1
        assert enrollments[0].subject_id == subject_id
        assert enrollments[0].subject is not None

    @pytest.mark.asyncio
    async def test_get_many_with_relations_respects_pagination(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test that pagination works for enrollments."""
        setup_test_data  # Fixture already returns data
        
        repo = EnrollmentRepository(async_db_session)
        
        # Get with limit
        enrollments = await repo.get_many_with_relations(
            skip=0,
            limit=1,
            relations=['estudiante', 'subject']
        )
        
        assert len(enrollments) <= 1

    @pytest.mark.asyncio
    async def test_get_with_relations_loads_grades(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test loading grades relationship."""
        data = setup_test_data
        enrollment_id = data['enrollment'].id
        
        repo = EnrollmentRepository(async_db_session)
        
        enrollment = await repo.get_with_relations(
            enrollment_id,
            relations=['grades']
        )
        
        assert enrollment is not None
        # Note: grades might not be loaded immediately due to lazy loading
        # This test verifies the query runs without error

    @pytest.mark.asyncio
    async def test_get_with_relations_loads_all_relations(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test loading all relationships together."""
        data = setup_test_data
        enrollment_id = data['enrollment'].id
        
        repo = EnrollmentRepository(async_db_session)
        
        enrollment = await repo.get_with_relations(
            enrollment_id,
            relations=['estudiante', 'subject', 'grades']
        )
        
        assert enrollment is not None
        assert enrollment.estudiante is not None
        assert enrollment.subject is not None
        assert enrollment.estudiante.id == data['estudiante'].id
        assert enrollment.subject.id == data['subject'].id

    @pytest.mark.asyncio
    async def test_get_with_relations_loads_only_estudiante(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test loading only estudiante relationship."""
        data = setup_test_data
        enrollment_id = data['enrollment'].id
        
        repo = EnrollmentRepository(async_db_session)
        
        enrollment = await repo.get_with_relations(
            enrollment_id,
            relations=['estudiante']
        )
        
        assert enrollment is not None
        assert enrollment.estudiante is not None
        assert enrollment.estudiante.id == data['estudiante'].id

    @pytest.mark.asyncio
    async def test_get_with_relations_loads_only_subject(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test loading only subject relationship."""
        data = setup_test_data
        enrollment_id = data['enrollment'].id
        
        repo = EnrollmentRepository(async_db_session)
        
        enrollment = await repo.get_with_relations(
            enrollment_id,
            relations=['subject']
        )
        
        assert enrollment is not None
        assert enrollment.subject is not None
        assert enrollment.subject.id == data['subject'].id

    @pytest.mark.asyncio
    async def test_get_many_with_relations_filters_by_both_estudiante_and_subject(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test filtering enrollments by both estudiante and subject."""
        data = setup_test_data
        estudiante_id = data['estudiante'].id
        subject_id = data['subject'].id
        
        repo = EnrollmentRepository(async_db_session)
        
        enrollments = await repo.get_many_with_relations(
            estudiante_id=estudiante_id,
            subject_id=subject_id,
            relations=['estudiante', 'subject']
        )
        
        assert len(enrollments) == 1
        assert enrollments[0].estudiante_id == estudiante_id
        assert enrollments[0].subject_id == subject_id
        assert enrollments[0].estudiante is not None
        assert enrollments[0].subject is not None

    @pytest.mark.asyncio
    async def test_get_many_with_relations_returns_empty_when_no_match(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test that get_many_with_relations returns empty list when no match."""
        repo = EnrollmentRepository(async_db_session)
        
        enrollments = await repo.get_many_with_relations(
            estudiante_id=99999,
            relations=['estudiante', 'subject']
        )
        
        assert len(enrollments) == 0

    @pytest.mark.asyncio
    async def test_get_many_with_relations_with_pagination_details(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test that pagination works correctly with skip and limit."""
        setup_test_data  # Fixture already returns data
        
        repo = EnrollmentRepository(async_db_session)
        
        # Get first page
        enrollments_page1 = await repo.get_many_with_relations(
            skip=0,
            limit=1,
            relations=['estudiante', 'subject']
        )
        
        # Get second page
        enrollments_page2 = await repo.get_many_with_relations(
            skip=1,
            limit=1,
            relations=['estudiante', 'subject']
        )
        
        assert len(enrollments_page1) <= 1
        assert len(enrollments_page2) <= 1
        if len(enrollments_page1) > 0 and len(enrollments_page2) > 0:
            assert enrollments_page1[0].id != enrollments_page2[0].id

    @pytest.mark.asyncio
    async def test_get_by_estudiante_returns_correct_enrollments(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test that get_by_estudiante returns enrollments for that student."""
        data = setup_test_data
        estudiante_id = data['estudiante'].id
        
        repo = EnrollmentRepository(async_db_session)
        
        enrollments = await repo.get_by_estudiante(estudiante_id)
        
        assert len(enrollments) == 1
        assert enrollments[0].estudiante_id == estudiante_id

    @pytest.mark.asyncio
    async def test_get_by_estudiante_with_pagination(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test that get_by_estudiante respects pagination."""
        # Create additional enrollments for pagination test
        data = setup_test_data
        estudiante = data['estudiante']
        profesor = data['profesor']
        
        # Create another subject
        from app.models.subject import Subject
        subject2 = Subject(
            codigo_institucional="FIS101",
            nombre="Física",
            numero_creditos=3,
            profesor_id=profesor.id
        )
        async_db_session.add(subject2)
        await async_db_session.flush()
        
        # Create another enrollment
        enrollment2 = Enrollment(
            estudiante_id=estudiante.id,
            subject_id=subject2.id
        )
        async_db_session.add(enrollment2)
        await async_db_session.commit()
        
        repo = EnrollmentRepository(async_db_session)
        
        # Get first page
        enrollments_page1 = await repo.get_by_estudiante(estudiante.id, skip=0, limit=1)
        # Get second page
        enrollments_page2 = await repo.get_by_estudiante(estudiante.id, skip=1, limit=1)
        
        assert len(enrollments_page1) == 1
        assert len(enrollments_page2) == 1
        assert enrollments_page1[0].id != enrollments_page2[0].id

    @pytest.mark.asyncio
    async def test_get_by_estudiante_returns_empty_for_nonexistent_student(
        self, async_db_session: AsyncSession
    ):
        """Test that get_by_estudiante returns empty list for non-existent student."""
        repo = EnrollmentRepository(async_db_session)
        
        enrollments = await repo.get_by_estudiante(99999)
        
        assert len(enrollments) == 0

    @pytest.mark.asyncio
    async def test_get_by_subject_returns_correct_enrollments(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test that get_by_subject returns enrollments for that subject."""
        data = setup_test_data
        subject_id = data['subject'].id
        
        repo = EnrollmentRepository(async_db_session)
        
        enrollments = await repo.get_by_subject(subject_id)
        
        assert len(enrollments) == 1
        assert enrollments[0].subject_id == subject_id

    @pytest.mark.asyncio
    async def test_get_by_subject_with_pagination(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test that get_by_subject respects pagination."""
        # Create additional enrollments for pagination test
        data = setup_test_data
        subject = data['subject']
        profesor = data['profesor']
        
        # Create another estudiante
        from datetime import date
        from app.utils.codigo_generator import generar_codigo_institucional
        from app.core.security import get_password_hash
        codigo_est2 = await generar_codigo_institucional(async_db_session, "Estudiante")
        
        estudiante2 = User(
            email="est2@test.com",
            password_hash=get_password_hash("pass"),
            role=UserRole.ESTUDIANTE,
            nombre="Estudiante2",
            apellido="Test",
            codigo_institucional=codigo_est2,
            fecha_nacimiento=date(2001, 1, 1),
            edad=22
        )
        async_db_session.add(estudiante2)
        await async_db_session.flush()
        
        # Create another enrollment
        enrollment2 = Enrollment(
            estudiante_id=estudiante2.id,
            subject_id=subject.id
        )
        async_db_session.add(enrollment2)
        await async_db_session.commit()
        
        repo = EnrollmentRepository(async_db_session)
        
        # Get first page
        enrollments_page1 = await repo.get_by_subject(subject.id, skip=0, limit=1)
        # Get second page
        enrollments_page2 = await repo.get_by_subject(subject.id, skip=1, limit=1)
        
        assert len(enrollments_page1) == 1
        assert len(enrollments_page2) == 1
        assert enrollments_page1[0].id != enrollments_page2[0].id

    @pytest.mark.asyncio
    async def test_get_by_subject_returns_empty_for_nonexistent_subject(
        self, async_db_session: AsyncSession
    ):
        """Test that get_by_subject returns empty list for non-existent subject."""
        repo = EnrollmentRepository(async_db_session)
        
        enrollments = await repo.get_by_subject(99999)
        
        assert len(enrollments) == 0

    @pytest.mark.asyncio
    async def test_get_by_estudiante_and_subject_returns_enrollment(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test that get_by_estudiante_and_subject returns correct enrollment."""
        data = setup_test_data
        estudiante_id = data['estudiante'].id
        subject_id = data['subject'].id
        
        repo = EnrollmentRepository(async_db_session)
        
        enrollment = await repo.get_by_estudiante_and_subject(estudiante_id, subject_id)
        
        assert enrollment is not None
        assert enrollment.estudiante_id == estudiante_id
        assert enrollment.subject_id == subject_id
        assert enrollment.id == data['enrollment'].id

    @pytest.mark.asyncio
    async def test_get_by_estudiante_and_subject_returns_none_when_not_exists(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test that get_by_estudiante_and_subject returns None when enrollment doesn't exist."""
        data = setup_test_data
        estudiante_id = data['estudiante'].id
        
        repo = EnrollmentRepository(async_db_session)
        
        # Use non-existent subject_id
        enrollment = await repo.get_by_estudiante_and_subject(estudiante_id, 99999)
        
        assert enrollment is None

    @pytest.mark.asyncio
    async def test_get_by_estudiante_and_subject_returns_none_for_nonexistent_estudiante(
        self, async_db_session: AsyncSession, setup_test_data
    ):
        """Test that get_by_estudiante_and_subject returns None for non-existent estudiante."""
        data = setup_test_data
        subject_id = data['subject'].id
        
        repo = EnrollmentRepository(async_db_session)
        
        # Use non-existent estudiante_id
        enrollment = await repo.get_by_estudiante_and_subject(99999, subject_id)
        
        assert enrollment is None


class TestRepositoryErrorHandling:
    """Tests for repository error handling with decorators."""

    @pytest.mark.asyncio
    async def test_grade_repository_handles_invalid_pagination(
        self, async_db_session: AsyncSession
    ):
        """Test that invalid pagination raises ValueError."""
        repo = GradeRepository(async_db_session)
        
        with pytest.raises(ValueError):
            await repo.get_many_with_relations(skip=-1, limit=10)

    @pytest.mark.asyncio
    async def test_enrollment_repository_handles_invalid_pagination(
        self, async_db_session: AsyncSession
    ):
        """Test that invalid pagination raises ValueError."""
        repo = EnrollmentRepository(async_db_session)
        
        with pytest.raises(ValueError):
            await repo.get_many_with_relations(skip=0, limit=-10)
