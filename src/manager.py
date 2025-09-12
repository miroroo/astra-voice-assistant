from .core.core import Core

class AstraManager:
    
    def __init__(self):
        self.core = Core()
        # инициализируем ядро
    
    def start(self):
        """Запустить Астру."""
        self.core.start()
    
    def stop(self):
        """Остановить Астру."""
        self.core.shutdown()
    
    async def force_state_change(self, new_state: str):
        """Принудительно сменить состояние (для тестирования)."""
        try:
            await self.core.state_manager.change_state(new_state)
        except ValueError as e:
            print(f"Ошибка: {e}")
    
    def get_state(self) -> str:
        """Получить текущее состояние."""
        return self.core.state_manager.get_state()
