from abc import ABC, abstractmethod

class Module(ABC):
    """Абстрактный базовый класс для всех модулей."""
    
    def __init__(self, astra_manager):
        self.astra_manager = astra_manager
    
    @abstractmethod
    async def can_handle(self, command: str) -> bool:
        pass
    
    @abstractmethod
    async def execute(self, command: str) -> str:
        pass

    def get_name(self) -> str:
        """Возвращает имя модуля. По умолчанию используется имя класса."""
        return self.__class__.__name__
    
         