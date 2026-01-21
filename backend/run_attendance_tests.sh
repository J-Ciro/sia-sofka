#!/bin/bash
# Script para ejecutar SOLO los tests de asistencia (cambios del usuario)

cd "$(dirname "$0")"

echo "=========================================="
echo "EXECUTING ATTENDANCE TESTS ONLY"
echo "=========================================="
echo ""

# Tests de asistencia
TESTS=(
    "tests/unit/test_attendance_models.py"
    "tests/unit/test_attendance_repository.py"
    "tests/unit/test_attendance_service.py"
    "tests/unit/test_attendance_schemas.py"
    "tests/unit/test_attendance_validators.py"
    "tests/integration/test_attendance_endpoints.py"
)

# Archivos para cobertura (SOLO asistencia)
COV_FILES=(
    "app/models/attendance.py"
    "app/repositories/attendance_repository.py"
    "app/services/attendance_service.py"
    "app/schemas/attendance.py"
    "app/utils/attendance_validators.py"
    "app/api/v1/endpoints/attendance.py"
)

# Construir comando de cobertura
COV_CMD=""
for file in "${COV_FILES[@]}"; do
    COV_CMD="$COV_CMD --cov=$file"
done

# Ejecutar pytest solo con archivos de asistencia
python -m pytest "${TESTS[@]}" \
    $COV_CMD \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-report=xml \
    -v \
    --tb=short \
    "$@"

echo ""
echo "=========================================="
echo "TEST EXECUTION COMPLETE"
echo "=========================================="
