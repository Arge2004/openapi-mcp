import os
import yaml
from pathlib import Path


def load_services(path: str = "services.yaml") -> dict[str, str]:
    """Carga la configuración de servicios desde variable de entorno o archivo YAML."""
    env_services = os.getenv("OPENAPI_SERVICES")
    if env_services:
        services: dict[str, str] = {}
        for entry in env_services.split(","):
            entry = entry.strip()
            if not entry:
                continue
            if ":" not in entry:
                raise ValueError(f"Formato inválido en OPENAPI_SERVICES: {entry}. Esperado nombre:url")
            name, url = entry.split(":", 1)
            services[name.strip()] = url.strip()
        if not services:
            raise ValueError("OPENAPI_SERVICES está vacía o no contiene entradas válidas")
        return services

    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(
            f"Archivo de configuración no encontrado: {path}. "
            "Usa la variable de entorno OPENAPI_SERVICES con formato nombre:url,nombre2:url"
        )

    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    services = data.get("services", {})
    if not services:
        raise ValueError("No se encontraron servicios en la configuración")

    return services
