import httpx


class OpenAPILoader:
    """Descarga especificaciones OpenAPI desde los microservicios configurados."""

    def __init__(self, services: dict[str, str]) -> None:
        self.services = services

    async def fetch_spec(self, service: str) -> dict:
        """Obtiene la especificación OpenAPI de un servicio en tiempo real."""
        if service not in self.services:
            raise ValueError(f"Servicio no encontrado: {service}")

        url = self.services[service]
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except httpx.ConnectError as e:
            raise ConnectionError(
                f"No se pudo conectar al servicio '{service}' en {url}: {e}"
            )
        except httpx.HTTPStatusError as e:
            raise RuntimeError(
                f"El servicio '{service}' respondió con error HTTP {e.response.status_code}"
            )
        except Exception as e:
            raise RuntimeError(
                f"Error al obtener la especificación de '{service}': {e}"
            )

    def list_services(self) -> list[str]:
        """Devuelve la lista de nombres de servicios configurados."""
        return list(self.services.keys())
