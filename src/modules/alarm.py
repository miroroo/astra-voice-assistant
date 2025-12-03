# import logging
# import asyncio
# from datetime import datetime
# from typing import Optional

# from src.modules.module import Module
# from src.modules.parse_time import TimeParser

# class AlarmModule(Module):
#     def __init__(self, astra_manager):
#         super().__init__(astra_manager)
#         self.active_alarms = []
#         self.state_manager = astra_manager.get_state_manager()
#         self.event_bus = astra_manager.get_event_bus()
#         self.logger = logging.getLogger(__name__)
#         self.time_parser = TimeParser()
    
#     async def on_context_cleared(self, module_name=None):
#         """Обработчик очистки контекста."""
#         self.state_manager.clear_active_context(self.get_name())
        
#     async def can_handle(self, command: str) -> bool:

#         if self.state_manager.get_module_priority(self.get_name()) > 0:
#             if self.time_parser.extract_time(command):
#                 return True

#         alarm_keywords = [
#             "будильник", "разбуди", "напомни", "таймер", 
#             "отмени", "стоп", "список", "какие", "какой",
#             "поставь", "установи", "создай"
#         ]
        
#         return any(cmd in command for cmd in alarm_keywords)
    
#     async def execute(self, command: str) -> str:
#         command_lower = command.lower()
        
#         # Обработка команд отмены и показа списка (работают всегда)
#         if any(cmd in command_lower for cmd in ["отмени", "удали", "стоп", "отмена"]):
#             result = await self._cancel_alarms()
#             self.state_manager.clear_active_context(self.get_name())
#             return result
#         elif any(cmd in command_lower for cmd in ["список", "сколько", "какие", "какой", "покажи"]):
#             return await self._show_alarms()
        
#         # Проверяем, есть ли активный контекст для этого модуля
#         has_context = self.state_manager.get_module_priority(self.get_name()) > 0
        
#         # Если есть контекст - обрабатываем как продолжение диалога
#         if has_context:
#             return await self._handle_with_context(command)
        
#         # Если контекста нет - начинаем новый диалог
#         return await self._handle_new_request(command)

#     async def _handle_new_request(self, command: str) -> str:
#         """Обработка новой команды установки будильника."""
#         command_lower = command.lower()
        
#         # Проверяем, содержит ли команда время
#         time_match = self.time_parser.extract_time(command)
        
#         if time_match:
#             # Если время найдено, устанавливаем будильник
#             try:
#                 alarm_time = self.time_parser.parse_time(time_match, command)
#                 await self._schedule_alarm(alarm_time)
#                 return f"✅ Будильник установлен на {alarm_time.strftime('%H:%M')}"
#             except ValueError as e:
#                 # Если время не распознано, активируем контекст для уточнения
#                 self.state_manager.set_active_context(
#                     self.get_name(), 
#                     priority=10,
#                     context_type="alarm",
#                     timeout_seconds=60
#                 )
#                 return "Не удалось распознать время. На какое время установить будильник?"
#         else:
#             # Если время не указано, активируем контекст для уточнения
#             self.state_manager.set_active_context(
#                 self.get_name(), 
#                 priority=10,
#                 context_type="alarm",
#                 timeout_seconds=60
#             )
#             return "На какое время установить будильник?"

#     async def _handle_with_context(self, command: str) -> str:
#         """Обработка команды в контексте установки будильника."""
#         # Пытаемся извлечь время из команды
#         time_match = self.time_parser.extract_time(command)
        
#         if time_match:
#             try:
#                 alarm_time = self.time_parser.parse_time(time_match, command)
#                 await self._schedule_alarm(alarm_time)
#                 self.state_manager.clear_active_context(self.get_name())
#                 return f"✅ Будильник установлен на {alarm_time.strftime('%H:%M')}"
#             except ValueError as e:
#                 # Остаемся в контексте для повторного запроса
#                 return "Не удалось распознать время. Пожалуйста, назовите время по-другому, например: 'на пять минут' или 'в три часа'"
#         else:
#             # Если время снова не указано, остаемся в контексте
#             return "Пожалуйста, назовите время для будильника. Например: 'на пять минут' или 'в три часа'"

#     async def _schedule_alarm(self, alarm_time: datetime) -> None:
#         """Планирует будильник."""
#         delay = (alarm_time - datetime.now()).total_seconds()
        
#         if delay > 0:
#             alarm_id = str(alarm_time.timestamp())
#             task = asyncio.create_task(self._trigger_alarm(alarm_time, delay, alarm_id))
#             alarm_info = {
#                 'id': alarm_id,
#                 'time': alarm_time,
#                 'task': task
#             }
#             self.active_alarms.append(alarm_info)
#             self.logger.info(f"Будильник установлен на {alarm_time.strftime('%H:%M')}")

#     async def _trigger_alarm(self, alarm_time: datetime, delay: float, alarm_id: str):
#         """Срабатывание будильника."""
#         try:
#             await asyncio.sleep(delay)
#             await self.event_bus.publish_async("calendar_reminder", {
#                 "message": f"⏰ Будильник на {alarm_time.strftime('%H:%M')}!"
#             })
        
