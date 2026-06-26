import json
from loader import OpenAPILoader


class OpenAPITools:
    """Implementación de las herramientas MCP para explorar documentación OpenAPI."""

    def __init__(self, loader: OpenAPILoader) -> None:
        self.loader = loader

    async def list_services(self) -> str:
        """Devuelve la lista de microservicios disponibles."""
        services = self.loader.list_services()
        return json.dumps(services, indent=2)

    async def list_endpoints(self, service: str) -> str:
        """Devuelve todos los endpoints de un servicio con método, path y summary."""
        try:
            spec = await self.loader.fetch_spec(service)
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)

        paths = spec.get("paths", {})
        endpoints: list[dict] = []

        for path, methods in paths.items():
            for method, details in methods.items():
                if method in ("parameters",):
                    continue
                endpoints.append({
                    "method": method.upper(),
                    "path": path,
                    "summary": details.get("summary", "")
                })

        return json.dumps(endpoints, indent=2)

    async def get_endpoint(self, service: str, method: str, path: str) -> str:
        """Devuelve la definición completa de un endpoint específico."""
        try:
            spec = await self.loader.fetch_spec(service)
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)

        paths = spec.get("paths", {})
        if path not in paths:
            return json.dumps({"error": f"Path no encontrado: {path}"}, indent=2)

        method_lower = method.lower()
        if method_lower not in paths[path]:
            available = [
                m.upper() for m in paths[path].keys() if m != "parameters"
            ]
            return json.dumps({
                "error": (
                    f"Método '{method}' no encontrado para {path}. "
                    f"Disponibles: {available}"
                )
            }, indent=2)

        return json.dumps(paths[path][method_lower], indent=2)

    async def search(self, query: str) -> str:
        """Busca texto en paths, operationId, summary, description y tags de todos los servicios."""
        query_lower = query.lower()
        results: list[dict] = []

        for service in self.loader.list_services():
            try:
                spec = await self.loader.fetch_spec(service)
            except Exception as e:
                results.append({"service": service, "error": str(e)})
                continue

            paths = spec.get("paths", {})
            for path, methods in paths.items():
                for method, details in methods.items():
                    if method in ("parameters",):
                        continue

                    text_fields = [
                        path,
                        details.get("operationId", ""),
                        details.get("summary", ""),
                        details.get("description", ""),
                    ]

                    tags = details.get("tags", [])
                    if isinstance(tags, list):
                        text_fields.extend(tags)

                    all_text = " ".join(str(f) for f in text_fields).lower()

                    if query_lower in all_text:
                        results.append({
                            "service": service,
                            "method": method.upper(),
                            "path": path,
                            "operationId": details.get("operationId", ""),
                            "summary": details.get("summary", "")
                        })

        return json.dumps(results, indent=2)

    async def get_schema(self, service: str, schema_name: str) -> str:
        """Devuelve la definición de un schema de components.schemas."""
        try:
            spec = await self.loader.fetch_spec(service)
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)

        schemas = spec.get("components", {}).get("schemas", {})
        if schema_name not in schemas:
            available = list(schemas.keys())
            return json.dumps({
                "error": (
                    f"Schema '{schema_name}' no encontrado en '{service}'. "
                    f"Disponibles: {available}"
                )
            }, indent=2)

        return json.dumps(schemas[schema_name], indent=2)
