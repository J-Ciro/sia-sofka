.PHONY: help install install-dev test test-cov lint format type-check quality clean docker-up docker-down docker-logs migrate

help: ## Mostrar ayuda
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Instalar dependencias de producción
	pip install -r requirements.txt

install-dev: ## Instalar dependencias de desarrollo
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

test: ## Ejecutar pruebas
	pytest -v

test-cov: ## Ejecutar pruebas con cobertura
	pytest --cov=app --cov-report=html --cov-report=term-missing --cov-report=xml
	@echo "Reporte HTML generado en htmlcov/index.html"

test-unit: ## Ejecutar solo pruebas unitarias
	pytest tests/unit/ -v

test-integration: ## Ejecutar solo pruebas de integración
	pytest tests/integration/ -v

lint: ## Ejecutar flake8
	flake8 app tests

format: ## Formatear código con black e isort
	black app tests
	isort app tests

format-check: ## Verificar formateo sin modificar
	black --check app tests
	isort --check app tests

type-check: ## Verificar tipos con mypy
	mypy app

quality: format-check lint type-check test-cov ## Ejecutar todas las verificaciones de calidad
	@echo " Todas las verificaciones pasaron exitosamente"

clean: ## Limpiar archivos temporales
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name "coverage.xml" -delete
	find . -type f -name ".coverage" -delete

docker-up: ## Levantar servicios Docker
	docker-compose up -d

docker-down: ## Detener servicios Docker
	docker-compose down

docker-logs: ## Ver logs de Docker
	docker-compose logs -f api

docker-build: ## Construir imagen Docker
	docker-compose build

docker-restart: ## Reiniciar servicios Docker
	docker-compose restart

migrate: ## Ejecutar migraciones
	alembic upgrade head

migrate-create: ## Crear nueva migración (requiere MESSAGE="descripción")
	alembic revision --autogenerate -m "$(MESSAGE)"

migrate-downgrade: ## Revertir última migración
	alembic downgrade -1

run: ## Ejecutar aplicación en desarrollo
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-prod: ## Ejecutar aplicación en producción
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

shell: ## Abrir shell de Python con contexto de la app
	python -i -c "from app.main import app; from app.core.database import SessionLocal"

pre-commit: ## Ejecutar pre-commit en todos los archivos
	pre-commit run --all-files

coverage-report: ## Abrir reporte de cobertura en el navegador
	@python -m webbrowser htmlcov/index.html || open htmlcov/index.html || xdg-open htmlcov/index.html

ci: quality ## Simular pipeline de CI localmente
	@echo " Pipeline de CI completado exitosamente"
