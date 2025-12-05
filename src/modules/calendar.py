from .module import Module
from datetime import datetime, timedelta
import re
from typing import Dict, Optional
import asyncio
from src.modules.parse_time import TimeParser

class CalendarModule(Module):
    """Модуль для управления календарем и задачами с улучшенным TimeParser."""
    
    def __init__(self, astra_manager):
        super().__init__(astra_manager)
        self.tasks = {}
        self.next_task_id = 1
        self.time_parser = TimeParser()  # Используем улучшенный парсер
        
        self.calendar_commands = [
            "добавь задачу", "создай задачу", "новая задача", "напомни",
            "какие задачи", "покажи задачи", "что в календаре",
            "удали задачу", "отмени задачу", "заверши задачу",
            "планы на", "что запланировано", "расписание"
        ]
        
        self.module_name = self.get_name()
        self.event_bus = self.astra_manager.get_event_bus()
        self.state_manager = self.astra_manager.get_state_manager()
    
    async def on_context_cleared(self, event_data=None):
        pass

    async def can_handle(self, command: str) -> bool:
        command_lower = command.lower()
        return any(cmd in command_lower for cmd in self.calendar_commands)
    
    async def execute(self, command: str) -> str:
        command_lower = command.lower()
        
        if any(cmd in command_lower for cmd in ["добавь задачу", "создай задачу", "новая задача", "напомни"]):
            return await self._add_task(command)
        elif any(cmd in command_lower for cmd in ["какие задачи", "покажи задачи", "что в календаре", "планы на", "что запланировано", "расписание"]):
            return await self._show_tasks(command)
        elif any(cmd in command_lower for cmd in ["удали задачу", "отмени задачу", "заверши задачу"]):
            return await self._remove_task(command)
        else:
            return "Не поняла, что сделать с календарем."

    async def _add_task(self, command: str) -> str:
        """Добавление новой задачи с использованием улучшенного TimeParser"""
        try:
            # Используем новый универсальный парсер
            time_result = self.time_parser.parse_datetime(command)
            
            if not time_result["success"]:
                self.state_manager.set_active_context(
                    self.module_name,
                    priority=15,
                    context_type="calendar_add",
                    timeout_seconds=120
                )
                return "Пожалуйста, укажите что и когда нужно сделать. Например: 'Добавь задачу завтра в десять часов утра позвонить маме'"
            
            # Извлекаем название задачи
            title = self._extract_task_title(command, time_result.get("original_command", ""))
            if not title:
                return "Не удалось определить, что нужно сделать. Пожалуйста, уточните задачу."
            
            task_id = self.next_task_id
            self.tasks[task_id] = {
                "id": task_id,
                "title": title,
                "datetime": time_result["datetime"],
                "created": datetime.now(),
                "completed": False,
                "type": time_result["type"]
            }
            self.next_task_id += 1
            
            # Запускаем напоминание
            if time_result["datetime"]:
                asyncio.create_task(self._schedule_reminder(task_id))
            
            response = f"✅ Задача добавлена: {title}"
            if time_result["datetime"]:
                response += f" на {time_result['datetime'].strftime('%d.%m в %H:%M')}"
            
            return response
            
        except Exception as e:
            return f"Ошибка при добавлении задачи: {str(e)}"

    def _extract_task_title(self, command: str, time_expression: str = "") -> str:
        """Извлекает название задачи, убирая временные выражения"""
        clean_text = command
        
        # Убираем команды добавления
        clean_text = re.sub(
            r'добавь задачу|создай задачу|новую задачу|напомни', 
            '', clean_text, flags=re.IGNORECASE
        )
        
        # Убираем временное выражение если есть
        if time_expression:
            clean_text = clean_text.replace(time_expression, '')
        
        # Убираем лишние слова
        stop_words = ['на', 'в', 'завтра', 'сегодня', 'послезавтра', 'через', 'что', 'когда']
        words = clean_text.split()
        filtered_words = [word for word in words if word.lower() not in stop_words]
        
        return ' '.join(filtered_words).strip()

    async def _show_tasks(self, command: str) -> str:
        """Показ списка задач"""
        try:
            # Фильтруем задачи по дате из команды
            target_date = self._parse_date_from_command(command)
            now = datetime.now()
            
            if target_date:
                filtered_tasks = [
                    task for task in self.tasks.values() 
                    if task["datetime"] and task["datetime"].date() == target_date.date()
                ]
                date_str = target_date.strftime("%d.%m.%Y")
            else:
                # Показываем задачи на сегодня и будущие
                filtered_tasks = [
                    task for task in self.tasks.values() 
                    if not task["completed"] and (not task["datetime"] or task["datetime"] >= now)
                ]
                date_str = "сегодня и в будущем"
            
            if not filtered_tasks:
                return f"📅 На {date_str} задач нет."
            
            # Сортируем по дате
            filtered_tasks.sort(key=lambda x: x["datetime"] or datetime.max)
            
            response = f"📅 Задачи на {date_str}:\n"
            for task in filtered_tasks:
                status = "✅ " if task["completed"] else "⏰ "
                time_str = task["datetime"].strftime("%H:%M") if task["datetime"] else "без времени"
                response += f"{status}{task['title']} ({time_str})\n"
            
            return response.strip()
            
        except Exception as e:
            return f"Ошибка при получении задач: {str(e)}"

    async def _remove_task(self, command: str) -> str:
        """Удаление или завершение задачи"""
        try:
            # Пытаемся найти ID задачи в команде
            task_id = self._find_task_id_in_command(command)
            
            if not task_id:
                # Показываем список задач для выбора
                pending_tasks = [t for t in self.tasks.values() if not t["completed"]]
                if not pending_tasks:
                    return "Нет активных задач для удаления."
                
                response = "Какую задачу удалить? Скажите номер:\n"
                for task in pending_tasks[:5]:  # Показываем первые 5
                    time_str = task["datetime"].strftime("%H:%M") if task["datetime"] else "без времени"
                    response += f"{task['id']}. {task['title']} ({time_str})\n"
                
                self.state_manager.set_active_context(
                    self.module_name,
                    priority=10,
                    context_type="calendar_remove",
                    timeout_seconds=60
                )
                return response
            
            if task_id not in self.tasks:
                return f"Задача с номером {task_id} не найдена."
            
            task_title = self.tasks[task_id]["title"]
            del self.tasks[task_id]
            
            return f"✅ Задача '{task_title}' удалена."
            
        except Exception as e:
            return f"Ошибка при удалении задачи: {str(e)}"
        

    async def _schedule_reminder(self, task_id: int):
        """Запланировать напоминание о задаче"""
        if task_id not in self.tasks:
            return
        
        task = self.tasks[task_id]
        if not task["datetime"] or task["completed"]:
            return
        
        now = datetime.now()
        delay = (task["datetime"] - now).total_seconds()
        
        if delay > 0:
            await asyncio.sleep(delay)
            
            # Проверяем, что задача все еще актуальна
            if task_id in self.tasks and not self.tasks[task_id]["completed"]:
                await self.event_bus.publish_async("message_reminder", {
                    "task_id": task_id,
                    "title": task["title"],
                    "datetime": task["datetime"]
                })
                del self.tasks[task_id]

    def _parse_task_command(self, command: str) -> Optional[Dict]:
        """Парсит команду для извлечения деталей задачи с использованием TimeParser"""
        # Используем TimeParser для извлечения времени
        time_match = self.time_parser.extract_time(command)
        
        if time_match:
            try:
                # Парсим время с помощью TimeParser
                datetime_obj = self.time_parser.parse_time(time_match, command)
                
                # Извлекаем название задачи (убираем временные выражения)
                title = self._extract_task_title(command, time_match)
                
                if not title:
                    return None
                    
                return {
                    "title": title,
                    "datetime": datetime_obj
                }
            except ValueError:
                # Если TimeParser не смог распарсить, пробуем старый метод
                pass
        
        # Резервный метод парсинга
        return self._parse_task_command_fallback(command)

    def _parse_task_command_fallback(self, command: str) -> Optional[Dict]:
        """Резервный метод парсинга команд"""
        clean_command = re.sub(
            r'добавь задачу|создай задачу|новую задачу|напомни', 
            '', command, flags=re.IGNORECASE
        ).strip()
        
        if not clean_command:
            return None
        
        # Парсим дату и время с улучшенным распознаванием
        datetime_obj = self._parse_datetime_advanced(clean_command)
        
        # Извлекаем название задачи
        title = self._extract_task_title_advanced(clean_command)
        
        if not title:
            return None
            
        return {
            "title": title,
            "datetime": datetime_obj
        }

    def _parse_datetime_advanced(self, text: str) -> Optional[datetime]:
        """Улучшенный парсинг даты и времени с поддержкой текстовых форматов"""
        now = datetime.now()
        text_lower = text.lower()
        
        # Базовые относительные даты
        if "сейчас" in text_lower or "текущий момент" in text_lower:
            return now
        elif "сегодня" in text_lower:
            base_date = now
        elif "завтра" in text_lower:
            base_date = now + timedelta(days=1)
        elif "послезавтра" in text_lower:
            base_date = now + timedelta(days=2)
        elif "через неделю" in text_lower:
            base_date = now + timedelta(days=7)
        elif "через месяц" in text_lower:
            base_date = now + timedelta(days=30)
        else:
            # Парсим дни недели
            day_found = None
            for day_name, day_num in self.time_parser.days_of_week.items():
                if day_name in text_lower:
                    current_weekday = now.weekday()
                    days_ahead = day_num - current_weekday
                    if days_ahead <= 0:
                        days_ahead += 7
                    base_date = now + timedelta(days=days_ahead)
                    day_found = True
                    break
            
            if not day_found:
                # Парсим конкретные даты с месяцами
                date_found = self._parse_text_date(text_lower)
                if date_found:
                    return date_found
                else:
                    base_date = now
        
        # Парсим время
        time_obj = self._parse_text_time(text_lower)
        if time_obj:
            hour, minute = time_obj
        else:
            # Время по умолчанию
            if base_date.date() > now.date():
                hour, minute = 9, 0  # 9:00 утра
            else:
                hour, minute = (now.hour + 1) % 24, now.minute
        
        return datetime(base_date.year, base_date.month, base_date.day, hour, minute)

    def _parse_text_date(self, text: str) -> Optional[datetime]:
        """Парсит текстовые даты типа 'пятого мая'"""
        now = datetime.now()
        
        # Паттерн для дат типа "пятого мая", "первое января"
        date_pattern = r'(\d{1,2}|[а-я]+)\s+([а-я]+)'
        match = re.search(date_pattern, text)
        
        if match:
            day_str, month_str = match.groups()
            
            # Конвертируем день
            if day_str.isdigit():
                day = int(day_str)
            else:
                day = self._text_to_day_number(day_str)
                if day is None:
                    return None
            
            # Конвертируем месяц
            month = self.time_parser.months.get(month_str.lower())
            if month is None:
                return None
            
            year = now.year
            # Если месяц уже прошел в этом году, берем следующий год
            if month < now.month or (month == now.month and day < now.day):
                year += 1
            
            try:
                return datetime(year, month, day)
            except ValueError:
                return None
        
        return None

    def _parse_text_time(self, text: str) -> Optional[tuple]:
        """Парсит текстовое время"""
        # Используем TimeParser для извлечения времени
        time_match = self.time_parser.extract_time(text)
        if time_match:
            try:
                time_obj = self.time_parser.parse_time(time_match, text)
                return time_obj.hour, time_obj.minute
            except ValueError:
                pass
        
        # Ручной парсинг для простых случаев
        time_words = {
            'утро': (9, 0), 'утра': (9, 0), 'утром': (9, 0),
            'день': (14, 0), 'дня': (14, 0), 'днем': (14, 0),
            'вечер': (19, 0), 'вечера': (19, 0), 'вечером': (19, 0),
            'ночь': (22, 0), 'ночи': (22, 0), 'ночью': (22, 0),
            'полдень': (12, 0), 'полночь': (0, 0)
        }
        
        for word, time_tuple in time_words.items():
            if word in text:
                return time_tuple
        
        return None

    def _text_to_day_number(self, day_text: str) -> Optional[int]:
        """Конвертирует текстовое представление дня в число"""
        day_mapping = {
            'первое': 1, 'первого': 1,
            'второе': 2, 'второго': 2,
            'третье': 3, 'третьего': 3,
            'четвертое': 4, 'четвертого': 4,
            'пятое': 5, 'пятого': 5,
            'шестое': 6, 'шестого': 6,
            'седьмое': 7, 'седьмого': 7,
            'восьмое': 8, 'восьмого': 8,
            'девятое': 9, 'девятого': 9,
            'десятое': 10, 'десятого': 10,
            'одиннадцатое': 11, 'одиннадцатого': 11,
            'двенадцатое': 12, 'двенадцатого': 12,
            'тринадцатое': 13, 'тринадцатого': 13,
            'четырнадцатое': 14, 'четырнадцатого': 14,
            'пятнадцатое': 15, 'пятнадцатого': 15,
            'шестнадцатое': 16, 'шестнадцатого': 16,
            'семнадцатое': 17, 'семнадцатого': 17,
            'восемнадцатое': 18, 'восемнадцатого': 18,
            'девятнадцатое': 19, 'девятнадцатого': 19,
            'двадцатое': 20, 'двадцатого': 20,
            'двадцать первое': 21, 'двадцать первого': 21,
            'двадцать второе': 22, 'двадцать второго': 22,
            'двадцать третье': 23, 'двадцать третьего': 23,
            'двадцать четвертое': 24, 'двадцать четвертого': 24,
            'двадцать пятое': 25, 'двадцать пятого': 25,
            'двадцать шестое': 26, 'двадцать шестого': 26,
            'двадцать седьмое': 27, 'двадцать седьмого': 27,
            'двадцать восьмое': 28, 'двадцать восьмого': 28,
            'двадцать девятое': 29, 'двадцать девятого': 29,
            'тридцатое': 30, 'тридцатого': 30,
            'тридцать первое': 31, 'тридцать первого': 31
        }
        
        return day_mapping.get(day_text.lower())

    def _extract_task_title(self, command: str, time_match: str = "") -> str:
        """Извлекает название задачи, убирая временные выражения"""
        if time_match:
            # Убираем найденное временное выражение
            clean_text = command.replace(time_match, '')
        else:
            clean_text = command
        
        # Убираем команды добавления задачи
        clean_text = re.sub(
            r'добавь задачу|создай задачу|новую задачу|напомни|что|когда',
            '', clean_text, flags=re.IGNORECASE
        )
        
        # Убираем лишние слова
        stop_words = ['на', 'в', 'завтра', 'сегодня', 'послезавтра', 'через']
        words = clean_text.split()
        filtered_words = [word for word in words if word.lower() not in stop_words]
        
        return ' '.join(filtered_words).strip()

    def _extract_task_title_advanced(self, text: str) -> str:
        """Улучшенное извлечение названия задачи"""
        # Убираем временные паттерны
        time_patterns = [
            r'сегодня', r'завтра', r'послезавтра', r'через неделю', r'через месяц',
            r'в \d{1,2}[:\.]?\d{0,2}', r'на \d{1,2}[:\.]?\d{0,2}',
            r'\d{1,2}[\.\/]\d{1,2}', r'\d{1,2}[:\.]?\d{2}',
            r'утра', r'вечера', r'дня', r'ночи'
        ]
        
        clean_text = text
        for pattern in time_patterns:
            clean_text = re.sub(pattern, '', clean_text, flags=re.IGNORECASE)
        
        # Убираем дни недели и месяцы
        for day in self.time_parser.days_of_week.keys():
            clean_text = re.sub(r'\b' + re.escape(day) + r'\b', '', clean_text, flags=re.IGNORECASE)
        
        for month in self.time_parser.months.keys():
            clean_text = re.sub(r'\b' + re.escape(month) + r'\b', '', clean_text, flags=re.IGNORECASE)
        
        return clean_text.strip()

    def _parse_date_from_command(self, command: str) -> Optional[datetime]:
        """Парсит дату из команды показа задач"""
        return self._parse_datetime_advanced(command)

    def _find_task_id_in_command(self, command: str) -> Optional[int]:
        """Находит ID задачи в команде"""
        # Ищем цифры в команде
        numbers = re.findall(r'\d+', command)
        if numbers:
            task_id = int(numbers[0])
            if task_id in self.tasks:
                return task_id
        
        # Ищем по названию
        for task_id, task in self.tasks.items():
            if task["title"].lower() in command.lower():
                return task_id
        
        return None

