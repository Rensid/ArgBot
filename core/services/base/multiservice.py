from pathlib import Path
from typing import List

from core.services.base.types import BaseService
from logs.logs import log_decorator


class MultipleServices(BaseService):
    services: List[BaseService]

    def __init__(self, name: str, category: str, *args: BaseService):
        self.name = name
        self.category = category
        super().__init__()
        self.services: List[BaseService] = list(args)
        self.parameters = []
        for ServiceType in self.services:
            self.parameters += ServiceType.parameters

    @log_decorator
    def init(self, **kwargs):
        self.query = kwargs

    @log_decorator
    def run(self) -> List[Path]:
        files = []
        for service in self.services:
            service.init(**self.query)
            files.append(service.run())
        return files
