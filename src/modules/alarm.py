from .module import Module
import asyncio
from datetime import datetime, timedelta
import re

class AlarmModule(Module):
    def __init__(self, astra_manager):
        super().__init__(astra_manager)
        self.active_alarms = []
        self.state_manager = astra_manager.get_state_manager()
        
    async def can_handle(self, command: str) -> bool:
        command_lower = command.lower()
        
        # Проверяем, есть ли активный контекст установки будильника
        if self.state_manager.get_module_priority(self.get_name()) > 0:
            return True
            
        return any(cmd in command_lower for cmd in ["будильник", "разбуди", "напомни", "таймер", "отмени", "стоп", "список", "сколько",
                                                    "какие", "какой"])
    
    async def execute(self, command: str) -> str:
        command_lower = command.lower()
        
        # Проверяем, есть ли активный контекст для этого модуля
        has_context = self.state_manager.get_module_priority(self.get_name()) > 0
        
        if any(cmd in command_lower for cmd in ["отмени", "удали", "стоп"]):
            result = await self._cancel_alarms()
            self.state_manager.clear_active_context(self.get_name())
            return result
        elif any(cmd in command_lower for cmd in ["список", "сколько","какие", "какой"]):
            return await self._show_alarms()
        
        # Если есть контекст, это продолжение установки будильника
        if has_context:
            return await self._handle_alarm_context(command)
        else:
            # Новая команда установки будильника
            return await self._set_alarm(command)

    async def _handle_alarm_context(self, command: str) -> str:
        """Обработка команды в контексте установки будильника"""
        time_match = self._extract_time(command)
        
        if not time_match:
            # Сохраняем контекст и снова спрашиваем время
            self.state_manager.set_active_context(self.get_name(), priority=10, timeout_seconds=60)
            return "Не понял время. На какое время установить будильник? Например: 'на 15:30' или 'через 10 минут'"
        
        try:
            alarm_time = self._parse_time(time_match)
            await self._schedule_alarm(alarm_time)
            # Очищаем контекст после успешной установки
            self.state_manager.clear_active_context(self.get_name())
            return f"✅ Будильник установлен на {alarm_time.strftime('%H:%M')}"
            
        except ValueError as e:
            # Сохраняем контекст при ошибке
            self.state_manager.set_active_context(self.get_name(), priority=10, timeout_seconds=60)
            return f"Не удалось установить будильник: {str(e)}. Попробуйте еще раз."

    async def _set_alarm(self, command: str) -> str:
        """Начало установки будильника"""
        time_match = self._extract_time(command)
        
        if time_match:
            # Если время указано сразу в первой команде
            try:
                alarm_time = self._parse_time(time_match)
                await self._schedule_alarm(alarm_time)
                return f"✅ Будильник установлен на {alarm_time.strftime('%H:%M')}"
            except ValueError as e:
                return f"Не удалось установить будильник: {str(e)}"
        else:
            # Устанавливаем контекст для продолжения диалога
            self.state_manager.set_active_context(self.get_name(), priority=10, timeout_seconds=60)
            return "На какое время установить будильник?"

    def _extract_time(self, command: str) -> str:
        """Извлекает время из команды"""
        patterns = [
            r'на\s+(\d+:\d+)',
            r'в\s+(\d+:\d+)', 
            r'на\s+(\d+)\s*(утра|вечера|ночи|дня)',
            r'в\s+(\d+)\s*(утра|вечера|ночи|дня)',
            r'через\s+(\d+)\s*(минут|минуты|час|часа|часов)',
            r'(\d+:\d+)',  # Просто время без предлога
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command.lower())
            if match:
                return match.group(0)
        return None

    def _parse_time(self, time_text: str) -> datetime:
        """Парсит время из текста"""
        now = datetime.now()
        time_text = time_text.lower()
        
        # "через X минут/часов"
        if "через" in time_text:
            match = re.search(r'через\s+(\d+)\s*(минут|минуты|час|часа|часов)', time_text)
            if match:
                amount = int(match.group(1))
                unit = match.group(2)
                if "минут" in unit:
                    return now + timedelta(minutes=amount)
                else:
                    return now + timedelta(hours=amount)
        
        # "на 7 утра" или "в 7 вечера"
        match = re.search(r'(?:на|в)\s+(\d+)\s*(утра|вечера|ночи|дня)', time_text)
        if match:
            hour = int(match.group(1))
            period = match.group(2)
            if period in ["вечера", "ночи"] and hour < 12:
                hour += 12
            elif period == "дня" and hour < 12:
                hour += 12
            alarm_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            if alarm_time <= now:
                alarm_time += timedelta(days=1)
            return alarm_time
        
        # "на 7:30" или "7:30"
        match = re.search(r'(?:на\s+)?(\d+):(\d+)', time_text)
        if match:
            hour, minute = int(match.group(1)), int(match.group(2))
            alarm_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if alarm_time <= now:
                alarm_time += timedelta(days=1)
            return alarm_time
        
        raise ValueError("Неизвестный формат времени")

    async def _schedule_alarm(self, alarm_time: datetime) -> None:
        """Создает таймер для будильника"""
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
        """Срабатывание будильника с оповещением"""
        try:
            await asyncio.sleep(delay)
            await self.event_bus.emit("alarm_triggered", {
                "message": f"Будильник на {alarm_time.strftime('%H:%M')}!"
            })
        
        except asyncio.CancelledError:
            print(f"Будильник {alarm_time} отменен")
        finally:
            self.active_alarms = [alarm for alarm in self.active_alarms if alarm['id'] != alarm_id]

    async def _cancel_alarms(self) -> str:
        """Отмена всех будильников"""
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
        """Возвразает пользователю количество будильников и на какое время они установлены"""
        if not self.active_alarms:
            return "Нет активных будильников"
        
        alarm_times = [alarm['time'].strftime("%H:%M") for alarm in self.active_alarms]
        return f"Всего будильников: {len(self.active_alarms)}. На {', '.join(alarm_times)}"

    def get_name(self) -> str:
        return "AlarmModule"