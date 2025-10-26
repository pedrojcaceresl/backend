# Sistema de Autenticación - TechHub UPE

## 🔐 Cambio de OAuth a Autenticación Local

**¡PROBLEMA RESUELTO!** El enlace `AUTH_API_BASE_URL=https://demobackend.emergentagent.com/auth/v1/env/oauth` **NO era tuyo** y no funcionaba. Por eso las pruebas de autenticación fallaban.

## ✅ Nueva Implementación

Ahora tienes un **sistema de autenticación local completo** que funciona sin depender de servicios externos.

### 🆕 Nuevos Endpoints

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/auth/register` | POST | Registrar nuevo usuario |
| `/auth/login` | POST | Iniciar sesión |
| `/auth/me` | GET | Obtener info del usuario actual |
| `/auth/logout` | POST | Cerrar sesión |
| `/auth/change-password` | POST | Cambiar contraseña |
| `/auth/complete` | POST | ⚠️ **DEPRECADO** (OAuth legacy) |

### 📝 Cómo usar el nuevo sistema:

#### 1️⃣ Registrar un usuario:
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User",
    "role": "STUDENT"
  }'
```

**Respuesta:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid-here",
    "email": "test@example.com",
    "name": "Test User",
    "role": "STUDENT",
    "is_verified": true
  }
}
```

#### 2️⃣ Iniciar sesión:
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

#### 3️⃣ Obtener info del usuario actual:
```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Cookie: session_token=your_session_token_here"
```

### 🛠️ Configuración actualizada

**Archivo `.env` actualizado:**
```properties
# Database Configuration
ENV=DEVELOPMENT

# Authentication Configuration (Local)
JWT_SECRET_KEY=your-secret-key-change-this-in-production-please
AUTH_MODE=local

# ❌ YA NO NECESITAS ESTO:
# AUTH_API_BASE_URL=https://demobackend.emergentagent.com/auth/v1/env/oauth
```

### 📋 Roles de usuario disponibles:

- **ADMIN**: Acceso completo al sistema
- **STUDENT**: Puede ver cursos, eventos, postularse a trabajos
- **COMPANY**: Puede publicar trabajos, ver candidatos

### 🔧 Crear usuarios de prueba

Ejecuta este script para crear usuarios de prueba:

```bash
python scripts/create_test_users.py
```

**Credenciales de prueba:**
- **Admin**: `admin@techhub.com` / `admin123`
- **Student**: `student@techhub.com` / `student123`
- **Company**: `company@techhub.com` / `company123`

### 🧪 Tests actualizados

Los tests ahora funcionan con el nuevo sistema:

```bash
# Ejecutar tests de autenticación
python -m pytest tests/test_auth_flow.py -v

# Ejecutar todos los tests
python run_tests.py
```

### 🔒 Características de seguridad:

✅ **Contraseñas hasheadas** con bcrypt  
✅ **JWT tokens** para autenticación de API  
✅ **Session cookies** HTTPOnly y seguras  
✅ **Expiración automática** de sesiones  
✅ **Validación de entrada** con Pydantic  
✅ **Usuarios verificados automáticamente**  

### 🚀 Ventajas del nuevo sistema:

1. **✅ Funciona independientemente** - No depende de servicios externos
2. **✅ Fácil de testear** - Todos los tests pasan
3. **✅ Más control** - Puedes modificar la lógica como necesites
4. **✅ Más rápido** - No hay llamadas HTTP externas
5. **✅ Más seguro** - Controlas toda la seguridad

### 📁 Archivos nuevos/modificados:

```
app/
├── utils/
│   └── auth.py                    # ✅ NUEVO: Utilidades de autenticación
├── models/
│   ├── auth.py                    # ✅ NUEVO: Modelos de autenticación
│   └── user.py                    # ✅ MODIFICADO: Agregado password_hash
├── controllers/
│   └── auth_controller_local.py   # ✅ NUEVO: Controlador local
├── routes/
│   └── auth.py                    # ✅ MODIFICADO: Nuevos endpoints
└── core/
    └── config.py                  # ✅ MODIFICADO: Nueva configuración

scripts/
└── create_test_users.py           # ✅ NUEVO: Crear usuarios de prueba

tests/
└── test_auth_flow.py              # ✅ MODIFICADO: Tests del nuevo sistema

.env                               # ✅ MODIFICADO: Nueva configuración
requirements.txt                   # ✅ MODIFICADO: Agregado bcrypt
```

### 🎯 Siguientes pasos:

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Crear usuarios de prueba:**
   ```bash
   python scripts/create_test_users.py
   ```

3. **Ejecutar tests:**
   ```bash
   python run_tests.py
   ```

4. **Iniciar el servidor:**
   ```bash
   uvicorn main:app --reload
   ```

5. **Probar los endpoints** con las credenciales de prueba

## 🎉 ¡Ya no tienes dependencias externas rotas!

Tu sistema de autenticación ahora es **completamente funcional e independiente**. Puedes desarrollar, testear y desplegar sin problemas.

---

**💡 Nota:** El endpoint `/auth/complete` sigue disponible por compatibilidad, pero ahora devuelve un mensaje explicando que OAuth no está disponible y que deben usar los nuevos endpoints de login.