#         except asyncio.CancelledError:
#             self.logger.info(f"Будильник {alarm_time} отменен")
#         finally:
#             self.active_alarms = [alarm for alarm in self.active_alarms if alarm['id'] != alarm_id]

#     async def _cancel_alarms(self) -> str:
#         """Отменяет все активные будильники."""
#         if not self.active_alarms:
#             return "Нет активных будильников"
        
#         cancelled = 0
#         for alarm in self.active_alarms:
#             if not alarm['task'].done():
#                 alarm['task'].cancel()
#                 cancelled += 1
        
#         self.active_alarms = []
#         return f"✅ Отменено будильников: {cancelled}"
    
#     async def _show_alarms(self) -> str:
#         """Показывает список активных будильников."""
#         if not self.active_alarms:
#             return "Нет активных будильников"
        
#         alarm_times = [alarm['time'].strftime("%H:%M") for alarm in self.active_alarms]
#         return f"Всего будильников: {len(self.active_alarms)}. На {', '.join(alarm_times)}"


import logging
import asyncio
from datetime import datetime
from typing import Optional
from src.modules.module import Module
from src.modules.parse_time import TimeParser

class AlarmModule(Module):
    def __init__(self, astra_manager):
        super().__init__(astra_manager)
        self.active_alarms = []
        self.state_manager = astra_manager.get_state_manager()
        self.event_bus = astra_manager.get_event_bus()
        self.logger = logging.getLogger(__name__)
        self.time_parser = TimeParser()  # Используем улучшенный парсер
        
    def get_name(self) -> str:
        return "AlarmModule"
    
    async def on_context_cleared(self, event_data=None):
        pass
        
    async def can_handle(self, command: str) -> bool:
        command_lower = command.lower()
        
        # Если есть активный контекст - принимаем любую команду
        if self.state_manager.get_module_priority(self.get_name()) > 0:
            return True
        
        # Без контекста принимаем только команды установки будильника
        setup_keywords = ["будильник", "разбуди", "напомни", "таймер"]
        return any(cmd in command_lower for cmd in setup_keywords)
    
    async def execute(self, command: str) -> str:
        command_lower = command.lower()
        has_context = self.state_manager.get_module_priority(self.get_name()) > 0
        
        # Обработка команд отмены и показа списка
        if any(cmd in command_lower for cmd in ["отмени", "удали", "стоп", "отмена"]):
            result = await self._cancel_alarms()
            self.state_manager.clear_active_context(self.get_name())
            return result
        elif any(cmd in command_lower for cmd in ["список", "сколько", "какие", "какой", "покажи"]):
            return await self._show_alarms()
        
        # Используем улучшенный парсер
        time_result = self.time_parser.parse_datetime(command)
        
        if not time_result["success"]:
            if has_context:
                return "Не удалось распознать время. Пожалуйста, назовите время по-другому."
            else:
                self.state_manager.set_active_context(
                    self.get_name(), 
                    priority=10,
                    context_type="alarm",
                    timeout_seconds=60
                )
                return "На какое время установить будильник?"
        
        # Устанавливаем будильник
        try:
            await self._schedule_alarm(time_result["datetime"])
            self.state_manager.clear_active_context(self.get_name())
            return f"✅ Будильник установлен на {time_result['datetime'].strftime('%d.%m.%Y в %H:%M')}"
        except Exception as e:
            return f"❌ Ошибка при установке будильника: {str(e)}"

    # Остальные методы без изменений
    async def _schedule_alarm(self, alarm_time: datetime) -> None:
        delay = (alarm_time - datetime.now()).total_seconds()
        
        if delay > 0:
            alarm_id = str(alarm_time.timestamp())
            task = asyncio.create_task(self._trigger_alarm(alarm_time, delay, alarm_id))
            alarm_info = {
                'id': alarm_id,
                'time': alarm_time,
                'task': task
            }
            self.active_alarms.append(alarm_info)

    async def _trigger_alarm(self, alarm_time: datetime, delay: float, alarm_id: str):
        try:
            await asyncio.sleep(delay)
            await self.event_bus.publish_async("message_reminder", {
                "message": f"⏰ Будильник на {alarm_time.strftime('%H:%M')}!"
            })
        except asyncio.CancelledError:
            self.logger.info(f"Будильник {alarm_time} отменен")
        finally:
            self.active_alarms = [alarm for alarm in self.active_alarms if alarm['id'] != alarm_id]

    async def _cancel_alarms(self) -> str:
        if not self.active_alarms:
            return "Нет активных будильников"
        
        cancelled = 0
        for alarm in self.active_alarms:
            if not alarm['task'].done():
                alarm['task'].cancel()
                cancelled += 1
        
        self.active_alarms = []
        return f"✅ Отменено будильников: {cancelled}"
    
    async def _show_alarms(self) -> str:
        if not self.active_alarms:
            return "Нет активных будильников"
        
        alarm_times = [alarm['time'].strftime("%H:%M") for alarm in self.active_alarms]
        return f"Всего будильников: {len(self.active_alarms)}. На {', '.join(alarm_times)}"