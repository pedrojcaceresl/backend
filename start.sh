#!/bin/bash

# =================================
# SCRIPT DE INICIO PARA RENDER
# =================================

echo "🚀 Iniciando aplicación tech_hub Backend..."

# Verificar que las variables de entorno estén configuradas
if [ -z "$MONGODB_URL" ]; then
    echo "❌ Error: MONGODB_URL no está configurada"
    exit 1
fi

if [ -z "$JWT_SECRET_KEY" ]; then
    echo "❌ Error: JWT_SECRET_KEY no está configurada"
    exit 1
fi

echo "✅ Variables de entorno verificadas"

# Crear directorio de uploads si no existe
mkdir -p uploads

echo "✅ Directorio de uploads creado"

# Verificar la conexión a la base de datos
echo "🔍 Verificando conexión a MongoDB..."

# Ejecutar script de poblado de datos si es necesario
echo "📊 Verificando datos iniciales..."
python -c "
import asyncio
from app.core.database import connect_to_mongo, get_database
from motor.motor_asyncio import AsyncIOMotorClient

async def check_data():
    try:
        await connect_to_mongo()
        db = get_database()
        users_count = await db.users.count_documents({})
        print(f'Usuarios en base de datos: {users_count}')
        if users_count == 0:
            print('Base de datos vacía, ejecutando script de poblado...')
            import subprocess
            subprocess.run(['python', 'scripts/populate_data.py'])
    except Exception as e:
        print(f'Error verificando datos: {e}')

asyncio.run(check_data())
"

echo "✅ Verificación de datos completada"

# Iniciar la aplicación
echo "🎯 Iniciando servidor FastAPI..."

# Usar el puerto proporcionado por Render o 8000 por defecto
PORT=${PORT:-8000}

# Iniciar uvicorn con configuración de producción
exec uvicorn main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --workers 1 \
    --log-level info \
    --access-log \
    --no-use-colors