import asyncio
from typing import Dict, List, Callable
                 
class EventBus():
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        # инициализируем словарь, где ключ - тип события, а значения - список запросов

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self._subscribers:
            # проверка, есть ли такое состояние в словаре
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    async def publish_async(self, event_type: str, *args, **kwargs):
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        # Если обработчик асинхронный
                        await callback(*args, **kwargs)
                    else:
                        # Если синхронный - запускаем в отдельном потоке
                        loop = asyncio.get_event_loop()
                        await loop.run_in_executor(
                            None, callback, *args, **kwargs)
                except Exception as e:
                    print(f"Ошибка в обработчике {event_type}: {e}")
