from .module import Module

class IntroducingModule(Module):
    def __init__(self, astra_manager):
        super().__init__(astra_manager)
        self.system_name = "Астра"
        self.version = "1.3"
        self.greeting_phrases = ["привет", "здравствуй", "добрый день", "доброе утро", "добрый вечер"]
        self.about_phrases = ["кто ты", "расскажи о себе", "что ты умеешь", "твои возможности"]

    async def can_handle(self, command: str) -> bool:
        """Проверяет, может ли модуль обработать команду представления или приветствия."""
        normalized_command = command.lower()
        return any(phrase in normalized_command for phrase in self.greeting_phrases + self.about_phrases)

    async def execute(self, command: str) -> str:
        """Выполняет обработку команды представления или приветствия."""
        normalized_command = command.lower()
        
        if any(phrase in normalized_command for phrase in self.greeting_phrases):
            return f"Привет! Я {self.system_name}, ваша голосовая ассистентка. Чем могу помочь?"
        
        if any(phrase in normalized_command for phrase in self.about_phrases):
            return (f"Я голосовой ассистент {self.system_name} версии {self.version}. "
                    "Я могу отвечать на вопросы, выполнять команды и помогать с различными задачами.")
        
        return f"{self.system_name}: Рада вас слышать! Чем могу помочь?"