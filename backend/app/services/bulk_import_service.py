"""Bulk import/export service for students via Excel."""

from collections import Counter
from datetime import date
from io import BytesIO
from typing import BinaryIO, Callable, Any
import logging
import re

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
        out: list[dict[str, Any]] = []
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

    def _get_field_display_name(self, field: str) -> str:
        """Get user-friendly field name in Spanish."""
        field_names = {
            "email": "email",
            "password": "contraseña",
            "nombre": "nombre",
            "apellido": "apellido",
            "rol": "rol",
            "fecha_nacimiento": "fecha de nacimiento",
            "numero_contacto": "número de contacto",
            "programa_academico": "programa académico",
            "ciudad_residencia": "ciudad de residencia",
        }
        return field_names.get(field, field)

    def _translate_email_error(self, msg: str) -> str:
        """Translate email validation errors."""
        if "@-sign" in msg.lower() or ("@" in msg.lower() and "sign" in msg.lower()):
            return "El email no es válido: debe contener el símbolo @"
        return "El email no es válido"

    def _translate_string_length_error(self, msg: str, field: str) -> str:
        """Translate string length validation errors."""
        field_display = self._get_field_display_name(field)
        msg_lower = msg.lower()
        
        # Extract number from message
        at_least_match = re.search(r'at least (\d+)', msg_lower)
        at_most_match = re.search(r'at most (\d+)', msg_lower)
        
        if "at least" in msg_lower and at_least_match:
            num = at_least_match.group(1)
            field_specific = {
                "password": f"La contraseña debe tener al menos {num} caracteres",
                "numero_contacto": f"El número de contacto debe tener al menos {num} caracteres",
            }
            return field_specific.get(field, f"El campo {field_display} debe tener al menos {num} caracteres")
        
        if "at most" in msg_lower and at_most_match:
            num = at_most_match.group(1)
            return f"El campo {field_display} es demasiado largo (máximo {num} caracteres)"
        
        return f"El campo {field_display} es demasiado corto" if "at least" in msg_lower else f"El campo {field_display} es demasiado largo"

    def _translate_date_error(self, msg: str) -> str:
        """Translate date validation errors."""
        msg_lower = msg.lower()
        
        # Specific date error patterns with their translations
        date_error_patterns = [
            (r"month.*outside.*expected.*range|month.*1-12", "La fecha no es válida: el mes debe estar entre 1 y 12"),
            (r"invalid.*character.*year", "La fecha no es válida: formato de año incorrecto"),
            (r"day.*(outside|invalid)", "La fecha no es válida: el día no es válido para el mes especificado"),
        ]
        
        for pattern, translation in date_error_patterns:
            if re.search(pattern, msg_lower):
                return translation
        
        # Generic date error
        return "La fecha no es válida o tiene un formato incorrecto"

    def _translate_type_error(self, msg: str, field: str) -> str:
        """Translate type validation errors."""
        field_display = self._get_field_display_name(field)
        msg_lower = msg.lower()
        
        type_translations = {
            "string": f"El campo {field_display} debe ser un texto válido",
            "date": f"El campo {field_display} debe ser una fecha válida",
            "datetime": f"El campo {field_display} debe ser una fecha válida",
            "integer": f"El campo {field_display} debe ser un número entero",
            "int": f"El campo {field_display} debe ser un número entero",
            "float": f"El campo {field_display} debe ser un número",
            "number": f"El campo {field_display} debe ser un número",
        }
        
        for type_key, translation in type_translations.items():
            if type_key in msg_lower:
                return translation
        
        return f"El campo {field_display} no es válido"

    def _extract_value_error_message(self, msg: str) -> str:
        """Extract Spanish message from Value error."""
        for prefix in ["Value error, ", "Value error,"]:
            if prefix in msg:
                return msg.split(prefix, 1)[-1].strip()
        return msg

    def _get_error_translators(self) -> list[tuple[Callable[[str], bool], Callable[[str, str], str]]]:
        """Get list of (pattern_checker, translator) tuples for error translation.
        
        This registry pattern allows adding new error translators without modifying
        the main translation logic. Each tuple contains:
        - pattern_checker: Function(msg: str) -> bool that checks if the error matches
        - translator: Function(msg: str, field: str) -> str that translates the error
        
        To add a new error type, simply add a new tuple to this list:
        
        Example:
            (
                lambda m: "new error pattern" in m.lower(),
                lambda m, f: f"Traducción del nuevo error para {f}"
            ),
        
        Returns:
            List of tuples where first element checks if pattern matches,
            and second element is the translator function.
        """
        return [
            # Email validation errors
            (
                lambda m: "email" in m.lower() or "email address" in m.lower(),
                lambda m, f: self._translate_email_error(m)
            ),
            # String length validation errors
            (
                lambda m: "string should have at least" in m.lower() or "string should have at most" in m.lower(),
                lambda m, f: self._translate_string_length_error(m, f)
            ),
            # Date validation errors
            (
                lambda m: "date" in m.lower() or "datetime" in m.lower(),
                lambda m, f: self._translate_date_error(m)
            ),
            # Type validation errors - string
            (
                lambda m: "input should be a valid string" in m.lower(),
                lambda m, f: f"El campo {self._get_field_display_name(f)} debe ser un texto válido"
            ),
            # Type validation errors - general
            (
                lambda m: "input should be a valid" in m.lower(),
                lambda m, f: self._translate_type_error(m, f)
            ),
            # Value errors (already in Spanish from custom validators)
            (
                lambda m: "value error" in m.lower(),
                lambda m, f: self._extract_value_error_message(m)
            ),
            # Required field errors
            (
                lambda m: "field required" in m.lower() or ("required" in m.lower() and "field" in m.lower()),
                lambda m, f: f"El campo {self._get_field_display_name(f)} es obligatorio"
            ),
        ]

    def _translate_pydantic_error(self, msg: str, field: str) -> str:
        """Translate Pydantic error messages to Spanish.
        
        Uses a registry pattern for maintainability and scalability.
        New error types can be added by extending _get_error_translators().
        
        Args:
            msg: Original Pydantic error message
            field: Field name that caused the error
            
        Returns:
            Translated error message in Spanish
        """
        translators = self._get_error_translators()
        
        for pattern_check, translator in translators:
            if pattern_check(msg):
                translated: str = translator(msg, field)
                return translated
        
        # Return original message if no pattern matches
        return msg

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
                    # Translate error message to Spanish
                    translated_msg = self._translate_pydantic_error(msg, str(field))
                    val = d.get(field) if isinstance(d, dict) else None
                    errors.append(
                        BulkImportError(
                            row=row_1based,
                            field=str(field),
                            message=translated_msg,
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
                        setattr(existing, 'nombre', r.nombre)
                        setattr(existing, 'apellido', r.apellido)
                        setattr(existing, 'fecha_nacimiento', r.fecha_nacimiento)
                        setattr(existing, 'numero_contacto', r.numero_contacto)
                        setattr(existing, 'programa_academico', r.programa_academico)
                        setattr(existing, 'ciudad_residencia', r.ciudad_residencia)
                        setattr(existing, 'edad', existing.calcular_edad())
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
                        setattr(user, 'edad', user.calcular_edad())
                        self.db.add(user)
                        await self.db.flush()  # hace visible el nuevo usuario para el siguiente generar_codigo
                        created += 1
                        logger.info(f"Created user: {r.email}")
                        
                except SQLAlchemyError as e:
                    logger.error(f"Database error processing user {r.email}: {str(e)}")
                    await self.db.rollback()
                    error_type = type(e).__name__
                    raise DatabaseOperationError(
                        "procesamiento de usuario",
                        f"Error en la base de datos al procesar usuario {r.email} ({error_type}): {str(e)}"
                    )
                except Exception as e:
                    logger.error(f"Unexpected error processing user {r.email}: {str(e)}")
                    await self.db.rollback()
                    error_type = type(e).__name__
                    raise DatabaseOperationError(
                        "procesamiento de usuario",
                        f"Error inesperado al procesar usuario {r.email} ({error_type}): {str(e)}"
                    )
            
            # Commit all changes
            await self.db.commit()
            logger.info(f"Bulk import completed: {created} created, {updated} updated")
            return BulkImportResult(created=created, updated=updated, errors=[])
            
        except DatabaseOperationError:
            # Re-raise database operation errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error during bulk import: {str(e)}", exc_info=True)
            await self.db.rollback()
            error_type = type(e).__name__
            raise DatabaseOperationError(
                "importación masiva",
                f"Error inesperado durante la importación masiva ({error_type}): {str(e)}"
            )

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
            error_type = type(e).__name__
            raise DatabaseOperationError(
                "consulta de usuarios",
                f"Error en la base de datos al consultar usuarios para exportación ({error_type}): {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error during user query: {str(e)}")
            error_type = type(e).__name__
            raise DatabaseOperationError(
                "consulta de usuarios",
                f"Error inesperado al consultar usuarios para exportación ({error_type}): {str(e)}"
            )
        
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
            error_type = type(e).__name__
            if "openpyxl" in str(e).lower() or "excel" in str(e).lower():
                raise FileCorruptedError("generación del archivo Excel de exportación")
            else:
                raise DatabaseOperationError(
                    "generación de archivo de exportación",
                    f"Error al generar el archivo Excel ({error_type}): {str(e)}"
                )

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
