from src.core.core import Core

class AstraManager:
    
    def __init__(self):
        self.core = Core()
        # инициализируем ядро
    
    async def start(self):
        """Запустить Астру."""
        await self.core.start()
    
    async def stop(self):
        """Остановить Астру."""
        await self.core.shutdown()
    
    async def force_state_change(self, new_state: str):
        """Принудительно сменить состояние (для тестирования)
        Args:
            new_state (str): Новое состояние
        """
        try:
            await self.core.state_manager.change_state(new_state)
        except ValueError as e:
            print(f"Ошибка: {e}")
    
    def get_state(self) -> str:
        """Получить текущее состояние.
        Returns:
            bool: Состояние ядра на момент запроса
        """
        
        return self.core.state_manager.get_state()
