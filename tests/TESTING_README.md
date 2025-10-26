# TechHub Backend - Tests

Esta carpeta contiene todos los tests organizados para el backend de JobConnect.

## Estructura

```
tests/
├── __init__.py                    # Package initialization
├── run_all_tests.py              # Main test runner (ejecuta todos los tests)
├── legacy_*.py                   # Tests legacy movidos de la raíz
├── helpers/                      # Utilities y helpers para testing
│   ├── __init__.py
│   ├── test_client.py            # Cliente de test async reutilizable
│   ├── check_db.py               # Helper para verificar base de datos
│   └── debug_*.py                # Scripts de debug específicos
├── integration/                  # Tests de integración (API endpoints)
│   ├── __init__.py
│   ├── test_health.py            # Tests de salud del servidor
│   ├── test_applications.py      # Tests de endpoints de Applications
│   ├── test_saved_items.py       # Tests de endpoints de SavedItems
│   └── *.py                      # Tests legacy movidos
└── unit/                         # Tests unitarios (para el futuro)
    └── __init__.py
```

## Cómo Ejecutar los Tests

### Ejecutar todos los tests

```bash
# Desde la raíz del proyecto
python tests/run_all_tests.py
```

### Ejecutar tests específicos

```bash
# Test de salud del servidor
python tests/integration/test_health.py

# Test de Applications API
python tests/integration/test_applications.py

# Test de SavedItems API  
python tests/integration/test_saved_items.py
```

### Ejecutar tests legacy

```bash
# Test de nuevos endpoints (más completo)
python tests/integration/test_new_endpoints.py

# Test simple de API
python tests/integration/simple_api_test.py
```

## Requisitos

- Servidor debe estar ejecutándose: `uvicorn main:app --reload --host 0.0.0.0 --port 8000`
- Base de datos debe estar poblada: `python scripts/populate_data.py`
- Dependencias instaladas: `pip install -r requirements.txt`

## Tests Disponibles

### ✅ **Funcionando Perfectamente**

- **test_health.py**: Verificación de salud del servidor
- **test_applications.py**: API completa de Applications (postulaciones)
- **test_saved_items.py**: API completa de SavedItems (favoritos)

### 📋 **Tests Legacy** (movidos de la raíz)

- **test_new_endpoints.py**: Test completo de nuevos endpoints
- **simple_api_test.py**: Test básico de API
- **test_all_endpoints.py**: Test de todos los endpoints

### 🔧 **Helpers**

- **test_client.py**: Cliente async reutilizable con autenticación
- **check_db.py**: Verificación de contenido de base de datos
- **debug_*.py**: Scripts específicos para debugging

## Funcionalidades Probadas

### Applications API ✅

- Autenticación
- Aplicar a trabajos
- Ver mis aplicaciones
- Detalles de aplicación
- Retirar aplicación
- Estadísticas de aplicaciones

### SavedItems API ✅

- Guardar elementos (jobs, courses, events)
- Ver elementos guardados
- Formato legacy compatible
- Verificar si está guardado
- Toggle save/unsave
- Operaciones bulk
- Estadísticas de elementos guardados

### Sistema General ✅

- Salud del servidor
- Documentación de API
- Sistema de autenticación
- Endpoints básicos
