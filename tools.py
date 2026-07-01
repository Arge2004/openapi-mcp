import json
from loader import OpenAPILoader


def _strip_docs(obj):
    if isinstance(obj, dict):
        return {k: _strip_docs(v) for k, v in obj.items() if k not in ("description", "example", "examples")}
    if isinstance(obj, list):
        return [_strip_docs(item) for item in obj]
    return obj


class OpenAPITools:

    def __init__(self, loader: OpenAPILoader) -> None:
        self.loader = loader

    async def list_endpoints(self, service: str) -> str:
        try:
            spec = await self.loader.fetch_spec(service)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

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

        return json.dumps(endpoints, ensure_ascii=False)

    async def get_endpoint(self, service: str, method: str, path: str) -> str:
        try:
            spec = await self.loader.fetch_spec(service)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

        paths = spec.get("paths", {})
        if path not in paths:
            return json.dumps({"error": f"Path no encontrado: {path}"}, ensure_ascii=False)

        method_lower = method.lower()
        if method_lower not in paths[path]:
            available = [m.upper() for m in paths[path].keys() if m != "parameters"]
            return json.dumps({
                "error": f"Metodo '{method}' no encontrado para {path}. Disponibles: {available}"
            }, ensure_ascii=False)

        return json.dumps(_strip_docs(paths[path][method_lower]), ensure_ascii=False)

    async def search(self, query: str) -> str:
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

        return json.dumps(results, ensure_ascii=False)

    async def get_schema(self, service: str, schema_name: str) -> str:
        try:
            spec = await self.loader.fetch_spec(service)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

        schemas = spec.get("components", {}).get("schemas", {})
        if schema_name not in schemas:
            available = list(schemas.keys())
            return json.dumps({
                "error": f"Schema '{schema_name}' no encontrado en '{service}'. Disponibles: {available}"
            }, ensure_ascii=False)

        return json.dumps(_strip_docs(schemas[schema_name]), ensure_ascii=False)
