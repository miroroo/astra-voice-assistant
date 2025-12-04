from .module import Module

class IntroducingModule(Module):
    def __init__(self, astra_manager):
        super().__init__(astra_manager)
        self.system_name = "Астра"
        self.version = "1.3"
        # self.greeting_phrases = ["привет", "здравствуй", "добрый день", "доброе утро", "добрый вечер"]
        self.about_phrases = ["кто ты", "расскажи о себе", "что ты умеешь", "твои возможности"]

        self.event_bus = self.astra_manager.get_event_bus()
        self.event_bus.subscribe("context_cleared", self.on_context_cleared)
    
    async def on_context_cleared(self, module_name: str):
        if module_name == self.get_name():
            pass

    async def can_handle(self, command: str) -> bool:
        """Проверяет, может ли модуль обработать команду представления или приветствия."""
        return any(phrase in command for phrase in  self.about_phrases)

    async def execute(self, command: str) -> str:
        """Выполняет обработку команды представления или приветствия."""
        
        return (f"Я голосовой ассистент {self.system_name} версии {self.version}. "
                    "Я могу отвечать на вопросы, выполнять команды и помогать с различными задачами.")
        