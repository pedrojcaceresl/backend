# UPE Program Backend

API backend para el programa de perfeccionamiento profesional universitario.

## Estructura del Proyecto

```
backend/
├── app/
│   ├── __init__.py
│   ├── controllers/           # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── auth_controller.py
│   │   ├── user_controller.py
│   │   ├── job_controller.py
│   │   ├── content_controller.py
│   │   └── stats_controller.py
│   ├── core/                  # Configuración y dependencias centrales
│   │   ├── __init__.py
│   │   ├── config.py          # Configuración de la aplicación
│   │   ├── database.py        # Conexión a base de datos
│   │   └── dependencies.py    # Dependencias de FastAPI
│   ├── models/                # Modelos Pydantic
│   │   ├── __init__.py
│   │   ├── enums.py          # Enumeraciones
│   │   ├── user.py           # Modelos de usuario
│   │   ├── job.py            # Modelos de trabajos
│   │   ├── course.py         # Modelos de cursos
│   │   ├── event.py          # Modelos de eventos
│   │   └── saved_item.py     # Modelos de elementos guardados
│   ├── routes/                # Rutas de API
│   │   ├── __init__.py
│   │   ├── auth.py           # Rutas de autenticación
│   │   ├── users.py          # Rutas de usuarios
│   │   ├── jobs.py           # Rutas de trabajos
│   │   ├── content.py        # Rutas de contenido
│   │   ├── company.py        # Rutas de empresa
│   │   └── stats.py          # Rutas de estadísticas
│   ├── services/              # Servicios de base de datos
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── job_service.py
│   │   ├── course_service.py
│   │   ├── event_service.py
│   │   ├── saved_item_service.py
│   │   └── stats_service.py
│   └── utils/                 # Utilidades
│       ├── __init__.py
│       └── helpers.py
├── uploads/                   # Archivos subidos
├── main.py                    # Punto de entrada principal
├── server.py                  # DEPRECATED - usar main.py
├── requirements.txt           # Dependencias
├── .env.example              # Ejemplo de variables de entorno
└── README.md                 # Este archivo
```

## Arquitectura

### Patrón de Capas

1. **Routes (Rutas)**: Reciben las peticiones HTTP y las direccionan
2. **Controllers (Controladores)**: Contienen la lógica de negocio
3. **Services (Servicios)**: Manejan las operaciones de base de datos
4. **Models (Modelos)**: Definen la estructura de datos con Pydantic

### Separación de Responsabilidades

- **Routes**: Solo manejan HTTP, validación de entrada y respuesta
- **Controllers**: Lógica de negocio, validaciones complejas, coordinación entre servicios
- **Services**: Operaciones CRUD, consultas a base de datos
- **Models**: Validación y serialización de datos

## Instalación y Configuración

1. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar variables de entorno**:
   ```bash
   cp .env.example .env
   # Editar .env con tus valores
   ```

3. **Ejecutar la aplicación**:
   ```bash
   # Desarrollo
   python main.py
   
   # O con uvicorn directamente
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## Endpoints Principales

### Autenticación
- `POST /api/auth/complete` - Completar autenticación
- `GET /api/auth/me` - Obtener usuario actual
- `POST /api/auth/logout` - Cerrar sesión

### Usuarios
- `PUT /api/users/profile` - Actualizar perfil
- `POST /api/users/upload-file` - Subir archivo

### Trabajos
- `GET /api/jobs` - Listar trabajos
- `POST /api/jobs` - Crear trabajo (empresas)
- `GET /api/jobs/{id}` - Obtener trabajo específico
- `POST /api/jobs/{id}/apply` - Aplicar a trabajo

### Contenido
- `GET /api/courses` - Listar cursos
- `GET /api/events` - Listar eventos
- `POST /api/saved-items` - Guardar elemento
- `GET /api/saved-items` - Obtener elementos guardados

### Empresa
- `GET /api/company/applications` - Ver aplicaciones
- `PUT /api/company/applications/{id}/status` - Actualizar estado

### Estadísticas
- `GET /api/stats` - Estadísticas de la plataforma

## Beneficios de la Nueva Estructura

### Mantenibilidad
- Código organizado por responsabilidades
- Fácil localización de funcionalidades
- Separación clara entre capas

### Escalabilidad
- Fácil agregar nuevas funcionalidades
- Servicios reutilizables
- Estructura modular

### Testabilidad
- Cada capa se puede testear independientemente
- Inyección de dependencias facilita mocking
- Lógica de negocio aislada

### Legibilidad
- Archivos más pequeños y enfocados
- Imports más claros
- Estructura familiar para desarrolladores

## Migración desde server.py

El archivo `server.py` original ha sido reestructurado manteniendo toda la funcionalidad:

1. **Modelos**: Movidos a `app/models/`
2. **Rutas**: Separadas en `app/routes/`
3. **Lógica**: Movida a `app/controllers/`
4. **Base de datos**: Abstraída en `app/services/`
5. **Configuración**: Centralizada en `app/core/`

Para usar la nueva estructura, simplemente ejecuta `main.py` en lugar de `server.py`.

## Desarrollo

### Agregar Nueva Funcionalidad

1. **Crear modelo** en `app/models/`
2. **Crear servicio** en `app/services/`
3. **Crear controlador** en `app/controllers/`
4. **Crear rutas** en `app/routes/`
5. **Registrar router** en `app/routes/__init__.py`

### Mejores Prácticas

- Un archivo por modelo/servicio/controlador
- Nombres descriptivos y consistentes
- Documentar endpoints con docstrings
- Usar tipos de Python (typing)
- Validar entrada con Pydantic
- Manejar errores apropiadamente