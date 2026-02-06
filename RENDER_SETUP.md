# Render Deployment - Configuración Correcta

## Problema Resuelto

Render estaba buscando `requirements.txt` en la raíz, pero está en `backend/`.

## Solución: Configuración Manual en Render Dashboard

### Paso 1: Configurar Backend en Render

1. Ve a tu servicio en Render Dashboard
2. Ve a **Settings** → **Build & Deploy**

3. **Actualiza estos campos**:

   **Root Directory**: `backend`
   
   **Build Command**: 
   ```
   pip install -r requirements.txt
   ```
   
   **Start Command**:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

### Paso 2: Variables de Entorno

En **Environment** → **Environment Variables**, agrega:

```
YOU_API_KEY=ydc-sk-09fbca0d85ced898-68ovOc9LUrsIik7Wj8dHOxt96eWwjyM4-42e0deea
OPENAI_API_KEY=tu_openai_key_aqui
COMPOSIO_API_KEY=ak_2kucd3CqABTzY449ABY8
COMPOSIO_ENTITY_ID=pg-test-fbbef01e-671d-4816-bac1-0546cea96299
ENVIRONMENT=production
LOG_LEVEL=INFO
SCAN_INTERVAL_MINUTES=15
```

### Paso 3: Guardar y Deploy

1. Click **Save Changes**
2. Click **Manual Deploy** → **Deploy latest commit**

## Alternativa: Usar render.yaml (Auto-deploy)

Si prefieres configuración automática, el archivo `render.yaml` ya está creado en la raíz del proyecto. Render lo detectará automáticamente.

## Verificación

Después del deploy, verifica:
- ✅ Health check: `https://tu-backend.onrender.com/health`
- ✅ API funciona: `https://tu-backend.onrender.com/api/risk/latest`

## Notas Importantes

- **Root Directory**: Debe ser `backend` para que Render sepa dónde está el código
- **Puerto**: Render asigna un puerto automáticamente, usa `$PORT` en el start command
- **Python Version**: Render detecta automáticamente, pero puedes especificar en `runtime.txt` si necesitas una versión específica
