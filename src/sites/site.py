from abc import abstractmethod, ABC
from dataclasses import dataclass

from playwright.async_api import Page

@dataclass
class Site(ABC):
    data: dict

    @abstractmethod
    async def validate_type(self, page: Page):
        pass

    @abstractmethod
    async def process(self, page: Page):
        pass
