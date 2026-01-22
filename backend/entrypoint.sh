#!/bin/bash
set -e

echo "Waiting for database to be ready..."
sleep 5

echo "Setting up database..."
python -c "
import asyncio
from sqlalchemy import text
from app.core.database import get_engine, Base
from app.models import User, Subject, Enrollment, Grade, Classroom, Schedule, ClaseSession, Attendance, AttendanceStats, AttendanceAlert

async def setup_database():
    engine = get_engine()
    async with engine.begin() as conn:
        # Check if alembic_version table exists
        result = await conn.execute(text(\"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version')\"))
        has_alembic = result.scalar()
        
        # Check if subjects table exists
        result = await conn.execute(text(\"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'subjects')\"))
        has_subjects = result.scalar()
        
        if not has_subjects:
            # Fresh database - create base tables first (subjects, users, etc.)
            # Then run migrations for schedules and fecha_especifica
            print('Fresh database detected. Creating base tables (subjects, users, etc.)...')
            await conn.run_sync(Base.metadata.create_all)
            print('✓ Base tables created')
            
            # Now run migrations for schedules (which depend on subjects)
            print('Running migrations for schedules...')
            import subprocess
            subprocess.run(['alembic', 'upgrade', 'head'], check=True)
            print('✓ All migrations applied')
        elif not has_alembic:
            # Tables exist but no migration history
            # Check if fecha_especifica column exists
            result = await conn.execute(text(\"SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'schedules' AND column_name = 'fecha_especifica')\"))
            has_fecha_especifica = result.scalar()
            
            if has_fecha_especifica:
                # All tables and columns exist - stamp head
                print('Database has all tables and columns. Stamping head...')
                import subprocess
                subprocess.run(['alembic', 'stamp', 'head'], check=True)
                print('✓ Migrations marked as applied')
            else:
                # Tables exist but fecha_especifica is missing
                print('Database has tables but missing fecha_especifica. Stamping base migration...')
                import subprocess
                subprocess.run(['alembic', 'stamp', '20260119'], check=True)
                print('Running remaining migrations...')
                subprocess.run(['alembic', 'upgrade', 'head'], check=True)
                print('✓ All migrations applied')
        else:
            # Migration history exists - run migrations to add new fields
            print('Migration history exists. Running migrations...')
            import subprocess
            subprocess.run(['alembic', 'upgrade', 'head'], check=True)
            print('✓ Migrations applied')

asyncio.run(setup_database())
"

echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
