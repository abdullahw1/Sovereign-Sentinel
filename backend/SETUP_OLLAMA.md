# Setup de Ollama (Modelo Open Source)

## Instalación

### macOS
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Windows
Descargar desde: https://ollama.ai/download

## Descargar Modelos

```bash
# Opción 1: LLaMA 2 (7B - más rápido)
ollama pull llama2

# Opción 2: LLaMA 2 (13B - mejor calidad)
ollama pull llama2:13b

# Opción 3: Mistral (7B - muy eficiente)
ollama pull mistral

# Opción 4: Mistral (7B específico)
ollama pull mistral:7b
```

## Verificar Instalación

```bash
# Verificar que Ollama está corriendo
ollama list

# Probar modelo
ollama run llama2 "Hello, how are you?"
```

## Configuración en la Aplicación

El servidor Ollama corre en `http://localhost:11434` por defecto.

En el archivo `.env`, configura:
```
OLLAMA_MODEL=llama2
OLLAMA_BASE_URL=http://localhost:11434
```

## Notas

- El primer uso del modelo puede tardar mientras se descarga
- Los modelos ocupan espacio en disco (7B ~4GB, 13B ~7GB)
- Para producción, considera usar un servidor Ollama dedicado
