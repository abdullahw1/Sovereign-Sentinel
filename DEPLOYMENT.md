# Deployment Guide - Sovereign Sentinel

Esta guía te ayudará a desplegar Sovereign Sentinel en producción.

## Arquitectura

- **Backend**: FastAPI (Python) - Puerto 8000
- **Frontend**: Next.js (React) - Puerto 3000
- **Base de datos**: Archivos JSON (persistencia local) o puedes usar PostgreSQL/Redis

## Opción 1: Render (Recomendado)

### Backend en Render

1. **Crear nuevo servicio**:
   - Ve a [render.com](https://render.com)
   - Click en "New" → "Web Service"
   - Conecta tu repositorio de GitHub

2. **Configuración del Backend**:
   ```
   Name: sovereign-sentinel-backend
   Environment: Python 3
   Build Command: cd backend && pip install -r requirements.txt
   Start Command: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

3. **Variables de Entorno**:
   ```
   YOU_API_KEY=tu_you_api_key
   OPENAI_API_KEY=tu_openai_api_key
   COMPOSIO_API_KEY=tu_composio_api_key (opcional)
   ENVIRONMENT=production
   LOG_LEVEL=INFO
   SCAN_INTERVAL_MINUTES=15
   ```

4. **Plan**: Free tier funciona, pero considera Starter ($7/mes) para mejor rendimiento

### Frontend en Render

1. **Crear nuevo servicio**:
   - "New" → "Static Site" o "Web Service"
   - Conecta tu repositorio

2. **Configuración del Frontend**:
   ```
   Build Command: cd frontend && npm install && npm run build
   Publish Directory: frontend/.next
   ```

3. **Variables de Entorno**:
   ```
   NEXT_PUBLIC_API_URL=https://tu-backend.onrender.com
   ```

**Nota**: Si usas Static Site, necesitas usar Vercel o Railway para el frontend (ver abajo).

## Opción 2: Vercel (Frontend) + Render (Backend)

### Frontend en Vercel

1. **Instalar Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Deploy**:
   ```bash
   cd frontend
   vercel
   ```

3. **Configurar variables de entorno en Vercel Dashboard**:
   ```
   NEXT_PUBLIC_API_URL=https://tu-backend.onrender.com
   ```

4. **Deploy automático**: Vercel detecta cambios en GitHub automáticamente

### Backend en Render
(Sigue las instrucciones de la Opción 1)

## Opción 3: Railway (Todo en uno)

### Deploy Backend

1. **Crear proyecto**:
   - Ve a [railway.app](https://railway.app)
   - "New Project" → "Deploy from GitHub repo"

2. **Configurar servicio Backend**:
   - Selecciona el directorio `backend/`
   - Railway detecta automáticamente Python
   - Agrega `start` script en `backend/Procfile`:
     ```
     web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```

3. **Variables de Entorno**:
   - Agrega todas las variables necesarias en Railway dashboard

### Deploy Frontend

1. **Crear segundo servicio**:
   - En el mismo proyecto, "New" → "GitHub Repo"
   - Selecciona directorio `frontend/`

2. **Configurar**:
   - Railway detecta Next.js automáticamente
   - Agrega variable: `NEXT_PUBLIC_API_URL=https://tu-backend.railway.app`

## Opción 4: Docker (Cualquier plataforma)

### Crear Dockerfile para Backend

Crea `backend/Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Crear Dockerfile para Frontend

Crea `frontend/Dockerfile`:
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV production

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000

CMD ["node", "server.js"]
```

Actualiza `frontend/next.config.js`:
```javascript
const nextConfig = {
  output: 'standalone',
  // ... resto de la config
}
```

### Docker Compose (Desarrollo local)

Crea `docker-compose.yml`:
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - YOU_API_KEY=${YOU_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - COMPOSIO_API_KEY=${COMPOSIO_API_KEY}
    volumes:
      - ./backend/data:/app/data

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend
```

Deploy:
```bash
docker-compose up -d
```

## Opción 5: AWS / Google Cloud / Azure

### AWS (Elastic Beanstalk o ECS)

**Backend**:
- Usa Elastic Beanstalk con Python 3.11
- O ECS con Fargate + Application Load Balancer

**Frontend**:
- S3 + CloudFront para hosting estático
- O Amplify para Next.js completo

### Google Cloud (Cloud Run)

**Backend**:
```bash
gcloud run deploy backend \
  --source ./backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**Frontend**:
- Cloud Run o Firebase Hosting

### Azure (App Service)

- Crea dos App Services (uno para backend, uno para frontend)
- Configura variables de entorno en cada uno

## Checklist de Deployment

### Pre-Deployment

- [ ] Todas las variables de entorno configuradas
- [ ] API keys válidas y activas
- [ ] CORS configurado correctamente en backend
- [ ] `NEXT_PUBLIC_API_URL` apunta al backend correcto
- [ ] Tests pasando (si los tienes)

### Backend

- [ ] Puerto configurado correctamente (usar `$PORT` en producción)
- [ ] Logging configurado
- [ ] Health check endpoint funcionando (`/health`)
- [ ] Scheduler funcionando correctamente
- [ ] Persistencia de datos configurada (volúmenes o base de datos)

### Frontend

- [ ] Build exitoso (`npm run build`)
- [ ] Variables de entorno públicas configuradas
- [ ] API URL correcta
- [ ] CORS permitido desde el dominio del frontend

### Post-Deployment

- [ ] Verificar que el backend responde en `/health`
- [ ] Verificar que el frontend carga correctamente
- [ ] Probar escaneo OSINT manual
- [ ] Verificar conexiones de Composio (si aplica)
- [ ] Monitorear logs para errores

## Variables de Entorno Requeridas

### Backend (.env)
```bash
# API Keys
YOU_API_KEY=tu_you_api_key
OPENAI_API_KEY=tu_openai_api_key
COMPOSIO_API_KEY=tu_composio_api_key  # Opcional

# Configuración
ENVIRONMENT=production
LOG_LEVEL=INFO
SCAN_INTERVAL_MINUTES=15
CACHE_TTL_SECONDS=3600
RISK_THRESHOLD=70
```

### Frontend (.env.local o variables de entorno)
```bash
NEXT_PUBLIC_API_URL=https://tu-backend-url.com
```

## Troubleshooting

### Backend no inicia
- Verifica que todas las variables de entorno estén configuradas
- Revisa los logs: `render logs` o en el dashboard
- Verifica que el puerto sea correcto

### Frontend no conecta con backend
- Verifica `NEXT_PUBLIC_API_URL`
- Verifica CORS en backend (debe permitir el dominio del frontend)
- Revisa la consola del navegador para errores

### Scheduler no funciona
- Verifica que el proceso esté corriendo
- Revisa logs para errores del scheduler
- Verifica que `YOU_API_KEY` sea válida

### Composio no funciona
- Verifica `COMPOSIO_API_KEY`
- Revisa que las conexiones estén activas en Composio dashboard
- Verifica logs del ResearchAgent

## Monitoreo Recomendado

1. **Logs**: Usa el sistema de logs de tu plataforma (Render, Vercel, Railway)
2. **Health Checks**: Configura health checks en `/health`
3. **Alertas**: Configura alertas para errores críticos
4. **Métricas**: Considera usar servicios como Datadog, New Relic, o Sentry

## Costos Estimados

- **Render Free Tier**: $0 (limitado, puede ser lento)
- **Render Starter**: ~$7/mes por servicio
- **Vercel**: Free tier generoso, luego $20/mes
- **Railway**: $5/mes + uso
- **AWS/GCP/Azure**: Pay-as-you-go, puede ser más económico a escala

## Recomendación Final

Para empezar rápido:
1. **Backend**: Render (Free tier o Starter)
2. **Frontend**: Vercel (Free tier)

Para producción:
1. **Backend**: Railway o Render (Starter plan)
2. **Frontend**: Vercel (Pro plan si necesitas más features)

¡Buena suerte con el deployment! 🚀
