# OpenAPI MCP Server

Servidor MCP (Model Context Protocol) que permite a un agente consultar la documentación OpenAPI de un backend en tiempo real.

## Requisitos

- Python 3.12+
- Docker

## Instalación

### Con Docker (recomendado)

```bash
cd openapi_mcp
docker build -t openapi-mcp .
```

### Entorno local (alternativa)

```bash
cd openapi_mcp
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuración

### Opción 1: Variable de entorno (más sencilla)

Configura tu backend directamente en el JSON del agente MCP usando la variable `OPENAPI_SERVICES` con formato `nombre:url,nombre2:url`:

```json
{
  "mcpServers": {
    "openapi": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "OPENAPI_SERVICES=mi-backend:http://host.docker.internal:8080/v3/api-docs",
        "openapi-mcp"
      ]
    }
  }
}
```

> Si tu backend está en `localhost`, usa `host.docker.internal` para que el contenedor pueda llegar a él.

Para múltiples backends:

```json
{
  "mcpServers": {
    "openapi": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "OPENAPI_SERVICES=mi-backend:http://host.docker.internal:8080/v3/api-docs,legacy:http://host.docker.internal:8081/v3/api-docs",
        "openapi-mcp"
      ]
    }
  }
}
```

### Opción 2: Archivo YAML (alternativa)

Edita `services.yaml` con la URL de tu backend:

```yaml
services:
  mi-backend: http://localhost:8080/v3/api-docs
```

Y monta el archivo como volumen al ejecutar Docker:

```json
{
  "mcpServers": {
    "openapi": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v",
        "/ruta/absoluta/a/openapi_mcp/services.yaml:/app/services.yaml",
        "openapi-mcp"
      ]
    }
  }
}
```

## Ejecución

### Con Docker

La ejecución va integrada en la configuración del agente. No necesitas ejecutar nada manualmente.

### Entorno local

```bash
python server.py
```

## Cómo funciona

Tu backend expone la especificación OpenAPI en una URL (por ejemplo, `GET /v3/api-docs`). El servidor MCP hace lo siguiente cuando una herramienta es invocada:

1. **Lee la configuración**: `config.py` carga la variable `OPENAPI_SERVICES` o el archivo `services.yaml`.
2. **Descarga la especificación**: `loader.py` hace una petición HTTP `GET` a la URL configurada y recibe el JSON de OpenAPI.
3. **Procesa en memoria**: `tools.py` convierte el JSON en un diccionario de Python y lo consulta directamente.
4. **Sin persistencia**: nunca se guarda el JSON en disco ni se mantiene en caché. Cada llamada descarga la especificación más reciente.

## Registro en Claude Desktop

Edita el archivo de configuración de Claude Desktop:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

Usa la configuración Docker con variable de entorno que aparece arriba en **Opción 1**.

Reinicia Claude Desktop después de guardar la configuración.

## Registro en Claude Code

Claude Code lee la configuración MCP desde `~/.mcp/config.json` o desde archivos `.mcp.json` en el directorio de trabajo.

### Configuración global

Crea `~/.mcp/config.json` con la configuración Docker de **Opción 1**.

### Configuración por proyecto

Crea un archivo `.mcp.json` en la raíz de tu proyecto con la misma configuración.

Claude Code detectará automáticamente el servidor MCP al iniciar.

## Herramientas disponibles

| Herramienta | Descripción |
|-------------|-------------|
| `list_services()` | Lista los backends configurados |
| `list_endpoints(service)` | Lista todos los endpoints de un backend |
| `get_endpoint(service, method, path)` | Devuelve la definición completa de un endpoint |
| `search(query)` | Busca texto en toda la documentación de todos los backends |
| `get_schema(service, schema_name)` | Devuelve la definición de un schema |

## Notas

- **Sin caché**: cada consulta descarga la especificación más reciente.
- **Sin resolución de `$ref`**: los schemas se devuelven tal como aparecen en el OpenAPI.
- **Errores descriptivos**: si un backend no responde, un path no existe o un schema no se encuentra, se devuelve un mensaje de error claro.
# openapi-mcp
