from .module import Module

class SleepModule(Module):
    """Модуль для перевода ассистента в режим сна."""
    
    def __init__(self, astra_manager):
        super().__init__(astra_manager)
        self.sleep_commands = [
            "выключись", "отключись", "заверши работу", "закройся", 
            "стоп", "остановись", "спокойной ночи", "добройн ночи", "усни", "перейди в режим сна"
        ]
        
        self.module_name = self.get_name()
        self.event_bus = self.astra_manager.get_event_bus()
        self.state_manager = self.astra_manager.get_state_manager()
        self.event_bus.subscribe("context_cleared", self.on_context_cleared)
    
    async def on_context_cleared(self, module_name: str):
        pass

    async def can_handle(self, command: str) -> bool: 
        if any(cmd in command for cmd in self.sleep_commands):
            self.state_manager.set_active_context(
                self.module_name, 
                priority=25,  # Высокий приоритет для системных команд
                context_type="system",
                timeout_seconds=300  # 5 минут
            )
            return True
        return False
    
    async def execute(self, command: str) -> str:
        # Отправляем событие запроса сна
        await self.event_bus.publish_async("sleep_requested")
        return "Выключаюсь"
            
