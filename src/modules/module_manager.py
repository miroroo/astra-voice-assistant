import logging
from typing import List
from src.modules.module import Module
import random

class ModuleManager:
    """Менеджер модулей с приоритетной системой выполнения и улучшенной работой с контекстами."""
    
    def __init__(self, astra_manager):
        self.astra_manager = astra_manager
        self.logger = logging.getLogger(__name__)
        self.modules: List[Module] = []
        
        self.fallback_phrases = [
            "Извините, не понял команду",
            "Попробуйте сказать по-другому",
            "Не совсем понимаю, что вы имеете в виду",
            "Можете повторить команду?",
            "Я пока не умею это делать",
        ]

    def register_module(self, module: Module):
        """Регистрирует модуль в менеджере."""
        self.modules.append(module)
        
        # Подписываем модуль на события очистки контекста
        event_bus = self.astra_manager.get_event_bus()
        if hasattr(module, 'on_context_cleared'):
            event_bus.subscribe("context_cleared", module.on_context_cleared)
            

    async def execute_command(self, command: str) -> str:
        """Выполняет команду с учётом приоритетов модулей и контекстов."""
        self.logger.info(f"[ModuleManager] Обработка: {command}")
        
        #Получаем модули с активными контекстами (отсортированные по приоритету)
        context_modules = self._get_context_modules()
        
        #Сначала даем шанс модулям с контекстом обработать команду
        for module in context_modules:
            try:
                if await module.can_handle(command):
                    result = await module.execute(command)
                    return result
            except Exception as e:
                self.logger.critical(f"[ModuleManager] Ошибка в модуле {module.get_name()}: {e}")
                continue
        
        #Если модули с контекстом не обработали, проверяем все модули
        for module in self.modules:
            # Пропускаем модули, которые уже проверялись в контексте
            if module in context_modules:
                continue  
            try:
                if await module.can_handle(command):
                    result = await module.execute(command)
                    return result
            except Exception as e:
                self.logger.critical(f"[ModuleManager] Ошибка в модуле {module.get_name()}: {e}")
                continue
        
        #Если ничего не найдено, возвращаем случайную фразу из fallback
        return self._get_fallback_response()

    def _get_context_modules(self) -> List[Module]:
        """Возвращает модули с активными контекстами, отсортированные по приоритету."""
        state_manager = self.astra_manager.get_state_manager()
        active_contexts = state_manager.get_active_contexts()
        
        #Создаем список кортежей (приоритет, модуль)
        prioritized_modules = []
        for module in self.modules:
            module_name = module.get_name()
            priority = active_contexts.get(module_name, 0)
            if priority > 0:
                prioritized_modules.append((priority, module))
        
        #Сортируем по приоритету (убывание)
        prioritized_modules.sort(key=lambda x: x[0], reverse=True)
        return [module for _, module in prioritized_modules]

    def _is_fallback_response(self, response: str) -> bool:
        """Проверяет, является ли ответ fallback-ом (неудачной обработкой)."""
        if not response or not response.strip():
            return True
        
        response_lower = response.lower().strip()
        
        #Проверяем явные фразы-индикаторы продолжения диалога
        continuation_phrases = [
            "на какое время",
            "не понял время",
            "повторите",
            "уточните",
            "скажите",
            "какое",
            "какую"
        ]
        
        if any(phrase in response_lower for phrase in continuation_phrases):
            return False
        
        fallback_indicators = [
            "не понял",
            "не могу распознать", 
            "извините",
            "не знаю",
            "не умею"
        ]
        
        return any(phrase in response_lower for phrase in fallback_indicators)

    def _get_fallback_response(self) -> str:
        """Возвращает случайную fallback-фразу."""
        return random.choice(self.fallback_phrases)




