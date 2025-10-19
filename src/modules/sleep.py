from .module import Module

class SleepModule(Module):
    """Модуль для перевода ассистента в режим сна."""
    
    def __init__(self, astra_manager):
        super().__init__(astra_manager)
        
        # Подписываемся на события очистки контекста
        event_bus = self.get_event_bus()
        event_bus.subscribe("context_cleared", self.on_context_cleared)
    
    async def on_context_cleared(self, module_name: str):
        if module_name == self.get_name():
            pass

    async def can_handle(self, command: str) -> bool:
        sleep_commands = [
            "выключись", "отключись", "заверши работу", "закройся", 
            "стоп", "остановись", "спокойной ночи", "усни", "перейди в режим сна"
        ]
        normalized_command = command.lower()
        
        return any(cmd in normalized_command for cmd in sleep_commands)

    async def execute(self, command: str) -> str:
        event_bus = self.get_event_bus()
        
        # Отправляем событие запроса сна
        await event_bus.publish_async("sleep_requested")
        return "Перехожу в режим сна. Скажите 'бот' чтобы разбудить."
            
