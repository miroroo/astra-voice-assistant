import asyncio
from typing import Dict, List, Callable, Any
                 
class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_history: List[Dict[str, Any]] = []  # История событий для отладки
        self._max_history = 100  # Максимальное количество событий в истории

    def subscribe(self, event_type: str, callback: Callable):

    
        if not callable(callback):
            print(f"[ERROR] Callback для события '{event_type}' не является вызываемым! Тип: {type(callback)}")
            raise TypeError(f"Callback must be callable, got {type(callback)}")
    
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)


    def unsubscribe(self, event_type: str, callback: Callable):
        """Отписаться от события"""
        if event_type in self._subscribers:
            if callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)

    async def publish_async(self, event_type: str, *args, **kwargs):
        """Асинхронная публикация события"""

        self._event_history.append({
            "type": event_type,
            "timestamp": asyncio.get_event_loop().time(),
            "args": args,
            "kwargs": kwargs
        })

        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)

        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(*args, **kwargs)
                    else:
                        loop = asyncio.get_event_loop()
                        await loop.run_in_executor(None, callback, *args, **kwargs)
                except Exception as e:
                    print(f"Ошибка в обработчике {event_type}: {e}")

    def publish(self, event_type: str, *args, **kwargs):
        """Синхронная публикация события (для случаев когда нельзя использовать await)"""
        asyncio.create_task(self.publish_async(event_type, *args, **kwargs))

    def get_subscribers_count(self, event_type: str = None) -> int:
        """Получить количество подписчиков"""
        if event_type:
            return len(self._subscribers.get(event_type, []))
        return sum(len(subscribers) for subscribers in self._subscribers.values())

    def get_event_history(self, limit: int = 10) -> List[Dict]:
        """Получить историю событий"""
        return self._event_history[-limit:] if self._event_history else []

    def clear_history(self):
        """Очистить историю событий"""
        self._event_history.clear()
