from sys import stderr
from importlib import import_module
from pathlib import Path

from . import base

SERVICES = []

this_folder = Path(__file__).parent
for service in this_folder.iterdir():
    if service.name.startswith("__") or service.name == 'base':
        print("Skipped " + service.name)
        continue
    try:
        module = import_module(
            f"core.services.{service.name.replace('.py', '')}")
    except ImportError:
        print(f"In module {service.name} not found the service", file=stderr)
        continue
    if all([
            hasattr(module, "is_enabled") and module.is_enabled,
            hasattr(module, "service") and isinstance(
                module.service, base.BaseService),
    ]):
        SERVICES.append(module.service)
        print(f"Service {service.name!r} is loaded and enabled")
    else:
        print(f"Service {service.name!r} is disabled", file=stderr)
