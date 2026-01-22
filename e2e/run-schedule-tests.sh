#!/bin/bash

# Script para ejecutar tests E2E específicos del sistema de horarios y calendario
# 
# Basado en:
# - .github/historias-usuario/hu-horarios-calendario.md
# - .github/plan/feature-horarios-calendario-1.md

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Valores por defecto
TEST_TYPE="all"
MODE="headless"
BROWSER="chromium"

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}🗓️  SIA SOFKA - Tests E2E de Horarios y Calendario${NC}"
    echo -e "${BLUE}=================================================${NC}"
    echo ""
    echo "Uso: ./run-schedule-tests.sh [opciones]"
    echo ""
    echo -e "${YELLOW}Opciones:${NC}"
    echo "  -t, --type <tipo>      Tipo de test a ejecutar (default: all)"
    echo "  -m, --mode <modo>      Modo de ejecución (default: headless)"
    echo "  -b, --browser <nav>    Navegador a usar (default: chromium)"
    echo "  -h, --help             Mostrar esta ayuda"
    echo ""
    echo -e "${YELLOW}Tipos de Test:${NC}"
    echo "  all      - Todos los tests"
    echo "  hu01     - HU-01: Crear Horario de Clase"
    echo "  hu02     - HU-02: Validar Conflictos de Salón"
    echo "  hu03     - HU-03: Validar Conflictos de Profesor"
    echo "  hu04     - HU-04: Editar Horario Existente"
    echo "  hu05     - HU-05: Eliminar Horario"
    echo "  hu06     - HU-06: Visualizar Calendario Semanal"
    echo "  hu07     - HU-07: Filtrar Horarios en Calendario"
    echo "  hu08     - HU-08: Ver Detalle de Horario desde Calendario"
    echo "  hu09     - HU-09: Exportar Horarios a PDF"
    echo "  hu10     - HU-10: Notificar Cambios de Horario"
    echo "  edge     - Edge Cases y Validaciones Críticas"
    echo "  conflicts- Tests de conflictos (HU-02 + HU-03)"
    echo "  calendar - Tests de calendario (HU-06 + HU-07 + HU-08)"
    echo "  filters  - Tests de filtros (HU-07)"
    echo ""
    echo -e "${YELLOW}Modos:${NC}"
    echo "  headless - Sin interfaz gráfica"
    echo "  headed   - Con interfaz gráfica"
    echo "  ui       - Interfaz de Playwright"
    echo "  debug    - Modo debug paso a paso"
    echo ""
    echo -e "${YELLOW}Navegadores:${NC}"
    echo "  chromium - Google Chrome"
    echo "  firefox  - Mozilla Firefox"
    echo "  webkit   - Safari"
    echo ""
    echo -e "${YELLOW}Ejemplos:${NC}"
    echo "  ./run-schedule-tests.sh"
    echo "  ./run-schedule-tests.sh -t hu01 -m ui"
    echo "  ./run-schedule-tests.sh -t conflicts -m headed"
    echo "  ./run-schedule-tests.sh -t all -m headless -b firefox"
}

# Función para mostrar header
show_header() {
    echo -e "${BLUE}🗓️  SIA SOFKA - Tests E2E de Horarios y Calendario${NC}"
    echo -e "${BLUE}=================================================${NC}"
    echo -e "${YELLOW}Tipo de Test: $TEST_TYPE${NC}"
    echo -e "${YELLOW}Modo: $MODE${NC}"
    echo -e "${YELLOW}Navegador: $BROWSER${NC}"
    echo ""
}

# Función para obtener el patrón de test
get_test_pattern() {
    case $1 in
        "hu01") echo "HU-01: Crear Horario de Clase" ;;
        "hu02") echo "HU-02: Validar Conflictos de Salón" ;;
        "hu03") echo "HU-03: Validar Conflictos de Profesor" ;;
        "hu04") echo "HU-04: Editar Horario Existente" ;;
        "hu05") echo "HU-05: Eliminar Horario" ;;
        "hu06") echo "HU-06: Visualizar Calendario Semanal" ;;
        "hu07") echo "HU-07: Filtrar Horarios en Calendario" ;;
        "hu08") echo "HU-08: Ver Detalle de Horario desde Calendario" ;;
        "hu09") echo "HU-09: Exportar Horarios a PDF" ;;
        "hu10") echo "HU-10: Notificar Cambios de Horario" ;;
        "edge") echo "Edge Cases y Validaciones Críticas" ;;
        "conflicts") echo "Validar Conflictos" ;;
        "calendar") echo "Calendario" ;;
        "filters") echo "Filtrar" ;;
        *) echo "all" ;;
    esac
}

