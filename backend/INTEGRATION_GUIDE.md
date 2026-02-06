# Guía de Integración: Research Agent y Financial Analysis Agent

## Resumen

Se han agregado dos nuevos agentes al sistema Sovereign Sentinel:

1. **Research Agent**: Extrae datos financieros de Xero, QuickBooks y Stripe usando Composio MCP
2. **Financial Analysis Agent**: Analiza préstamos usando modelos open source (Ollama/LLaMA 2)

## Configuración

### 1. Variables de Entorno

Agrega a tu archivo `.env`:

```bash
# Composio API Key (obtener en https://composio.dev)
COMPOSIO_API_KEY=your_composio_api_key_here

# Ollama Settings (opcional, defaults aplicados)
OLLAMA_MODEL=llama2
OLLAMA_BASE_URL=http://localhost:11434
```

### 2. Instalar Dependencias

```bash
cd backend
pip install -r requirements.txt
```

### 3. Instalar Ollama (para Financial Analysis Agent)

Ver `SETUP_OLLAMA.md` para instrucciones detalladas.

Resumen rápido:
```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Descargar modelo
ollama pull llama2
```

## Nuevos Endpoints API

### 1. Extraer Datos Financieros

**POST** `/api/research/extract`

Extrae datos de préstamos desde una fuente externa.

**Body (JSON):**
```json
{
  "source": "xero",  // "xero" | "quickbooks" | "stripe"
  "connection_id": "conn_123",
  "tenant_id": "tenant_456"  // Requerido para Xero y QuickBooks
}
```

**Response:**
```json
{
  "source": "xero",
  "loans": [
    {
      "loanId": "XERO_123_456",
      "borrower": "Acme Corp",
      "industry": "energy",
      "interestType": "PIK",
      "principalAmount": 10000000,
      "outstandingBalance": 12500000,
      "maturityDate": "2025-12-31T00:00:00Z",
      "covenants": []
    }
  ],
  "count": 1,
  "status": "success"
}
```

### 2. Analizar Portafolio

**POST** `/api/analysis/analyze`

Analiza un portafolio de préstamos usando AI o método tradicional.

**Body (JSON):**
```json
{
  "loans": [
    {
      "loanId": "L001",
      "borrower": "Acme Energy",
      "industry": "energy",
      "interestType": "PIK",
      "principalAmount": 10000000,
      "outstandingBalance": 12500000,
      "maturityDate": "2025-12-31T00:00:00Z",
      "covenants": []
    }
  ],
  "use_ai": true  // true = usa Ollama, false = usa Forensic Auditor tradicional
}
```

**Response:**
```json
{
  "total_loans": 1,
  "flagged_count": 1,
  "analysis_method": "ai",
  "flagged_loans": [
    {
      "loanId": "L001",
      "borrower": "Acme Energy",
      "risk_level": "critical",
      "flag_reason": "PIK loan in high-risk sector",
      "correlated_event": "Current geopolitical events",
      "flagged_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### 3. Extraer y Analizar (Combinado)

**POST** `/api/research/analyze-and-extract`

Extrae datos y los analiza en un solo paso.

**Body (JSON):**
```json
{
  "source": "quickbooks",
  "connection_id": "conn_123",
  "tenant_id": "company_456",
  "use_ai": true
}
```

**Response:**
```json
{
  "source": "quickbooks",
  "extracted_count": 5,
  "flagged_count": 2,
  "analysis_method": "ai",
  "flagged_loans": [...]
}
```

## Flujo de Trabajo Recomendado

### Opción 1: Extracción y Análisis Separados

```python
import requests

# 1. Extraer datos
response = requests.post(
    "http://localhost:8000/api/research/extract",
    json={
        "source": "xero",
        "connection_id": "your_connection_id",
        "tenant_id": "your_tenant_id"
    }
)
loans_data = response.json()["loans"]

# 2. Analizar
analysis_response = requests.post(
    "http://localhost:8000/api/analysis/analyze",
    json={
        "loans": loans_data,
        "use_ai": True
    }
)
flagged = analysis_response.json()["flagged_loans"]
```

### Opción 2: Todo en Uno

```python
import requests

response = requests.post(
    "http://localhost:8000/api/research/analyze-and-extract",
    json={
        "source": "quickbooks",
        "connection_id": "your_connection_id",
        "tenant_id": "your_company_id",
        "use_ai": True
    }
)
results = response.json()
```

## Configuración de Composio

### 1. Obtener API Key

1. Registrarse en https://composio.dev
2. Obtener API key desde el dashboard
3. Agregar a `.env`: `COMPOSIO_API_KEY=your_key`

### 2. Conectar Aplicaciones

Para conectar Xero, QuickBooks o Stripe:

1. Usar el SDK de Composio para crear conexiones OAuth
2. O usar el dashboard de Composio para conectar manualmente
3. Obtener `connection_id` después de conectar

**Ejemplo de conexión (usando Composio SDK):**
```python
from composio import ComposioClient

client = ComposioClient(api_key="your_key")
connection = client.connect_app(
    app="xero",
    entity_id="your_entity_id"
)
connection_id = connection.id
```

## Troubleshooting

### Error: "Research Agent not initialized"
- Verifica que `COMPOSIO_API_KEY` esté en `.env`
- Reinicia el servidor después de agregar la variable

### Error: "Failed to initialize Ollama"
- Verifica que Ollama esté corriendo: `ollama list`
- Verifica que el modelo esté descargado: `ollama pull llama2`
- Verifica `OLLAMA_BASE_URL` en `.env`

### Error: "Composio is not installed"
```bash
pip install composio-core
```

### Error: "LangChain not available"
```bash
pip install langchain langchain-community
```

## Notas

- El Research Agent requiere conexiones OAuth activas para cada fuente
- El Financial Analysis Agent usa fallback si Ollama no está disponible
- Los análisis con AI pueden ser más lentos que el método tradicional
- Para producción, considera usar un servidor Ollama dedicado
