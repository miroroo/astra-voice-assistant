import logging
import asyncio
from datetime import datetime
from src.modules.module import Module
from src.modules.parse_time import TimeParser

class AlarmModule(Module):
    def __init__(self, astra_manager):
        super().__init__(astra_manager)
        self.active_alarms = []
        self.state_manager = astra_manager.get_state_manager()
        self.event_bus = astra_manager.get_event_bus()
        self.logger = logging.getLogger(__name__)
        self.time_parser = TimeParser()  
        self.module_name = self.get_name()
        
    
    async def on_context_cleared(self, event_data=None):
        pass
        
    async def can_handle(self, command: str) -> bool:
        command_lower = command.lower()
        
        # Если есть активный контекст - принимаем любую команду
        if self.state_manager.get_module_priority(self.module_name()) > 0:
            if self.time_parser.parse_datetime(command)["success"]: 
                return True
        
        # Без контекста принимаем только команды установки будильника
        setup_keywords = ["будильник", "разбуди", "напомни", "таймер"]
        return any(cmd in command_lower for cmd in setup_keywords)
    
    async def execute(self, command: str) -> str:
        command_lower = command.lower()
        has_context = self.state_manager.get_module_priority(self.module_name()) > 0
        
        # Обработка команд отмены и показа списка
        if any(cmd in command_lower for cmd in ["отмени", "удали", "стоп", "отмена"]):
            result = await self._cancel_alarms()
            self.state_manager.clear_active_context(self.module_name())
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
                    self.module_name(), 
                    priority=10,
                    context_type="alarm",
                    timeout_seconds=60
                )
                return "На какое время установить будильник?"
        
        # Устанавливаем будильник
        try:
            await self._schedule_alarm(time_result["datetime"])
            self.state_manager.clear_active_context(self.module_name())
            return f"✅ Будильник установлен на {time_result['datetime'].strftime('%d.%m.%Y в %H:%M')}"
        except Exception as e:
            return f"[Alarm] Ошибка при установке будильника: {str(e)}"

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
            self.logger.info(f"[Alarm] Будильник {alarm_time} отменен")
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