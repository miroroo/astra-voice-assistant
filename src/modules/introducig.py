from src.modules.module import Module


class IntroducingModule(Module):
    """Модуль для представления системы и ответов на вопросы о себе."""
    
    def __init__(self, system_name: str = "Астра", version: str = "1.0"):
        """Инициализирует модуль представления с настраиваемыми параметрами системы.
        
        Args:
            system_name (str): Название системы для представления
            version (str): Версия системы для отображения
        """
        self.system_name = system_name
        self.version = version
        self.greeting_phrases = [
            "привет", "здравствуй", "добрый день", "доброе утро", "добрый вечер"
        ]
        self.about_phrases = [
            "кто ты", "расскажи о себе", "что ты умеешь", "твои возможности"
        ]

    async def can_handle(self, command: str) -> bool:
        """Проверяет, может ли модуль обработать команду представления или приветствия.
        
        Args:
            command (str): Команда для проверки
            
        Returns:
            bool: True если команда относится к представлению или приветствию
        """
        normalized_command = command.lower()
        
        # Проверяем приветственные фразы
        if any(phrase in normalized_command for phrase in self.greeting_phrases):
            return True
            
        # Проверяем вопросы о системе
        if any(phrase in normalized_command for phrase in self.about_phrases):
            return True
            
        # Проверяем прямые команды представления
        if "представься" in normalized_command or "назови себя" in normalized_command:
            return True
            
        return False

    async def execute(self, command: str) -> str:
        """Выполняет обработку команды представления или приветствия.
        
        Args:
            command (str): Команда для обработки
            
        Returns:
            str: Ответ системы с представлением или описанием возможностей
        """
        normalized_command = command.lower()
        
        # Обработка приветствий
        if any(phrase in normalized_command for phrase in self.greeting_phrases):
            return f"{self.system_name}: Привет! Я {self.system_name}, ваша голосовая ассистентка. Чем могу помочь?"
        
        # Обработка запроса о представлении
        if "представься" in normalized_command or "назови себя" in normalized_command:
            return f"Я {self.system_name}, версия {self.version}. Голосовой ассистент для решения ваших задач."
        
        # Обработка вопросов о системе
        if any(phrase in normalized_command for phrase in self.about_phrases):
            return (f"{self.system_name}: Я голосовой ассистент {self.system_name} версии {self.version}. "
                    "Я могу отвечать на вопросы, выполнять команды и помогать с различными задачами. "
                    "Спросите меня о чем-нибудь, и я постараюсь помочь!")
        
        # Запасной ответ
        return f"{self.system_name}: Рада вас слышать! Чем могу помочь?"