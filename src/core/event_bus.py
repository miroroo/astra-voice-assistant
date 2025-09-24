import asyncio
from typing import Dict, List, Callable
                 
class EventBus:
    def __init__(self):
        """Метод инициализирует словарь, где ключ - тип события, 
        а значения - список запросов"""
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable):
        """Метод добавляет запрос в список, если такого состояния нет.
        Args:
            event_type (str): тип состояния
            callback (Callable): запрос
        """
        if event_type not in self._subscribers:
            # проверка, есть ли такое состояние в словаре
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    async def publish_async(self, event_type: str, *args, **kwargs):
        """Метод выполняет запрос в отдельном потоке
        Args:
            event_type (str): тип события
            *args: аргументы запроса
            **kwargs: аргументы аргументов запроса
        """

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
