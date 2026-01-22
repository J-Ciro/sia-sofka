#!/usr/bin/env python3
"""
Script to create Excel fixture files for E2E testing
Creates various test scenarios for bulk import functionality
"""

import pandas as pd
import os
from datetime import datetime, date
import tempfile

# Base directory for fixtures
FIXTURES_DIR = "tests/fixtures"

def create_fixtures_directory():
    """Ensure fixtures directory exists"""
    os.makedirs(FIXTURES_DIR, exist_ok=True)

def create_partial_success_fixture():
    """Create Excel file with mixed valid/invalid data"""
    data = [
        # Valid entries
        {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'email': 'juan.perez@test.com',
            'fecha_nacimiento': '1995-05-15',
            'codigo_institucional': 'EST001',
            'role': 'Estudiante'
        },
        {
            'nombre': 'María',
            'apellido': 'García',
            'email': 'maria.garcia@test.com',
            'fecha_nacimiento': '1996-08-22',
            'codigo_institucional': 'EST002',
            'role': 'Estudiante'
        },
        # Invalid entries (missing required fields)
        {
            'nombre': 'Pedro',
            'apellido': '',  # Missing apellido
            'email': 'pedro@test.com',
            'fecha_nacimiento': '1997-03-10',
            'codigo_institucional': 'EST003',
            'role': 'Estudiante'
        },
        {
            'nombre': 'Ana',
            'apellido': 'López',
            'email': 'invalid-email',  # Invalid email format
            'fecha_nacimiento': '1998-12-05',
            'codigo_institucional': 'EST004',
            'role': 'Estudiante'
        }
    ]
    
    df = pd.DataFrame(data)
    df.to_excel(f"{FIXTURES_DIR}/estudiantes_parcial.xlsx", index=False)
    print("Created: estudiantes_parcial.xlsx")

def create_empty_fixture():
    """Create empty Excel file"""
    df = pd.DataFrame()
    df.to_excel(f"{FIXTURES_DIR}/estudiantes_vacio.xlsx", index=False)
    print("Created: estudiantes_vacio.xlsx")

def create_invalid_headers_fixture():
    """Create Excel file with wrong column headers"""
    data = [
        {
            'wrong_name': 'Juan',
            'wrong_surname': 'Pérez',
            'wrong_email': 'juan@test.com',
            'wrong_date': '1995-05-15',
            'wrong_code': 'EST001',
            'wrong_role': 'Estudiante'
        }
    ]
    
    df = pd.DataFrame(data)
    df.to_excel(f"{FIXTURES_DIR}/estudiantes_headers_invalidos.xlsx", index=False)
    print("Created: estudiantes_headers_invalidos.xlsx")

def create_invalid_data_fixture():
    """Create Excel file with invalid data types and formats"""
    data = [
        {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'email': 'not-an-email',  # Invalid email
            'fecha_nacimiento': '1995-13-45',  # Invalid date
            'codigo_institucional': '',  # Empty required field
            'role': 'InvalidRole'  # Invalid role
        },
        {
            'nombre': '',  # Empty required field
            'apellido': 'García',
            'email': 'maria@test.com',
            'fecha_nacimiento': 'not-a-date',  # Invalid date format
            'codigo_institucional': 'EST002',
            'role': 'Estudiante'
        },
        {
            'nombre': 'Pedro' * 50,  # Too long name
            'apellido': 'López',
            'email': 'pedro@test.com',
            'fecha_nacimiento': '2050-01-01',  # Future date
            'codigo_institucional': 'EST003',
            'role': 'Estudiante'
        }
    ]
    
    df = pd.DataFrame(data)
    df.to_excel(f"{FIXTURES_DIR}/estudiantes_datos_invalidos.xlsx", index=False)
    print("Created: estudiantes_datos_invalidos.xlsx")

def create_duplicate_emails_fixture():
    """Create Excel file with duplicate email addresses"""
    data = [
        {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'email': 'duplicate@test.com',  # Duplicate email
            'fecha_nacimiento': '1995-05-15',
            'codigo_institucional': 'EST001',
            'role': 'Estudiante'
        },
        {
            'nombre': 'María',
            'apellido': 'García',
            'email': 'duplicate@test.com',  # Same email as above
            'fecha_nacimiento': '1996-08-22',
            'codigo_institucional': 'EST002',
            'role': 'Estudiante'
        },
        {
            'nombre': 'Pedro',
            'apellido': 'López',
            'email': 'unique@test.com',  # Unique email
            'fecha_nacimiento': '1997-03-10',
            'codigo_institucional': 'EST003',
            'role': 'Estudiante'
        }
    ]
    
    df = pd.DataFrame(data)
    df.to_excel(f"{FIXTURES_DIR}/estudiantes_emails_duplicados.xlsx", index=False)
    print("Created: estudiantes_emails_duplicados.xlsx")

def create_corrupted_fixture():
    """Create a corrupted Excel file by writing invalid content"""
    filepath = f"{FIXTURES_DIR}/estudiantes_corrupto.xlsx"
    
    # Write invalid binary content that looks like Excel but isn't
    with open(filepath, 'wb') as f:
        f.write(b'PK\x03\x04\x14\x00\x00\x00\x08\x00')  # ZIP header start
        f.write(b'CORRUPTED_EXCEL_FILE_CONTENT')  # Invalid content
        f.write(b'\x00' * 100)  # Padding with nulls
    
    print("Created: estudiantes_corrupto.xlsx (corrupted)")

def main():
    """Create all fixture files"""
    print("Creating E2E test fixture files...")
    
    # Create fixtures directory
    create_fixtures_directory()
    
    # Create all fixture files
    create_partial_success_fixture()
    create_empty_fixture()
    create_invalid_headers_fixture()
    create_invalid_data_fixture()
    create_duplicate_emails_fixture()
    create_corrupted_fixture()
    
    print("\nAll fixture files created successfully!")
    print(f"Files created in: {FIXTURES_DIR}/")
    print("\nFixture files:")
    print("- estudiantes_parcial.xlsx (mixed valid/invalid data)")
    print("- estudiantes_vacio.xlsx (empty file)")
    print("- estudiantes_headers_invalidos.xlsx (wrong column headers)")
    print("- estudiantes_datos_invalidos.xlsx (invalid data types)")
    print("- estudiantes_emails_duplicados.xlsx (duplicate emails)")
    print("- estudiantes_corrupto.xlsx (corrupted file)")
    print("- invalid.txt (non-Excel file)")

if __name__ == "__main__":
    main()