"""Create attendance records for existing sessions that don't have them."""

import asyncio
from sqlalchemy import select
from app.core.database import get_db, get_engine
from app.models.attendance import ClaseSession, Attendance, AttendanceStatus
from app.models.enrollment import Enrollment
from app.models.base import Base


async def create_missing_attendances():
    """Create attendance records for sessions that don't have them."""
    # Initialize database
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Get database session
    async for db in get_db():
        try:
            # Get all sessions
            result = await db.execute(select(ClaseSession))
            sessions = result.scalars().all()
            
            print(f"Found {len(sessions)} sessions")
            
            for session in sessions:
                print(f"\nProcessing session {session.id} for subject {session.subject_id}")
                
                # Check if session already has attendance records
                existing_result = await db.execute(
                    select(Attendance).where(Attendance.clase_session_id == session.id)
                )
                existing_attendances = existing_result.scalars().all()
                
                if existing_attendances:
                    print(f"  - Already has {len(existing_attendances)} attendance records, skipping")
                    continue
                
                # Get all enrolled students for this subject
                enrollments_result = await db.execute(
                    select(Enrollment).where(Enrollment.subject_id == session.subject_id)
                )
                enrollments = enrollments_result.scalars().all()
                
                print(f"  - Found {len(enrollments)} enrolled students")
                
                # Create attendance records
                created_count = 0
                for enrollment in enrollments:
                    attendance = Attendance(
                        clase_session_id=session.id,
                        estudiante_id=enrollment.estudiante_id,
                        estado=AttendanceStatus.AUSENTE
                    )
                    db.add(attendance)
                    created_count += 1
                
                await db.commit()
                print(f"  - Created {created_count} attendance records")
            
            print("\n✅ Done! All sessions now have attendance records.")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await db.rollback()
        finally:
            break


if __name__ == "__main__":
    asyncio.run(create_missing_attendances())
