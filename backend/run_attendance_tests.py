#!/usr/bin/env python
"""
Script para ejecutar SOLO los tests de asistencia (commits del usuario)
Calcula coverage SOLO para archivos modificados
"""

import subprocess
import sys

# Tests de asistencia (lo que el usuario modificó/creó)
ATTENDANCE_TESTS = [
    "tests/unit/test_attendance_models.py",
    "tests/unit/test_attendance_schemas.py",
    "tests/unit/test_attendance_validators.py",
    "tests/integration/test_attendance_endpoints.py",
]

# Archivos de asistencia (SOLO cobertura de estos)
ATTENDANCE_FILES = [
    "app/models/attendance",
    "app/schemas/attendance",
    "app/utils/attendance_validators",
    "app/api/v1/endpoints/attendance",
]

def main():
    """Ejecutar tests de asistencia"""
    print("=" * 60)
    print("EXECUTING ATTENDANCE TESTS (User modifications only)")
    print("=" * 60)
    print()
    
    # Construir comando pytest
    cmd = ["python", "-m", "pytest"] + ATTENDANCE_TESTS
    
    # Agregar coverage para SOLO archivos de asistencia
    for file in ATTENDANCE_FILES:
        cmd.extend(["--cov=" + file])
    
    # Agregar opciones
    cmd.extend([
        "--cov-report=term-missing",
        "--cov-report=html",
        "-v",
        "--tb=short",
    ])
    
    # Ejecutar
    result = subprocess.run(cmd)
    
    print()
    print("=" * 60)
    print("TEST EXECUTION COMPLETE")
    print("=" * 60)
    print()
    print("Coverage report generated in: htmlcov/index.html")
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