# Función para mostrar información del test
show_test_info() {
    echo -e "${BLUE}📋 Información del Test:${NC}"
    
    case $1 in
        "hu01")
            echo -e "${GREEN}• HU-01: Crear Horario de Clase${NC}"
            echo "  - Escenario 1: Crear horario exitosamente sin conflictos"
            echo "  - Escenario 2: Validación de hora fin posterior a hora inicio"
            echo "  - Escenario 3: Validación de duración mínima y máxima"
            ;;
        "hu02")
            echo -e "${GREEN}• HU-02: Validar Conflictos de Salón${NC}"
            echo "  - Escenario 1: Detectar conflicto de salón"
            echo "  - Escenario 2: Horarios consecutivos sin conflicto"
            echo "  - Escenario 3: Salones diferentes sin conflicto"
            ;;
        "hu06")
            echo -e "${GREEN}• HU-06: Visualizar Calendario Semanal${NC}"
            echo "  - Escenario 1: Ver calendario con horarios"
            echo "  - Escenario 2: Clases superpuestas visualmente distinguibles"
            echo "  - Escenario 3: Navegación entre semanas"
            ;;
        "edge")
            echo -e "${GREEN}• Edge Cases y Validaciones Críticas${NC}"
            echo "  - Validación de horario límite (23:59)"
            echo "  - Validación de horario límite (00:00)"
            echo "  - Performance con muchos horarios"
            echo "  - Validación de campos obligatorios"
            ;;
        "all")
            echo -e "${GREEN}• Ejecutando TODOS los tests de horarios (HU-01 a HU-10 + Edge Cases)${NC}"
            echo "  - Total: ~40 tests individuales"
            echo "  - Tiempo estimado: 15-25 minutos"
            ;;
    esac
    echo ""
}

# Función para verificar prerequisitos
check_prerequisites() {
    echo -e "${YELLOW}🔍 Verificando prerequisitos...${NC}"
    
    # Verificar que estamos en el directorio correcto
    if [ ! -f "package.json" ]; then
        echo -e "${RED}❌ Error: No se encontró package.json. Ejecute desde el directorio e2e/${NC}"
        exit 1
    fi
    
    # Verificar que existe el archivo de tests
    if [ ! -f "tests/e2e/schedules.spec.js" ]; then
        echo -e "${RED}❌ Error: No se encontró schedules.spec.js${NC}"
        exit 1
    fi
    
    # Verificar que existe el Page Object
    if [ ! -f "tests/pages/SchedulePage.js" ]; then
        echo -e "${RED}❌ Error: No se encontró SchedulePage.js${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Prerequisitos verificados${NC}"
    echo ""
}

# Función para construir el comando de test
get_test_command() {
    local test_pattern="$1"
    local test_mode="$2"
    local test_browser="$3"
    
    local command="npx playwright test schedules.spec.js"
    
    # Agregar patrón de test específico
    if [ "$test_pattern" != "all" ]; then
        command="$command -g \"$test_pattern\""
    fi
    
    # Agregar configuración de modo
    case $test_mode in
        "headed") command="$command --headed" ;;
        "ui") command="$command --ui" ;;
        "debug") command="$command --debug" ;;
    esac
    
    # Agregar navegador específico
    if [ "$test_browser" != "chromium" ]; then
        command="$command --project=$test_browser"
    fi
    
    echo "$command"
}

# Función para mostrar información post-test
show_post_test_info() {
    echo ""
    echo -e "${BLUE}📊 Información Post-Test:${NC}"
    echo "• Reporte HTML: ./playwright-report/index.html"
    echo "• Resultados JSON: ./playwright-results.json"
    echo "• Screenshots (si hay fallos): ./test-results/"
    echo ""
    
    echo -e "${BLUE}🔧 Comandos útiles:${NC}"
    echo "• Ver reporte: npx playwright show-report"
    echo "• Ejecutar test específico: npx playwright test schedules.spec.js -g 'nombre del test'"
    echo "• Modo debug: npx playwright test schedules.spec.js --debug"
    echo "• Generar código: npx playwright codegen http://localhost:3000"
    echo ""
    
    echo -e "${BLUE}📚 Documentación:${NC}"
    echo "• HU Mapping: ./tests/docs/schedule-hu-test-mapping.md"
    echo "• Historias Usuario: ../.github/historias-usuario/hu-horarios-calendario.md"
    echo "• Plan Implementación: ../.github/plan/feature-horarios-calendario-1.md"
}

# Parsear argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            TEST_TYPE="$2"
            shift 2
            ;;
        -m|--mode)
            MODE="$2"
            shift 2
            ;;
        -b|--browser)
            BROWSER="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Opción desconocida: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Validar argumentos
case $TEST_TYPE in
    all|hu01|hu02|hu03|hu04|hu05|hu06|hu07|hu08|hu09|hu10|edge|conflicts|calendar|filters) ;;
    *)
        echo -e "${RED}Tipo de test inválido: $TEST_TYPE${NC}"
        show_help
        exit 1
        ;;
esac

case $MODE in
    headless|headed|ui|debug) ;;
    *)
        echo -e "${RED}Modo inválido: $MODE${NC}"
        show_help
        exit 1
        ;;
esac

case $BROWSER in
    chromium|firefox|webkit) ;;
    *)
        echo -e "${RED}Navegador inválido: $BROWSER${NC}"
        show_help
        exit 1
        ;;
esac

# Función principal
main() {
    show_header
    check_prerequisites
    show_test_info "$TEST_TYPE"
    
    local test_pattern=$(get_test_pattern "$TEST_TYPE")
    local command=$(get_test_command "$test_pattern" "$MODE" "$BROWSER")
    
    echo -e "${YELLOW}🚀 Ejecutando comando:${NC}"
    echo "$command"
    echo ""
    
    # Ejecutar el comando
    if eval "$command"; then
        echo -e "${GREEN}✅ Tests completados exitosamente!${NC}"
        exit_code=0
    else
        exit_code=$?
        echo -e "${RED}❌ Algunos tests fallaron (código de salida: $exit_code)${NC}"
    fi
    
    show_post_test_info
    exit $exit_code
}

# Ejecutar función principal
main