import asyncio
from src.core.event_bus import EventBus
import time
from typing import Dict, Any, Optional

class StateManager:
    """Управление конечным автоматом (FSM) состояний и контекстов."""
    
    # Определение состояний
    SLEEP = "SLEEP"
    LISTENING = "LISTENING" 
    PROCESSING = "PROCESSING"
    
    def __init__(self, event_bus: EventBus):
        self.current_state = self.SLEEP
        self.event_bus = event_bus
        
        self._transitions = {
            self.SLEEP: [self.LISTENING, self.SLEEP],
            self.LISTENING: [self.PROCESSING, self.SLEEP],
            self.PROCESSING: [self.LISTENING, self.SLEEP],
        }

        # Новая структура контекстов
        self._active_contexts: Dict[str, int] = {}  # module_name -> priority
        self._module_data: Dict[str, Dict[str, Any]] = {}  # module_name -> {data}
        self._context_timestamps: Dict[str, float] = {}  # module_name -> last_activity
        self._context_timeouts: Dict[str, int] = {}  # module_name -> timeout_seconds
        
        # Настройки таймаутов по умолчанию
        self.DEFAULT_CONTEXT_TIMEOUT = 2 * 60 * 60  # 2 часа в секундах
        self.SHORT_CONTEXT_TIMEOUT = 10 * 60  # 10 минут для кратковременных диалогов
    
    def can_transition_to(self, new_state: str) -> bool:
        """Метод проверки возможности перехода между состояниями.
        Args:
            new_state (str): Новое состояние
        Returns:
            bool: True если переход возможен
        """
        return new_state in self._transitions.get(self.current_state, [])
        # если новое состояние удовлетворяем правилам перехода, то возвращаем True
    
    async def change_state(self, new_state: str):
        """Метод смены состояния
        Args:
            new_state (str): Новое состояние
        """

        if not self.can_transition_to(new_state):
            raise ValueError(f"Невозможно перейти из {self.current_state} в {new_state}")
        
        old_state = self.current_state
        self.current_state = new_state

        # вывод в терминал перехода
        print(f"[StateManager] {old_state} → {new_state}")
        
        # Публикуем события о выходе из старого статуса, о входе в новый статус, о смене статуса
        await self.event_bus.publish_async(f"state_{old_state}_exit")
        await self.event_bus.publish_async(f"state_{new_state}_enter")
        await self.event_bus.publish_async("state_changed", old_state, new_state)
        

    def get_state(self) -> str:
        """Получить текущее состояние.
        Returns:
            bool: Состояние ядра на момент запроса
        """
        return self.current_state

    def set_active_context(self, module_name: str, priority: int = 10, 
                          timeout_seconds: Optional[int] = None) -> None:
        """Устанавливает активный контекст для модуля с приоритетом и таймаутом."""
        self._active_contexts[module_name] = priority
        self._context_timestamps[module_name] = time.time()
        
        # Устанавливаем таймаут
        if timeout_seconds is not None:
            self._context_timeouts[module_name] = timeout_seconds
        else:
            # Автоматический выбор таймаута на основе приоритета
            self._context_timeouts[module_name] = (
                self.SHORT_CONTEXT_TIMEOUT if priority >= 10 else self.DEFAULT_CONTEXT_TIMEOUT
            )
            

    def get_active_contexts(self) -> Dict[str, int]:
        """Возвращает все активные контексты с приоритетами."""
        self._clean_expired_contexts()
        return self._active_contexts.copy()

    def get_module_priority(self, module_name: str) -> int:
        """Получает приоритет модуля."""
        self._clean_expired_contexts()
        return self._active_contexts.get(module_name, 0)

    def set_module_data(self, module_name: str, key: str, value: Any) -> None:
        """Устанавливает данные для модуля."""
        if module_name not in self._module_data:
            self._module_data[module_name] = {}
        self._module_data[module_name][key] = value

    def get_module_data(self, module_name: str, key: str = None) -> Any:
        """Получает данные модуля."""
        if module_name not in self._module_data:
            return None
        if key:
            return self._module_data[module_name].get(key)
        return self._module_data[module_name].copy()

    def clear_module_data(self, module_name: str = None, key: str = None) -> None:
        """Очищает данные модуля."""
        if module_name and key:
            self._module_data.get(module_name, {}).pop(key, None)
        elif module_name:
            self._module_data.pop(module_name, None)
        else:
            self._module_data.clear()

    def clear_active_context(self, module_name: str = None) -> None:
        """Очищает активные контексты."""
        if module_name:
            self._publish_context_cleared(module_name)
            self._active_contexts.pop(module_name, None)
            self._context_timestamps.pop(module_name, None)
            self._context_timeouts.pop(module_name, None)
        else:
            # Публикуем события для всех модулей
            for module_name in list(self._active_contexts.keys()):
                self._publish_context_cleared(module_name)
                
            self._active_contexts.clear()
            self._context_timestamps.clear()
            self._context_timeouts.clear()

    def clear_all_contexts(self) -> None:
        """Очищает все контексты и данные."""
        self.clear_active_context()
        self._module_data.clear()
        print("[StateManager] Все контексты очищены")

    def _clean_expired_contexts(self) -> None:
        """Очищает просроченные контексты."""
        current_time = time.time()
        expired_modules = []
        
        for module_name, timestamp in self._context_timestamps.items():
            timeout = self._context_timeouts.get(module_name, self.DEFAULT_CONTEXT_TIMEOUT)
            if current_time - timestamp > timeout:
                expired_modules.append(module_name)
        
        for module_name in expired_modules:
            self._publish_context_cleared(module_name)
            self._active_contexts.pop(module_name, None)
            self._module_data.pop(module_name, None)
            self._context_timestamps.pop(module_name, None)
            self._context_timeouts.pop(module_name, None)

    def _publish_context_cleared(self, module_name: str) -> None:
        """Публикует событие очистки контекста."""
        asyncio.create_task(self._async_publish_context_cleared(module_name))
    
    async def _async_publish_context_cleared(self, module_name: str) -> None:
        """Асинхронно публикует событие очистки контекста."""
        await self.event_bus.publish_async("context_cleared", module_name)

    def get_context_info(self, module_name: str) -> Dict[str, Any]:
        """Возвращает информацию о контексте модуля (для отладки)."""
        if module_name not in self._active_contexts:
            return {}
            
        return {
            "priority": self._active_contexts[module_name],
            "last_activity": self._context_timestamps[module_name],
            "timeout": self._context_timeouts.get(module_name, self.DEFAULT_CONTEXT_TIMEOUT),
            "time_remaining": self._context_timeouts.get(module_name, self.DEFAULT_CONTEXT_TIMEOUT) - 
                             (time.time() - self._context_timestamps[module_name]),
            "data": self._module_data.get(module_name, {})
        }