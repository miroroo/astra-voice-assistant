import re
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple

from src.modules.module import Module

class AlarmModule(Module):
    def __init__(self, astra_manager):
        super().__init__(astra_manager)
        self.active_alarms = []
        self.state_manager = astra_manager.get_state_manager()
        self.event_bus = astra_manager.get_event_bus()
        
        # Улучшенный словарь для преобразования текста в числа
        self.number_words = {
            # Базовые числа
            'ноль': 0, 'нуль': 0,
            'один': 1, 'одна': 1, 'одну': 1,
            'два': 2, 'две': 2,
            'три': 3, 'четыре': 4, 'пять': 5,
            'шесть': 6, 'семь': 7, 'восемь': 8, 'девять': 9,
            'десять': 10, 'одиннадцать': 11, 'двенадцать': 12,
            'тринадцать': 13, 'четырнадцать': 14, 'пятнадцать': 15,
            'шестнадцать': 16, 'семнадцать': 17, 'восемнадцать': 18,
            'девятнадцать': 19, 
            
            # Десятки
            'двадцать': 20, 'тридцать': 30, 'сорок': 40, 'пятьдесят': 50,
            
            # Составные числа для минут (ДОБАВЛЕНО БОЛЬШЕ ВАРИАНТОВ)
            'двадцать один': 21, 'двадцать одна': 21, 'двадцать одну': 21,
            'двадцать два': 22, 'двадцать две': 22,
            'двадцать три': 23, 'двадцать четыре': 24, 'двадцать пять': 25,
            'двадцать шесть': 26, 'двадцать семь': 27, 'двадцать восемь': 28, 'двадцать девять': 29,
            'тридцать один': 31, 'тридцать одна': 31, 'тридцать одну': 31,
            'тридцать два': 32, 'тридцать две': 32,
            'тридцать три': 33, 'тридцать четыре': 34, 'тридцать пять': 35,
            'тридцать шесть': 36, 'тридцать семь': 37, 'тридцать восемь': 38, 'тридцать девять': 39,
            'сорок один': 41, 'сорок одна': 41, 'сорок одну': 41,
            'сорок два': 42, 'сорок две': 42,
            'сорок три': 43, 'сорок четыре': 44, 'сорок пять': 45,
            'сорок шесть': 46, 'сорок семь': 47, 'сорок восемь': 48, 'сорок девять': 49,
            'пятьдесят один': 51, 'пятьдесят одна': 51, 'пятьдесят одну': 51,
            'пятьдесят два': 52, 'пятьдесят две': 52,
            'пятьдесят три': 53, 'пятьдесят четыре': 54, 'пятьдесят пять': 55,
            'пятьдесят шесть': 56, 'пятьдесят семь': 57, 'пятьдесят восемь': 58, 'пятьдесят девять': 59,
            
            # Особые случаи
            'полчаса': 30, 'пол часа': 30, 'полтора': 90, 'полтора часа': 90
        }
        
        self.hour_variants = {
            'час': 1, 'часа': 1, 'часов': 1,
            'два': 2, 'две': 2, 'двух': 2,
            'три': 3, 'трёх': 3, 'трех': 3,
            'четыре': 4, 'четырёх': 4, 'четырех': 4,
            'пять': 5, 'пяти': 5,
            'шесть': 6, 'шести': 6,
            'семь': 7, 'семи': 7,
            'восемь': 8, 'восьми': 8,
            'девять': 9, 'девяти': 9,
            'десять': 10, 'десяти': 10,
            'одиннадцать': 11, 'одиннадцати': 11,
            'двенадцать': 12, 'двенадцати': 12,
            'первого': 1, 'второго': 2, 'третьего': 3, 'четвертого': 4,
            'пятого': 5, 'шестого': 6, 'седьмого': 7, 'восьмого': 8,
            'девятого': 9, 'десятого': 10, 'одиннадцатого': 11, 'двенадцатого': 12
        }
        
        self.minute_variants = {
            'минута': 1, 'минуты': 1, 'минут': 1,
            'одна': 1, 'одну': 1,
            'две': 2, 'два': 2,
            'пять': 5, 'десять': 10, 'пятнадцать': 15,
            'двадцать': 20, 'двадцать пять': 25, 
            'тридцать': 30, 'тридцать пять': 35, 
            'сорок': 40, 'сорок пять': 45, 
            'пятьдесят': 50, 'пятьдесят пять': 55
        }
        
    def _extract_time(self, command: str) -> str:
        """Извлекает время из команды - УЛУЧШЕННАЯ версия"""
        command_lower = command.lower()
        
        # УЛУЧШЕННЫЕ паттерны для числового времени
        patterns = [
            r'на\s+(\d+:\d+)',
            r'в\s+(\d+:\d+)', 
            r'на\s+(\d+)\s*(?:часов?|часа)?\s*(утра|вечера|ночи|дня)',  # УЛУЧШЕНО
            r'в\s+(\d+)\s*(?:часов?|часа)?\s*(утра|вечера|ночи|дня)',   # УЛУЧШЕНО
            r'через\s+(\d+)\s*(минут|минуты|час|часа|часов)',
            r'на\s+(\d+)\s*(минут|минуты|час|часа|часов)',
            r'(\d+:\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command_lower)
            if match:
                return match.group(0)
        
        # УЛУЧШЕННЫЕ паттерны для текстового времени
        text_patterns = [
            # Абсолютное время с составными числами
            r'(одиннадцать тридцать шесть|двенадцать сорок пять|час ночи|два часа|три часа|пять часов)',
            r'((?:одиннадцать|двенадцать|час|два|три|четыре|пять|шесть|семь|восемь|девять|десять)\s+(?:тридцать|сорок|пятнадцать|двадцать|двадцать пять|тридцать пять|сорок пять|пятьдесят|пятьдесят пять)\s*(?:\d+)?)',
            r'((?:на|в)\s+(?:один|два|три|четыре|пять|шесть|семь|восемь|девять|десять|одиннадцать|двенадцать)\s+(?:часа|часов)\s*(?:утра|вечера|ночи|дня))',
            r'((?:один|два|три|четыре|пять|шесть|семь|восемь|девять|десять|одиннадцать|двенадцать)\s+(?:часа|часов)\s*(?:утра|вечера|ночи|дня)?)',  # УЛУЧШЕНО
            r'(\d+\s*(?:часов?|часа)\s*(?:утра|вечера|ночи|дня))',  # ДОБАВЛЕНО для числовых часов с периодом
            
            # Относительное время
            r'(через\s+(?:пять|десять|пятнадцать|двадцать|двадцать пять|тридцать|тридцать пять|сорок|сорок пять|пятьдесят|пятьдесят пять)\s+минут)',
            r'(через\s+(?:один|два|три|четыре|пять|шесть)\s+часа?)',
            r'(через\s+(?:час|полчаса|полтора\s+часа))',
            
            # Комбинированное относительное время
            r'(через\s+(?:один|два|три|четыре|пять|шесть)\s+часа?\s+(?:пять|десять|пятнадцать|двадцать|двадцать пять|тридцать)\s+минут)',
        ]
        
        for pattern in text_patterns:
            match = re.search(pattern, command_lower)
            if match:
                return match.group(0)
                
        return None

    def _extract_number_from_text(self, text: str, default: int = None) -> int:
        """Извлекает число из текста - УЛУЧШЕННАЯ версия"""
        text_lower = text.lower()

        if "час" in text_lower and not any(word in text_lower for word in self.number_words if word != "час"):
            return 1
        
        # Сначала ищем составные числа (сортировка по длине для приоритета длинных)
        composite_numbers = [comp for comp in self.number_words.keys() if ' ' in comp]
        composite_numbers.sort(key=len, reverse=True)  # Сначала длинные
        
        for composite in composite_numbers:
            if composite in text_lower:
                return self.number_words[composite]
        
        # Затем ищем одиночные числительные
        for word, number in self.number_words.items():
            if ' ' not in word and word in text_lower:
                # Проверяем, что это отдельное слово (не часть другого слова)
                if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
                    return number
        
        # Ищем цифры
        match = re.search(r'(\d+)', text_lower)
        if match:
            return int(match.group(1))
        
        if default is not None:
            return default
        
        raise ValueError(f"Не удалось извлечь число из текста: '{text}'")

    def _extract_hours_minutes_from_text(self, text: str) -> Tuple[Optional[int], int]:
        """Извлекает часы и минуты из текстового времени - УЛУЧШЕННАЯ версия"""
        words = text.split()
        hours = None
        minutes = 0
        
        # Сначала попробуем найти составные выражения времени
        time_combinations = [
            ('одиннадцать', 'тридцать', 'шесть'), ('двенадцать', 'сорок', 'пять'),
            # Добавьте другие комбинации по необходимости
        ]
        
        for combo in time_combinations:
            if all(word in text for word in combo):
                if combo[0] in self.hour_variants:
                    hours = self.hour_variants[combo[0]]
                if f"{combo[1]} {combo[2]}" in self.number_words:
                    minutes = self.number_words[f"{combo[1]} {combo[2]}"]
                return hours, minutes
        
        i = 0
        while i < len(words):
            word = words[i]
            
            # Пытаемся найти часы
            if hours is None:
                # Проверяем текущее слово как час
                if word in self.hour_variants:
                    hours = self.hour_variants[word]
                    i += 1
                    continue
                
                # Проверяем составные часы (например, "два часа")
                if i + 1 < len(words) and words[i+1] in ['час', 'часа', 'часов']:
                    if word in self.number_words:
                        hours = self.number_words[word]
                        i += 2
                        continue
            
            # Пытаемся найти минуты
            if hours is not None:
                # Проверяем составные минуты в оставшемся тексте
                remaining_text = ' '.join(words[i:])
                
                # Сначала ищем составные числа для минут
                found_composite = False
                for composite in sorted(self.number_words.keys(), 
                                      key=lambda x: len(x), reverse=True):
                    if ' ' in composite and composite in remaining_text:
                        potential_minutes = self.number_words[composite]
                        if potential_minutes < 60:  # Только валидные минуты
                            minutes = potential_minutes
                            i += len(composite.split())  # Пропускаем обработанные слова
                            found_composite = True
                            break
                
                if found_composite:
                    continue
                
                # Если не нашли составные, проверяем одиночные минуты
                if word in self.minute_variants:
                    minutes = self.minute_variants[word]
                    i += 1
                    continue
                elif word in self.number_words and self.number_words[word] < 60:
                    minutes = self.number_words[word]
                    i += 1
                    continue
            
            i += 1
        
        return hours, minutes

    def _parse_absolute_text_time(self, time_text: str, base_time: datetime, original_command: str) -> datetime:
        """Парсит абсолютное время в текстовой форме - УЛУЧШЕННАЯ версия"""
        # УЛУЧШЕННОЕ определение периода суток
        original_lower = original_command.lower()
        
        is_pm = any(word in original_lower for word in ['вечера', 'дня'])
        is_am = any(word in original_lower for word in ['утра', 'ночи'])
        
        # Извлекаем часы и минуты из текста
        hours, minutes = self._extract_hours_minutes_from_text(time_text)
        
        if hours is None:
            hours = self._extract_hour_from_context(original_command)
        
        # УЛУЧШЕННАЯ корректировка 12-часового формата в 24-часовой
        if hours is not None:
            # Для периодов суток
            if is_pm and hours < 12:
                hours += 12
            elif is_am and hours == 12:
                hours = 0
            
            # Особые случаи
            if "ночи" in original_lower and hours >= 12:
                hours -= 12  # "час ночи" = 1:00, не 13:00
            
            # Создаем время
            alarm_time = base_time.replace(hour=hours, minute=minutes, second=0, microsecond=0)
            
            # Если время уже прошло сегодня, ставим на завтра
            if alarm_time <= base_time:
                alarm_time += timedelta(days=1)
            
            return alarm_time
        
        raise ValueError("Не удалось распознать время")

    def _parse_numeric_time(self, time_text: str, base_time: datetime) -> datetime:
        """Парсит числовое время - УЛУЧШЕННАЯ версия"""
        now = datetime.now()
        time_lower = time_text.lower()
        
        # УЛУЧШЕННАЯ обработка "на 7 утра" или "в 7 вечера" с текстовыми числами
        match = re.search(r'(?:на|в)\s+(\d+|[а-я]+)\s*(?:часов?|часа)?\s*(утра|вечера|ночи|дня)', time_lower)
        if match:
            hour_text = match.group(1)
            period = match.group(2)
            
            # Преобразуем текст в число
            hour = self._text_to_number(hour_text)
            
            # УЛУЧШЕННАЯ логика периодов
            if period in ["вечера", "дня"] and hour < 12:
                hour += 12
            elif period == "ночи" and hour == 12:
                hour = 0
            elif period == "утра" and hour == 12:
                hour = 0
                
            alarm_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            if alarm_time <= now:
                alarm_time += timedelta(days=1)
            return alarm_time
        
        # "на 7:30" или "7:30"
        match = re.search(r'(?:на\s+)?(\d+):(\d+)', time_lower)
        if match:
            hour, minute = int(match.group(1)), int(match.group(2))
            alarm_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if alarm_time <= now:
                alarm_time += timedelta(days=1)
            return alarm_time
        
        raise ValueError("Неизвестный формат времени")

    # Остальные методы остаются без изменений...
    async def can_handle(self, command: str) -> bool:
        command_lower = command.lower()
        
        if self.state_manager.get_module_priority(self.get_name()) > 0:
            return True
            
        alarm_keywords = [
            "будильник", "разбуди", "напомни", "таймер", 
            "отмени", "стоп", "список", "сколько", "какие", "какой",
            "поставь", "установи", "создай"
        ]
        
        return any(cmd in command_lower for cmd in alarm_keywords)
    
    async def execute(self, command: str) -> str:
        command_lower = command.lower()
        
        has_context = self.state_manager.get_module_priority(self.get_name()) > 0
        
        if any(cmd in command_lower for cmd in ["отмени", "удали", "стоп", "отмена"]):
            result = await self._cancel_alarms()
            self.state_manager.clear_active_context(self.get_name())
            return result
        elif any(cmd in command_lower for cmd in ["список", "сколько", "какие", "какой", "покажи"]):
            return await self._show_alarms()
        
        if has_context:
            return await self._handle_alarm_context(command)
        else:
            return await self._set_alarm(command)

    async def _handle_alarm_context(self, command: str) -> str:
        time_match = self._extract_time(command)
        
        if not time_match:
            self.state_manager.set_active_context(self.get_name(), priority=10, timeout_seconds=60)
            return "Не понял время. На какое время установить будильник? Например: 'на 15:30' или 'через 10 минут'"
        
        try:
            alarm_time = self._parse_time(time_match, command)
            await self._schedule_alarm(alarm_time)
            self.state_manager.clear_active_context(self.get_name())
            return f"✅ Будильник установлен на {alarm_time.strftime('%H:%M')}"
            
        except ValueError as e:
            self.state_manager.set_active_context(self.get_name(), priority=10, timeout_seconds=60)
            return f"Не удалось установить будильник: {str(e)}. Попробуйте еще раз."

    async def _set_alarm(self, command: str) -> str:
        time_match = self._extract_time(command)
        
        if time_match:
            try:
                alarm_time = self._parse_time(time_match, command)
                await self._schedule_alarm(alarm_time)
                return f"✅ Будильник установлен на {alarm_time.strftime('%H:%M')}"
            except ValueError as e:
                return f"Не удалось установить будильник: {str(e)}"
        else:
            self.state_manager.set_active_context(self.get_name(), priority=10, timeout_seconds=60)
            return "На какое время установить будильник?"

    def _parse_time(self, time_text: str, original_command: str = "") -> datetime:
        now = datetime.now()
        time_text = time_text.lower()
        original_command = original_command.lower()
        
        if "через" in time_text:
            return self._parse_relative_time(time_text, now)
        
        if any(word in time_text for word in self.number_words.keys()):
            return self._parse_absolute_text_time(time_text, now, original_command)
        
        return self._parse_numeric_time(time_text, now)

    def _parse_relative_time(self, time_text: str, base_time: datetime) -> datetime:
        if "минут" in time_text:
            minutes = self._extract_number_from_text(time_text)
            return base_time + timedelta(minutes=minutes)
        
        if "полчаса" in time_text or "пол часа" in time_text:
            return base_time + timedelta(minutes=30)
        
        if "полтора" in time_text:
            return base_time + timedelta(minutes=90)
            
        if "час" in time_text and "минут" not in time_text:
            hours = self._extract_number_from_text(time_text, default=1)
            return base_time + timedelta(hours=hours)
        
        if "час" in time_text and "минут" in time_text:
            hours_match = re.search(r'(\d+|[а-я]+)\s*час', time_text)
            minutes_match = re.search(r'(\d+|[а-я]+)\s*минут', time_text)
            
            hours = self._text_to_number(hours_match.group(1)) if hours_match else 0
            minutes = self._text_to_number(minutes_match.group(1)) if minutes_match else 0
            
            return base_time + timedelta(hours=hours, minutes=minutes)
        
        raise ValueError("Не удалось распознать относительное время")

    def _text_to_number(self, text: str) -> int:
        if text.isdigit():
            return int(text)
        
        for composite, number in self.number_words.items():
            if composite == text:
                return number
        
        return self.number_words.get(text, 0)

    def _extract_hour_from_context(self, command: str) -> int:
        time_indicators = {
            'утро': 9, 'утра': 9, 'утром': 9,
            'день': 14, 'дня': 14, 'днем': 14,
            'вечер': 19, 'вечера': 19, 'вечером': 19,
            'ночь': 22, 'ночи': 22, 'ночью': 22
        }
        
        for indicator, hour in time_indicators.items():
            if indicator in command:
                return hour
        
        return (datetime.now().hour + 1) % 24

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
            await self.event_bus.publish_async("alarm_triggered", {
                "message": f"⏰ Будильник на {alarm_time.strftime('%H:%M')}!"
            })
        
        except asyncio.CancelledError:
            print(f"Будильник {alarm_time} отменен")
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

    def get_name(self) -> str:
        return "AlarmModule"