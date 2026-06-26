from mcp.server.fastmcp import FastMCP
from config import load_services
from loader import OpenAPILoader
from tools import OpenAPITools

services = load_services()
loader = OpenAPILoader(services)
tools = OpenAPITools(loader)

mcp = FastMCP("openapi-mcp")


@mcp.tool()
async def list_services() -> str:
    """Devuelve la lista de microservicios disponibles."""
    return await tools.list_services()


@mcp.tool()
async def list_endpoints(service: str) -> str:
    """Devuelve todos los endpoints de un servicio.

    Args:
        service: Nombre del microservicio
    """
    return await tools.list_endpoints(service)


@mcp.tool()
async def get_endpoint(service: str, method: str, path: str) -> str:
    """Devuelve la definición completa de un endpoint.

    Args:
        service: Nombre del microservicio
        method: Método HTTP (GET, POST, PUT, DELETE, etc.)
        path: Ruta del endpoint
    """
    return await tools.get_endpoint(service, method, path)


@mcp.tool()
async def search(query: str) -> str:
    """Busca texto en la documentación OpenAPI de todos los servicios.

    Busca en paths, operationId, summary, description y tags.

    Args:
        query: Texto a buscar
    """
    return await tools.search(query)


@mcp.tool()
async def get_schema(service: str, schema_name: str) -> str:
    """Devuelve la definición de un schema de components.schemas.

    Args:
        service: Nombre del microservicio
        schema_name: Nombre del schema
    """
    return await tools.get_schema(service, schema_name)


if __name__ == "__main__":
    mcp.run(transport="stdio")
