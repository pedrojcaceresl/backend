# 🚀 Guía de Despliegue en Render

Esta guía te llevará paso a paso para desplegar tu backend tech_hub en Render.

## 📋 Preparativos

### 1. Verificar que tienes todos los archivos
- ✅ `render.yaml` - Configuración de servicios
- ✅ `requirements.txt` - Dependencias de Python
- ✅ `.env.example` - Variables de entorno ejemplo
- ✅ `start.sh` - Script de inicio (opcional)
- ✅ Código de la aplicación en GitHub

### 2. Repositorio en GitHub
Tu código debe estar en un repositorio de GitHub público o privado.

## 🎯 Paso a Paso para Desplegar en Render

### Paso 1: Crear cuenta en Render
1. Ve a [render.com](https://render.com)
2. Regístrate con tu cuenta de GitHub
3. Autoriza Render para acceder a tus repositorios

### Paso 2: Crear Web Service
1. En el dashboard de Render, haz clic en **"New +"**
2. Selecciona **"Web Service"**
3. Conecta tu repositorio de GitHub
4. Selecciona el repositorio de tu backend

### Paso 3: Configurar el Web Service
Rellena los siguientes campos:

**Configuración Básica:**
- **Name**: `tech_hub-backend` (o el nombre que prefieras)
- **Region**: Selecciona la región más cercana
- **Branch**: `main` (o tu rama principal)
- **Root Directory**: (déjalo vacío si el backend está en la raíz)

**Build & Deploy:**
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Plan:**
- Selecciona **"Free"** para empezar (puedes actualizar después)

### Paso 4: Configurar Variables de Entorno
En la sección **"Environment"**, agrega estas variables:

#### Variables Obligatorias:
```bash
# JWT Configuration
JWT_SECRET_KEY=tu_clave_secreta_super_segura_aqui_cambiar
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Database (configuraremos después)
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/tech_hub

# Environment
ENVIRONMENT=production

# CORS (agregar tu dominio de frontend cuando lo tengas)
CORS_ORIGINS=https://tu-frontend.onrender.com,http://localhost:3000

# Upload Configuration
UPLOAD_DIR=uploads
MAX_FILE_SIZE=52428800
LOG_LEVEL=INFO
```

#### Generar JWT_SECRET_KEY segura:
```bash
# En tu terminal local, ejecuta:
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Paso 5: Configurar MongoDB
Tienes dos opciones:

#### Opción A: MongoDB Atlas (Recomendado)
1. Ve a [MongoDB Atlas](https://cloud.mongodb.com)
2. Crea una cuenta gratuita
3. Crea un cluster (M0 es gratis)
4. En "Database Access", crea un usuario
5. En "Network Access", permite todas las IPs (0.0.0.0/0)
6. Obtén la connection string
7. Reemplaza la variable `MONGODB_URL` en Render

#### Opción B: MongoDB en Render (Alternativo)
1. En Render, crea un nuevo **"Private Service"**
2. Usa la imagen Docker: `mongo:latest`
3. Configura las variables de entorno para MongoDB
4. Conecta tu web service a este servicio

### Paso 6: Desplegar
1. Haz clic en **"Create Web Service"**
2. Render comenzará a construir tu aplicación
3. Espera a que el deploy termine (puede tomar varios minutos)

### Paso 7: Verificar el Despliegue
1. Una vez desplegado, obtendrás una URL como: `https://tu-app.onrender.com`
2. Verifica que funciona:
   - `https://tu-app.onrender.com/` - Debe mostrar mensaje de bienvenida
   - `https://tu-app.onrender.com/health` - Debe mostrar status healthy
   - `https://tu-app.onrender.com/docs` - Documentación de la API

### Paso 8: Poblar la Base de Datos
1. En Render, ve a tu servicio
2. En la pestaña **"Shell"**, ejecuta:
```bash
python scripts/populate_data.py
```

### Paso 9: Probar la API
Usa estos endpoints para probar:
```bash
# Health check
curl https://tu-app.onrender.com/health

# Registrar usuario
curl -X POST "https://tu-app.onrender.com/api/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "password": "Test123!",
       "first_name": "Test",
       "last_name": "User",
       "role": "estudiante"
     }'

# Login
curl -X POST "https://tu-app.onrender.com/api/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "password": "Test123!"
     }'
```

## 🔧 Configuraciones Adicionales

### Dominios Personalizados
1. En tu servicio de Render, ve a **"Settings"**
2. En **"Custom Domains"**, agrega tu dominio
3. Configura los DNS según las instrucciones

### Logs y Monitoreo
- Ve a **"Logs"** para ver los logs en tiempo real
- Ve a **"Metrics"** para ver el uso de recursos

### Escalado
- En **"Settings"**, puedes cambiar a planes pagos para más recursos
- Los planes pagos incluyen:
  - Más CPU y RAM
  - No hay downtime por inactividad
  - SSL automático

## 🚨 Solución de Problemas

### Error: "Application failed to respond"
- Verifica que la aplicación está escuchando en `0.0.0.0:$PORT`
- Revisa los logs para errores específicos

### Error de Base de Datos
- Verifica que `MONGODB_URL` está correctamente configurada
- Asegúrate de que MongoDB Atlas permite conexiones desde todas las IPs

### Error de CORS
- Agrega el dominio de tu frontend a `CORS_ORIGINS`
- Verifica que incluyes el protocolo (`https://`)

### Error 500 Internal Server Error
- Revisa los logs en Render
- Verifica que todas las variables de entorno están configuradas

## 📝 Notas Importantes

1. **Plan Gratuito**: Tiene limitaciones:
   - La aplicación se duerme después de 15 minutos de inactividad
   - 750 horas de uso por mes
   - Menos recursos de CPU/RAM

2. **Seguridad**:
   - Cambia `JWT_SECRET_KEY` por una clave segura
   - No uses credenciales de desarrollo en producción
   - Configura CORS solo para dominios necesarios

3. **Rendimiento**:
   - El primer request puede ser lento (cold start)
   - Considera un plan pago para aplicaciones en producción

## 🎉 ¡Listo!

Tu backend tech_hub ahora está desplegado en Render. Puedes:
- Conectar tu frontend a la URL de Render
- Monitorear los logs y métricas
- Actualizar automáticamente con cada push a GitHub

### URLs importantes:
- **API**: `https://tu-app.onrender.com`
- **Documentación**: `https://tu-app.onrender.com/docs`
- **Health Check**: `https://tu-app.onrender.com/health`