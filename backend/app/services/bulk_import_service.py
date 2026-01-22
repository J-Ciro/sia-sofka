"""Bulk import/export service for students via Excel."""

from collections import Counter
from datetime import date
from io import BytesIO
from typing import BinaryIO
import logging

import pandas as pd
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.core.security import get_password_hash
from app.core.exceptions import (
    FileFormatError,
    FileSizeError,
    FileCorruptedError,
    EmptyFileError,
    MissingColumnsError,
    TooManyRowsError,
    DatabaseOperationError,
)
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.bulk_import import (
    REQUIRED_EXCEL_COLUMNS,
    BulkImportError,
    BulkImportResult,
    EstudianteImportRow,
)
from app.utils.codigo_generator import generar_codigo_institucional

MAX_ROWS = 1000
MAX_FILE_SIZE_MB = 5

logger = logging.getLogger(__name__)


class BulkImportService:
    """Service for parsing, validating and bulk import/export of students."""

    def __init__(self, db: AsyncSession | None):
        self.db = db
        self.repository = UserRepository(db) if db is not None else None

    def parse_excel(self, stream: BinaryIO) -> list[dict]:
        """Parse Excel into list of dicts. Validates required columns and max rows.

        Args:
            stream: .xlsx file-like (BytesIO or UploadFile.file)

        Returns:
            List of dicts, one per row. fecha_nacimiento as date, NaN->None.

        Raises:
            FileCorruptedError: If file cannot be read or is corrupted.
            MissingColumnsError: If required columns are missing.
            TooManyRowsError: If file exceeds maximum row limit.
            EmptyFileError: If file contains no data rows.
        """
        try:
            df = pd.read_excel(stream, engine="openpyxl")
        except Exception as e:
            logger.error(f"Error reading Excel file: {str(e)}")
            if "not a valid Excel file" in str(e).lower() or "corrupt" in str(e).lower():
                raise FileCorruptedError()
            elif "no such file" in str(e).lower() or "permission denied" in str(e).lower():
                raise FileCorruptedError()
            else:
                raise FileCorruptedError()
        
        # Check if file is empty (no rows or no columns)
        if len(df) == 0 or len(df.columns) == 0:
            raise EmptyFileError()
        
        # Clean column names
        df = df.rename(columns={c: (c.strip() if isinstance(c, str) else c) for c in df.columns})
        
        # Check for required columns
        missing = [c for c in REQUIRED_EXCEL_COLUMNS if c not in df.columns]
        if missing:
            raise MissingColumnsError(missing)
        
        # Check row limit
        if len(df) > MAX_ROWS:
            raise TooManyRowsError(len(df), MAX_ROWS)
        
        # Process rows
        out = []
        try:
            for _, r in df.iterrows():
                d = r.to_dict()
                for k in list(d):
                    if pd.isna(d[k]):
                        d[k] = None
                    elif k == "fecha_nacimiento" and d[k] is not None:
                        try:
                            d[k] = pd.Timestamp(d[k]).date()
                        except (ValueError, TypeError) as e:
                            logger.warning(f"Invalid date format in row {len(out) + 2}, column {k}: {d[k]}")
                            # Keep original value, validation will catch it later
                    elif k == "numero_contacto" and d[k] is not None and isinstance(d[k], (int, float)):
                        d[k] = str(int(d[k])) if d[k] == int(d[k]) else str(d[k])
                    elif d[k] is not None and not isinstance(d[k], str) and not isinstance(d[k], date):
                        d[k] = str(d[k])
                out.append(d)
        except Exception as e:
            logger.error(f"Error processing Excel data: {str(e)}")
            raise FileCorruptedError()
        
        return out

    def validate_rows(
        self, rows: list[dict]
    ) -> tuple[list[EstudianteImportRow], list[BulkImportError]]:
        """Validate dict rows with Pydantic and check duplicate emails in file.

        Returns:
            (valid_rows, errors). If duplicate email in file, those rows are in errors.
        """
        valid_temp: list[tuple[int, EstudianteImportRow]] = []
        errors: list[BulkImportError] = []
        for i, d in enumerate(rows):
            row_1based = i + 2  # Excel: 1=header, 2=first data
            try:
                r = EstudianteImportRow.model_validate(d)
                valid_temp.append((row_1based, r))
            except ValidationError as e:
                errs = e.errors()
                for ei in errs:
                    loc = ei.get("loc", ())
                    field = loc[0] if loc else "?"
                    msg = ei.get("msg", str(ei))
                    val = d.get(field) if isinstance(d, dict) else None
                    errors.append(
                        BulkImportError(
                            row=row_1based,
                            field=str(field),
                            message=msg,
                            value=str(val)[:100] if val is not None else None,
                        )
                    )
        emails = [r.email for (_, r) in valid_temp]
        dup_emails = {e for e, c in Counter(emails).items() if c > 1}
        valid: list[EstudianteImportRow] = []
        for idx, r in valid_temp:
            if r.email in dup_emails:
                errors.append(
                    BulkImportError(
                        row=idx,
                        field="email",
                        message="Email duplicado dentro del mismo archivo",
                        value=r.email,
                    )
                )
            else:
                valid.append(r)
        return valid, errors

    async def bulk_import_students(
        self, rows: list[EstudianteImportRow]
    ) -> BulkImportResult:
        """Upsert students: create if new, update if email exists (password unchanged).

        All-or-nothing: on any error, rollback and raise.

        Args:
            rows: Pre-validated rows.

        Returns:
            BulkImportResult with created, updated, errors (empty on success).
            
        Raises:
            DatabaseOperationError: If database operations fail.
        """
        if self.db is None or self.repository is None:
            raise DatabaseOperationError("inicialización", "BulkImportService requires database connection")
        
        created = 0
        updated = 0
        
        try:
            for r in rows:
                try:
                    existing = await self.repository.get_by_email(r.email)
                    if existing:
                        # Update existing user
                        existing.nombre = r.nombre
                        existing.apellido = r.apellido
                        existing.fecha_nacimiento = r.fecha_nacimiento
                        existing.numero_contacto = r.numero_contacto
                        existing.programa_academico = r.programa_academico
                        existing.ciudad_residencia = r.ciudad_residencia
                        existing.edad = existing.calcular_edad()
                        updated += 1
                        logger.info(f"Updated user: {r.email}")
                    else:
                        # Create new user
                        try:
                            codigo = await generar_codigo_institucional(self.db, UserRole.ESTUDIANTE.value)
                        except Exception as e:
                            logger.error(f"Error generating institutional code: {str(e)}")
                            raise DatabaseOperationError("generación de código institucional", str(e))
                        
                        user = User(
                            email=r.email,
                            password_hash=get_password_hash(r.password),
                            role=UserRole.ESTUDIANTE,
                            nombre=r.nombre,
                            apellido=r.apellido,
                            codigo_institucional=codigo,
                            fecha_nacimiento=r.fecha_nacimiento,
                            numero_contacto=r.numero_contacto,
                            programa_academico=r.programa_academico,
                            ciudad_residencia=r.ciudad_residencia,
                        )
                        user.edad = user.calcular_edad()
                        self.db.add(user)
                        await self.db.flush()  # hace visible el nuevo usuario para el siguiente generar_codigo
                        created += 1
                        logger.info(f"Created user: {r.email}")
                        
                except SQLAlchemyError as e:
                    logger.error(f"Database error processing user {r.email}: {str(e)}")
                    await self.db.rollback()
                    raise DatabaseOperationError("procesamiento de usuario", f"Error con usuario {r.email}: {str(e)}")
                except Exception as e:
                    logger.error(f"Unexpected error processing user {r.email}: {str(e)}")
                    await self.db.rollback()
                    raise DatabaseOperationError("procesamiento de usuario", f"Error inesperado con usuario {r.email}")
            
            # Commit all changes
            await self.db.commit()
            logger.info(f"Bulk import completed: {created} created, {updated} updated")
            return BulkImportResult(created=created, updated=updated, errors=[])
            
        except DatabaseOperationError:
            # Re-raise database operation errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error during bulk import: {str(e)}")
            await self.db.rollback()
            raise DatabaseOperationError("importación masiva", str(e))

    async def export_users_to_excel(self, role: str | None = None) -> BytesIO:
        """Export users to Excel. Excludes password_hash. Max 1000 rows.

        Args:
            role: Filter by role (e.g. 'Estudiante'). If None, exports all.

        Returns:
            BytesIO with .xlsx content.
            
        Raises:
            DatabaseOperationError: If database query fails.
            FileCorruptedError: If Excel generation fails.
        """
        if self.db is None or self.repository is None:
            raise DatabaseOperationError("inicialización", "BulkImportService requires database connection")
        
        try:
            if role:
                users = await self.repository.get_by_role(role, 0, 1000)
            else:
                users = await self.repository.get_all(0, 1000)
        except SQLAlchemyError as e:
            logger.error(f"Database error during export: {str(e)}")
            raise DatabaseOperationError("consulta de usuarios", str(e))
        except Exception as e:
            logger.error(f"Unexpected error during user query: {str(e)}")
            raise DatabaseOperationError("consulta de usuarios", str(e))
        
        try:
            rows = []
            for u in users:
                r = {
                    "id": u.id,
                    "email": u.email,
                    "role": u.role.value if hasattr(u.role, "value") else str(u.role),
                    "nombre": u.nombre,
                    "apellido": u.apellido,
                    "codigo_institucional": u.codigo_institucional,
                    "fecha_nacimiento": u.fecha_nacimiento,
                    "numero_contacto": u.numero_contacto,
                    "programa_academico": u.programa_academico,
                    "ciudad_residencia": u.ciudad_residencia,
                    "created_at": u.created_at,
                    "updated_at": u.updated_at,
                }
                rows.append(r)
            
            df = pd.DataFrame(rows)
            buf = BytesIO()
            df.to_excel(buf, index=False, engine="openpyxl")
            buf.seek(0)
            
            logger.info(f"Successfully exported {len(rows)} users to Excel")
            return buf
            
        except Exception as e:
            logger.error(f"Error generating Excel file: {str(e)}")
            raise FileCorruptedError("archivo de exportación")

    def generate_import_template(self) -> BytesIO:
        """Generate empty Excel template with required headers and 2 example rows."""
        examples = [
            {
                "email": "ejemplo1@sofka.edu",
                "password": "Password123!",
                "nombre": "Juan",
                "apellido": "Pérez",
                "rol": "Estudiante",
                "fecha_nacimiento": date(2000, 5, 15),
                "numero_contacto": "3001234567",
                "programa_academico": "Ingeniería de Sistemas",
                "ciudad_residencia": "Cali",
            },
            {
                "email": "ejemplo2@sofka.edu",
                "password": "Password123!",
                "nombre": "María",
                "apellido": "García",
                "rol": "Estudiante",
                "fecha_nacimiento": date(2001, 3, 10),
                "numero_contacto": "3009876543",
                "programa_academico": "Medicina",
                "ciudad_residencia": "Bogotá",
            },
        ]
        df = pd.DataFrame(examples, columns=REQUIRED_EXCEL_COLUMNS)
        buf = BytesIO()
        df.to_excel(buf, index=False, engine="openpyxl")
        buf.seek(0)
        return buf
