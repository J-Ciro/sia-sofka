#!/usr/bin/env python3
"""
Debug script to check professor-subject-schedule relationships
"""
import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.core.config import settings
from app.models.user import User, UserRole
from app.models.subject import Subject
from app.models.schedule import Schedule

async def debug_permissions():
    """Check the actual data relationships in the database"""
    try:
        # Create database connection
        engine = create_async_engine(settings.database_url)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as session:
            print("=== DEBUGGING PROFESSOR PERMISSIONS ===\n")
            
            # Get all professors
            result = await session.execute(
                select(User).where(User.role == UserRole.PROFESOR)
            )
            professors = result.scalars().all()
            print(f"Found {len(professors)} professors:")
            for prof in professors:
                print(f"  - ID: {prof.id}, Email: {prof.email}, Name: {prof.nombre} {prof.apellido}")
            
            print()
            
            # Get all subjects with their professors
            result = await session.execute(
                select(Subject).join(User, Subject.profesor_id == User.id)
            )
            subjects = result.scalars().all()
            print(f"Found {len(subjects)} subjects:")
            for subj in subjects:
                # Load the professor relationship
                await session.refresh(subj, ['profesor'])
                prof_name = f"{subj.profesor.nombre} {subj.profesor.apellido}" if subj.profesor else "Unknown"
                print(f"  - ID: {subj.id}, Name: {subj.nombre}, Professor: {prof_name} (ID: {subj.profesor_id})")
            
            print()
            
            # Get all schedules with their subjects and professors
            result = await session.execute(
                select(Schedule)
                .join(Subject, Schedule.subject_id == Subject.id)
                .join(User, Subject.profesor_id == User.id)
            )
            schedules = result.scalars().all()
            print(f"Found {len(schedules)} schedules:")
            for sched in schedules:
                # Load relationships
                await session.refresh(sched, ['subject'])
                await session.refresh(sched.subject, ['profesor'])
                prof_name = f"{sched.subject.profesor.nombre} {sched.subject.profesor.apellido}"
                print(f"  - Schedule ID: {sched.id}")
                print(f"    Subject: {sched.subject.nombre} (ID: {sched.subject_id})")
                print(f"    Professor: {prof_name} (ID: {sched.subject.profesor_id})")
                print(f"    Day: {sched.dia_semana}, Time: {sched.hora_inicio}-{sched.hora_fin}")
                if sched.fecha_especifica:
                    print(f"    Specific Date: {sched.fecha_especifica}")
                print()
            
            # Check for any orphaned schedules (schedules without valid subjects)
            result = await session.execute(
                select(Schedule).outerjoin(Subject, Schedule.subject_id == Subject.id)
                .where(Subject.id.is_(None))
            )
            orphaned = result.scalars().all()
            if orphaned:
                print(f"WARNING: Found {len(orphaned)} orphaned schedules (no valid subject):")
                for sched in orphaned:
                    print(f"  - Schedule ID: {sched.id}, Subject ID: {sched.subject_id} (INVALID)")
            
            # Check for any subjects without professors
            result = await session.execute(
                select(Subject).outerjoin(User, Subject.profesor_id == User.id)
                .where(User.id.is_(None))
            )
            orphaned_subjects = result.scalars().all()
            if orphaned_subjects:
                print(f"WARNING: Found {len(orphaned_subjects)} subjects without valid professors:")
                for subj in orphaned_subjects:
                    print(f"  - Subject ID: {subj.id}, Name: {subj.nombre}, Professor ID: {subj.profesor_id} (INVALID)")
            
            print("\n=== PERMISSION CHECK SIMULATION ===")
            
            # Simulate permission check for each schedule
            for sched in schedules:
                await session.refresh(sched, ['subject'])
                await session.refresh(sched.subject, ['profesor'])
                
                print(f"\nSchedule {sched.id} ({sched.subject.nombre}):")
                print(f"  Subject Professor ID: {sched.subject.profesor_id}")
                
                # Check which professors can update this schedule
                for prof in professors:
                    can_update = prof.id == sched.subject.profesor_id
                    status = "✓ CAN UPDATE" if can_update else "✗ CANNOT UPDATE"
                    print(f"  Professor {prof.id} ({prof.email}): {status}")
        
        await engine.dispose()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_permissions())