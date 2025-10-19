from src.core.core import Core
from src.core.state_manager import StateManager
from src.core.event_bus import EventBus
from src.modules.module_manager import ModuleManager
from src.modules.registry import register_all_modules


class AstraManager:
    """Центральный координатор системы."""
    
    def __init__(self):
        # Инициализируем компоненты ядра
        self.event_bus = EventBus()
        self.state_manager = StateManager(self.event_bus)
        self.module_manager = ModuleManager(self)
        
        # Создаем ядро
        self.core = Core(self)
        
        # Регистрируем модули
        register_all_modules(self)
        
        print("[AstraManager] Инициализирован")

    async def process_command(self, user_id: str, command: str) -> str:
        """Обработка команды через менеджер модулей"""
        return await self.module_manager.execute_command(command)
    
    async def start(self):
        """Запустить Астру."""
        await self.core.start()
    
    async def stop(self):
        """Остановить Астру."""
        await self.core.shutdown()
    
    async def force_state_change(self, new_state: str):
        """Принудительно сменить состояние (для тестирования)"""
        try:
            await self.state_manager.change_state(new_state)
        except ValueError as e:
            print(f"Ошибка: {e}")
    
    def get_state(self) -> str:
        """Получить текущее состояние."""
        return self.state_manager.get_state()
    
    # Геттеры для внутреннего использования компонентами
    def get_state_manager(self):
        return self.state_manager
    
    def get_event_bus(self):
        return self.event_bus
    
    def get_module_manager(self):
        return self.module_manager  
    
    def get_voice_module(self):
        return self.voice_module