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
    
    async def on_context_cleared(self, module_name: str):
        """Вызывается при очистке контекста модуля. Может быть переопределен."""
        pass
    
    def get_name(self) -> str:
        """Возвращает имя модуля. По умолчанию используется имя класса."""
        return self.__class__.__name__
    
    # Вспомогательные методы для доступа к компонентам
    def get_state_manager(self):
        return self.astra_manager.get_state_manager()
    
    def get_event_bus(self):
        return self.astra_manager.get_event_bus()