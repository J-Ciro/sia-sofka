#!/bin/bash
set -e

echo "Waiting for database to be ready..."
sleep 5

echo "Creating database tables..."
python -c "
import asyncio
from app.core.database import engine, Base
from app.models import User, Subject, Enrollment, Grade

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('✓ Database tables created')

asyncio.run(create_tables())
"

echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
