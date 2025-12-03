# import re
# from datetime import datetime, timedelta
# from typing import Optional, Tuple

# class TimeParser:
#     def __init__(self):
#         self.number_words = {
#             'ноль': 0, 'нуль': 0,
#             'один': 1, 'одна': 1, 'одну': 1,
#             'два': 2, 'две': 2,
#             'три': 3, 'четыре': 4, 'пять': 5,
#             'шесть': 6, 'семь': 7, 'восемь': 8, 'девять': 9,
#             'десять': 10, 'одиннадцать': 11, 'двенадцать': 12,
#             'тринадцать': 13, 'четырнадцать': 14, 'пятнадцать': 15,
#             'шестнадцать': 16, 'семнадцать': 17, 'восемнадцать': 18,
#             'девятнадцать': 19, 
            
#             'двадцать': 20, 'тридцать': 30, 'сорок': 40, 'пятьдесят': 50,

#             'двадцать один': 21, 'двадцать одна': 21, 'двадцать одну': 21,
#             'двадцать два': 22, 'двадцать две': 22,
#             'двадцать три': 23, 'двадцать четыре': 24, 'двадцать пять': 25,
#             'двадцать шесть': 26, 'двадцать семь': 27, 'двадцать восемь': 28, 'двадцать девять': 29,
#             'тридцать один': 31, 'тридцать одна': 31, 'тридцать одну': 31,
#             'тридцать два': 32, 'тридцать две': 32,
#             'тридцать три': 33, 'тридцать четыре': 34, 'тридцать пять': 35,
#             'тридцать шесть': 36, 'тридцать семь': 37, 'тридцать восемь': 38, 'тридцать девять': 39,
#             'сорок один': 41, 'сорок одна': 41, 'сорок одну': 41,
#             'сорок два': 42, 'сорок две': 42,
#             'сорок три': 43, 'сорок четыре': 44, 'сорок пять': 45,
#             'сорок шесть': 46, 'сорок семь': 47, 'сорок восемь': 48, 'сорок девять': 49,
#             'пятьдесят один': 51, 'пятьдесят одна': 51, 'пятьдесят одну': 51,
#             'пятьдесят два': 52, 'пятьдесят две': 52,
#             'пятьдесят три': 53, 'пятьдесят четыре': 54, 'пятьдесят пять': 55,
#             'пятьдесят шесть': 56, 'пятьдесят семь': 57, 'пятьдесят восемь': 58, 'пятьдесят девять': 59,
            
#             'полчаса': 30, 'пол часа': 30, 'полтора': 90, 'полтора часа': 90
#         }
        
#         self.hour_variants = {
#             'час': 1, 'часа': 1, 'часов': 1,
#             'два': 2, 'две': 2, 'двух': 2,
#             'три': 3, 'трёх': 3, 'трех': 3,
#             'четыре': 4, 'четырёх': 4, 'четырех': 4,
#             'пять': 5, 'пяти': 5,
#             'шесть': 6, 'шести': 6,
#             'семь': 7, 'семи': 7,
#             'восемь': 8, 'восьми': 8,
#             'девять': 9, 'девяти': 9,
#             'десять': 10, 'десяти': 10,
#             'одиннадцать': 11, 'одиннадцати': 11,
#             'двенадцать': 12, 'двенадцати': 12,
#             'первого': 1, 'второго': 2, 'третьего': 3, 'четвертого': 4,
#             'пятого': 5, 'шестого': 6, 'седьмого': 7, 'восьмого': 8,
#             'девятого': 9, 'десятого': 10, 'одиннадцатого': 11, 'двенадцатого': 12
#         }
        
#         self.minute_variants = {
#             'минута': 1, 'минуты': 1, 'минут': 1,
#             'одна': 1, 'одну': 1,
#             'две': 2, 'два': 2,
#             'пять': 5, 'десять': 10, 'пятнадцать': 15,
#             'двадцать': 20, 'двадцать пять': 25, 
#             'тридцать': 30, 'тридцать пять': 35, 
#             'сорок': 40, 'сорок пять': 45, 
#             'пятьдесят': 50, 'пятьдесят пять': 55
#         }

#     def extract_time(self, command: str) -> str:
#         """Извлекает временное выражение из команды (только текстовое)"""
#         command_lower = command.lower()
        
#         # Убираем паттерны с цифровым временем (с двоеточием)
#         patterns = [
#             # Абсолютное время с периодом суток
#             r'на\s+(\d+|[а-я]+)\s*(?:часов?|часа)?\s*(утра|вечера|ночи|дня)',
#             r'в\s+(\d+|[а-я]+)\s*(?:часов?|часа)?\s*(утра|вечера|ночи|дня)', 
            
#             # Относительное время
#             r'через\s+(\d+|[а-я]+)\s*(минут|минуты|час|часа|часов)',
#             r'на\s+(\d+|[а-я]+)\s*(минут|минуты|час|часа|часов)',
            
#             # Составное относительное время
#             r'через\s+(\d+|[а-я]+)\s+часа?\s+(\d+|[а-я]+)\s+минут',
#         ]
        
#         for pattern in patterns:
#             match = re.search(pattern, command_lower)
#             if match:
#                 return match.group(0)
        
#         # Текстовые паттерны для абсолютного времени
#         text_patterns = [
#             # Конкретное время словами
#             r'(одиннадцать тридцать шесть|двенадцать сорок пять|час ночи|два часа|три часа|пять часов)',
            
#             # Общий паттерн для часов + минут
#             r'((?:одиннадцать|двенадцать|час|два|три|четыре|пять|шесть|семь|восемь|девять|десять)\s+(?:тридцать|сорок|пятнадцать|двадцать|двадцать пять|тридцать пять|сорок пять|пятьдесят|пятьдесят пять))',
            
#             # Часы с периодом суток
#             r'((?:на|в)\s+(?:один|два|три|четыре|пять|шесть|семь|восемь|девять|десять|одиннадцать|двенадцать)\s+(?:часа|часов)\s*(?:утра|вечера|ночи|дня))',
#             r'((?:один|два|три|четыре|пять|шесть|семь|восемь|девять|десять|одиннадцать|двенадцать)\s+(?:часа|часов)\s*(?:утра|вечера|ночи|дня)?)',
            
#             # Относительное время словами
#             r'(через\s+(?:пять|десять|пятнадцать|двадцать|двадцать пять|тридцать|тридцать пять|сорок|сорок пять|пятьдесят|пятьдесят пять)\s+минут)',
#             r'(через\s+(?:один|два|три|четыре|пять|шесть)\s+часа?)',
#             r'(через\s+(?:час|полчаса|полтора\s+часа))',
#         ]
        
#         for pattern in text_patterns:
#             match = re.search(pattern, command_lower)
#             if match:
#                 return match.group(0)
                
#         return None

#     def extract_number_from_text(self, text: str, default: int = None) -> int:
#         """Извлекает число из текста"""
#         text_lower = text.lower()

#         if "час" in text_lower and not any(word in text_lower for word in self.number_words if word != "час"):
#             return 1
        
#         # Сначала ищем составные числа (самые длинные)
#         composite_numbers = [comp for comp in self.number_words.keys() if ' ' in comp]
#         composite_numbers.sort(key=len, reverse=True)
        
#         for composite in composite_numbers:
#             if composite in text_lower:
#                 return self.number_words[composite]
        
#         # Затем простые числа
#         for word, number in self.number_words.items():
#             if ' ' not in word and word in text_lower:
#                 if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
#                     return number
        
#         # Пытаемся найти цифры (на случай, если всё же есть цифры)
#         match = re.search(r'(\d+)', text_lower)
#         if match:
#             return int(match.group(1))
        
#         if default is not None:
#             return default
        
#         raise ValueError(f"Не удалось извлечь число из текста: '{text}'")

#     def extract_hours_minutes_from_text(self, text: str) -> Tuple[Optional[int], int]:
#         """Извлекает часы и минуты из текстового времени"""
#         words = text.split()
#         hours = None
#         minutes = 0
        
#         # Специальные комбинации
#         time_combinations = [
#             ('одиннадцать', 'тридцать', 'шесть'), 
#             ('двенадцать', 'сорок', 'пять'),
#         ]
        
#         for combo in time_combinations:
#             if all(word in text for word in combo):
#                 if combo[0] in self.hour_variants:
#                     hours = self.hour_variants[combo[0]]
#                 if f"{combo[1]} {combo[2]}" in self.number_words:
#                     minutes = self.number_words[f"{combo[1]} {combo[2]}"]
#                 return hours, minutes
        
#         i = 0
#         while i < len(words):
#             word = words[i]
            
#             # Ищем часы
#             if hours is None:
#                 if word in self.hour_variants:
#                     hours = self.hour_variants[word]
#                     i += 1
#                     continue
                
#                 # Если следующее слово указывает на часы
#                 if i + 1 < len(words) and words[i+1] in ['час', 'часа', 'часов']:
#                     if word in self.number_words:
#                         hours = self.number_words[word]
#                         i += 2
#                         continue
            
#             # Ищем минуты
#             if hours is not None:
#                 remaining_text = ' '.join(words[i:])
                
#                 # Сначала ищем составные числа для минут
#                 found_composite = False
#                 for composite in sorted(self.number_words.keys(), 
#                                       key=lambda x: len(x), reverse=True):
#                     if ' ' in composite and composite in remaining_text:
#                         potential_minutes = self.number_words[composite]
#                         if potential_minutes < 60:
#                             minutes = potential_minutes
#                             i += len(composite.split())
#                             found_composite = True
#                             break
                
#                 if found_composite:
#                     continue
                
#                 # Затем простые числа для минут
#                 if word in self.minute_variants:
#                     minutes = self.minute_variants[word]
#                     i += 1
#                     continue
#                 elif word in self.number_words and self.number_words[word] < 60:
#                     minutes = self.number_words[word]
#                     i += 1
#                     continue
            
#             i += 1
        
#         return hours, minutes

#     def parse_absolute_text_time(self, time_text: str, base_time: datetime, original_command: str) -> datetime:
#         """Парсит абсолютное время в текстовой форме"""
#         original_lower = original_command.lower()
#         is_pm = any(word in original_lower for word in ['вечера', 'дня'])
#         is_am = any(word in original_lower for word in ['утра', 'ночи'])
        
#         hours, minutes = self.extract_hours_minutes_from_text(time_text)
        
#         if hours is None:
#             hours = self.extract_hour_from_context(original_command)
        
#         if hours is not None:
#             # Корректируем время в зависимости от периода суток
#             if is_pm and hours < 12:
#                 hours += 12
#             elif is_am and hours == 12:
#                 hours = 0
            
#             # Особый случай для "ночи"
#             if "ночи" in original_lower and hours >= 12:
#                 hours -= 12
            
#             alarm_time = base_time.replace(hour=hours, minute=minutes, second=0, microsecond=0)
            
#             # Если время уже прошло, ставим на следующий день
#             if alarm_time <= base_time:
#                 alarm_time += timedelta(days=1)
            
#             return alarm_time
        
#         raise ValueError("Не удалось распознать время")

#     def parse_relative_time(self, time_text: str, base_time: datetime) -> datetime:
#         """Парсит относительное время (через X минут/часов)"""
#         time_lower = time_text.lower()
        
#         # Обработка минут
#         if "минут" in time_lower:
#             minutes = self.extract_number_from_text(time_text)
#             return base_time + timedelta(minutes=minutes)
        
#         # Специальные случаи
#         if "полчаса" in time_lower or "пол часа" in time_lower:
#             return base_time + timedelta(minutes=30)
        
#         if "полтора" in time_lower:
#             return base_time + timedelta(minutes=90)
            
#         # Часы без минут
#         if "час" in time_lower and "минут" not in time_lower:
#             hours = self.extract_number_from_text(time_text, default=1)
#             return base_time + timedelta(hours=hours)
        
#         # Часы с минутами
#         if "час" in time_lower and "минут" in time_lower:
#             # Ищем часы
#             hours = 0
#             minutes = 0
            
#             # Пытаемся найти часы
#             for word in time_lower.split():
#                 if word in self.hour_variants or word in self.number_words:
#                     if word in self.hour_variants:
#                         hours = self.hour_variants[word]
#                     else:
#                         hours = self.number_words.get(word, 0)
#                     break
            
#             # Пытаемся найти минуты
#             for word in time_lower.split():
#                 if word in self.minute_variants or word in self.number_words:
#                     if word in self.minute_variants:
#                         minutes = self.minute_variants[word]
#                     else:
#                         num = self.number_words.get(word, 0)
#                         if num < 60:  # Убеждаемся, что это минуты, а не часы
#                             minutes = num
#                     break
            
#             return base_time + timedelta(hours=hours, minutes=minutes)
        
#         raise ValueError("Не удалось распознать относительное время")

#     def parse_time(self, time_text: str, original_command: str = "") -> datetime:
#         """Основной метод парсинга времени из текста"""
#         now = datetime.now()
#         time_text = time_text.lower()
#         original_command = original_command.lower()
        
#         # Определяем тип времени: относительное или абсолютное
#         if "через" in time_text or ("на" in time_text and any(word in time_text for word in ["минут", "час", "часа"])):
#             return self.parse_relative_time(time_text, now)
#         else:
#             # Абсолютное время
#             return self.parse_absolute_text_time(time_text, now, original_command)

#     def text_to_number(self, text: str) -> int:
#         """Конвертирует текстовое представление числа в числовое"""
#         if text.isdigit():
#             return int(text)
        
#         for composite, number in self.number_words.items():
#             if composite == text:
#                 return number
        
#         return self.number_words.get(text, 0)

#     def extract_hour_from_context(self, command: str) -> int:
#         """Извлекает час из контекста команды"""
#         time_indicators = {
#             'утро': 9, 'утра': 9, 'утром': 9,
#             'день': 14, 'дня': 14, 'днем': 14,
#             'вечер': 19, 'вечера': 19, 'вечером': 19,
#             'ночь': 22, 'ночи': 22, 'ночью': 22
#         }
        
#         for indicator, hour in time_indicators.items():
#             if indicator in command:
#                 return hour
        
#         return (datetime.now().hour + 1) % 24


import re
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any

class TimeParser:
    def __init__(self):
        # Существующие словари чисел
        self.number_words = {
            'ноль': 0, 'нуль': 0,
            'один': 1, 'одна': 1, 'одну': 1,
            'два': 2, 'две': 2,
            'три': 3, 'четыре': 4, 'пять': 5,
            'шесть': 6, 'семь': 7, 'восемь': 8, 'девять': 9,
            'десять': 10, 'одиннадцать': 11, 'двенадцать': 12,
            'тринадцать': 13, 'четырнадцать': 14, 'пятнадцать': 15,
            'шестнадцать': 16, 'семнадцать': 17, 'восемнадцать': 18,
            'девятнадцать': 19, 
            
            'двадцать': 20, 'тридцать': 30, 'сорок': 40, 'пятьдесят': 50,

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
            
            'полчаса': 30, 'пол часа': 30, 'полтора': 90, 'полтора часа': 90
        }
        
        # Словари для календаря
        self.days_of_week = {
            'понедельник': 0, 'вторник': 1, 'среду': 2, 'четверг': 3, 
            'пятницу': 4, 'субботу': 5, 'воскресенье': 6,
            'пн': 0, 'вт': 1, 'ср': 2, 'чт': 3, 'пт': 4, 'сб': 5, 'вс': 6
        }
        
        self.months = {
            'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,
            'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
            'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
        }
        
        self.day_numbers = {
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

    def extract_time(self, command: str) -> str:
        """Извлекает временное выражение из команды (расширенная версия для календаря и будильника)"""
        command_lower = command.lower()
        
        # Расширенные паттерны для календаря
        calendar_patterns = [
            # Даты с месяцами
            r'(\d{1,2}\s+[а-я]+|\d{1,2}[\.\/]\d{1,2}(?:[\.\/]\d{2,4})?)',
            r'([а-я]+\s+\d{1,2}(?:\s+года)?)',
            # Дни недели
            r'(в\s+[а-я]+|на\s+[а-я]+)',
            # Текстовые даты
            r'(пятого мая|первое января|десятого марта)',
            # Относительные даты для календаря
            r'(через неделю|через месяц|через год)',
            r'(на следующей неделе|в следующем месяце|в следующем году)',
        ]
        
        # Существующие паттерны времени
        time_patterns = [
            # Абсолютное время с периодом суток
            r'на\s+(\d+|[а-я]+)\s*(?:часов?|часа)?\s*(утра|вечера|ночи|дня)',
            r'в\s+(\d+|[а-я]+)\s*(?:часов?|часа)?\s*(утра|вечера|ночи|дня)', 
            
            # Относительное время
            r'через\s+(\d+|[а-я]+)\s*(минут|минуты|час|часа|часов)',
            r'на\s+(\d+|[а-я]+)\s*(минут|минуты|час|часа|часов)',
            
            # Составное относительное время
            r'через\s+(\d+|[а-я]+)\s+часа?\s+(\d+|[а-я]+)\s+минут',
        ]
        
        # Текстовые паттерны для абсолютного времени
        text_patterns = [
            # Конкретное время словами
            r'(одиннадцать тридцать шесть|двенадцать сорок пять|час ночи|два часа|три часа|пять часов)',
            
            # Общий паттерн для часов + минут
            r'((?:одиннадцать|двенадцать|час|два|три|четыре|пять|шесть|семь|восемь|девять|десять)\s+(?:тридцать|сорок|пятнадцать|двадцать|двадцать пять|тридцать пять|сорок пять|пятьдесят|пятьдесят пять))',
            
            # Часы с периодом суток
            r'((?:на|в)\s+(?:один|два|три|четыре|пять|шесть|семь|восемь|девять|десять|одиннадцать|двенадцать)\s+(?:часа|часов)\s*(?:утра|вечера|ночи|дня))',
            r'((?:один|два|три|четыре|пять|шесть|семь|восемь|девять|десять|одиннадцать|двенадцать)\s+(?:часа|часов)\s*(?:утра|вечера|ночи|дня)?)',
            
            # Относительное время словами
            r'(через\s+(?:пять|десять|пятнадцать|двадцать|двадцать пять|тридцать|тридцать пять|сорок|сорок пять|пятьдесят|пятьдесят пять)\s+минут)',
            r'(через\s+(?:один|два|три|четыре|пять|шесть)\s+часа?)',
            r'(через\s+(?:час|полчаса|полтора\s+часа))',
        ]
        
        # Объединяем все паттерны
        all_patterns = calendar_patterns + time_patterns + text_patterns
        
        for pattern in all_patterns:
            match = re.search(pattern, command_lower)
            if match:
                return match.group(0)
                
        return None

    def parse_datetime(self, command: str) -> Dict[str, Any]:
        """
        Универсальный метод парсинга даты и времени для календаря и будильника
        Возвращает словарь с распарсенными данными
        """
        command_lower = command.lower()
        now = datetime.now()
        
        result = {
            "datetime": None,
            "type": None,  # 'relative', 'absolute', 'date_only', 'time_only'
            "success": False,
            "original_command": command,
            "components": {}
        }
        
        try:
            # Сначала пробуем распарсить как относительное время
            relative_time = self._parse_relative_time(command_lower, now)
            if relative_time:
                result.update({
                    "datetime": relative_time,
                    "type": "relative",
                    "success": True,
                    "components": {"relative": True}
                })
                return result
            
            # Парсим абсолютную дату и время
            absolute_datetime = self._parse_absolute_datetime(command_lower, now)
            if absolute_datetime:
                result.update({
                    "datetime": absolute_datetime,
                    "type": "absolute",
                    "success": True,
                    "components": self._extract_datetime_components(absolute_datetime)
                })
                return result
            
            # Парсим только дату
            date_only = self._parse_date_only(command_lower, now)
            if date_only:
                result.update({
                    "datetime": date_only,
                    "type": "date_only", 
                    "success": True,
                    "components": self._extract_datetime_components(date_only)
                })
                return result
            
            # Парсим только время
            time_only = self._parse_time_only(command_lower, now)
            if time_only:
                result.update({
                    "datetime": time_only,
                    "type": "time_only",
                    "success": True,
                    "components": self._extract_datetime_components(time_only)
                })
                return result
                
        except Exception as e:
            result["error"] = str(e)
            
        return result

    def _parse_relative_time(self, command: str, base_time: datetime) -> Optional[datetime]:
        """Парсит относительное время (для будильника)"""
        if "через" not in command and "на" not in command:
            return None
            
        # Обработка минут
        if "минут" in command:
            minutes = self.extract_number_from_text(command)
            return base_time + timedelta(minutes=minutes)
        
        # Специальные случаи
        if "полчаса" in command or "пол часа" in command:
            return base_time + timedelta(minutes=30)
        
        if "полтора" in command:
            return base_time + timedelta(minutes=90)
            
        # Часы без минут
        if "час" in command and "минут" not in command:
            hours = self.extract_number_from_text(command, default=1)
            return base_time + timedelta(hours=hours)
        
        # Часы с минутами
        if "час" in command and "минут" in command:
            hours = 0
            minutes = 0
            
            # Пытаемся найти часы
            for word in command.split():
                if word in self.hour_variants or word in self.number_words:
                    if word in self.hour_variants:
                        hours = self.hour_variants[word]
                    else:
                        hours = self.number_words.get(word, 0)
                    break
            
            # Пытаемся найти минуты
            for word in command.split():
                if word in self.minute_variants or word in self.number_words:
                    if word in self.minute_variants:
                        minutes = self.minute_variants[word]
                    else:
                        num = self.number_words.get(word, 0)
                        if num < 60:
                            minutes = num
                    break
            
            return base_time + timedelta(hours=hours, minutes=minutes)
        
        return None

    def _parse_absolute_datetime(self, command: str, base_time: datetime) -> Optional[datetime]:
        """Парсит абсолютные даты и время (для календаря)"""
        # Определяем базовую дату
        base_date = self._parse_base_date(command, base_time)
        if not base_date:
            return None
            
        # Парсим время
        time_obj = self._parse_text_time(command)
        if time_obj:
            hour, minute = time_obj
        else:
            # Время по умолчанию
            if base_date.date() > base_time.date():
                hour, minute = 9, 0  # 9:00 утра для будущих дат
            else:
                hour, minute = (base_time.hour + 1) % 24, base_time.minute
        
        return datetime(base_date.year, base_date.month, base_date.day, hour, minute)

    def _parse_base_date(self, command: str, base_time: datetime) -> Optional[datetime]:
        """Определяет базовую дату из команды"""
        now = base_time
        
        # Базовые относительные даты
        if "сейчас" in command or "текущий момент" in command:
            return now
        elif "сегодня" in command:
            return now
        elif "завтра" in command:
            return now + timedelta(days=1)
        elif "послезавтра" in command:
            return now + timedelta(days=2)
        elif "через неделю" in command:
            return now + timedelta(days=7)
        elif "через месяц" in command:
            return now + timedelta(days=30)
        
        # Дни недели
        for day_name, day_num in self.days_of_week.items():
            if day_name in command:
                current_weekday = now.weekday()
                days_ahead = day_num - current_weekday
                if days_ahead <= 0:
                    days_ahead += 7
                return now + timedelta(days=days_ahead)
        
        # Конкретные даты с месяцами
        date_found = self._parse_text_date(command)
        if date_found:
            return date_found
        
        return now

    def _parse_text_date(self, command: str) -> Optional[datetime]:
        """Парсит текстовые даты типа 'пятого мая'"""
        now = datetime.now()
        
        # Паттерн для дат типа "пятого мая", "первое января"
        date_pattern = r'(\d{1,2}|[а-я]+)\s+([а-я]+)'
        match = re.search(date_pattern, command)
        
        if match:
            day_str, month_str = match.groups()
            
            # Конвертируем день
            if day_str.isdigit():
                day = int(day_str)
            else:
                day = self.day_numbers.get(day_str.lower())
                if day is None:
                    return None
            
            # Конвертируем месяц
            month = self.months.get(month_str.lower())
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

    def _parse_text_time(self, command: str) -> Optional[tuple]:
        """Парсит текстовое время"""
        # Используем существующую логику для времени
        time_match = self.extract_time(command)
        if time_match:
            try:
                time_obj = self.parse_time(time_match, command)
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
            if word in command:
                return time_tuple
        
        return None

    def _parse_date_only(self, command: str, base_time: datetime) -> Optional[datetime]:
        """Парсит только дату (без времени)"""
        base_date = self._parse_base_date(command, base_time)
        if base_date and base_date != base_time:
            return base_date.replace(hour=9, minute=0, second=0, microsecond=0)  # 9:00 по умолчанию
        return None

    def _parse_time_only(self, command: str, base_time: datetime) -> Optional[datetime]:
        """Парсит только время (на текущую дату)"""
        time_obj = self._parse_text_time(command)
        if time_obj:
            hour, minute = time_obj
            return base_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
        return None

    def _extract_datetime_components(self, dt: datetime) -> Dict[str, Any]:
        """Извлекает компоненты даты и времени для анализа"""
        return {
            "year": dt.year,
            "month": dt.month,
            "day": dt.day,
            "hour": dt.hour,
            "minute": dt.minute,
            "weekday": dt.weekday(),
            "is_future": dt > datetime.now(),
            "days_until": (dt.date() - datetime.now().date()).days if dt > datetime.now() else 0
        }

    # Сохраняем старые методы для обратной совместимости
    def parse_time(self, time_text: str, original_command: str = "") -> datetime:
        """Старый метод для обратной совместимости (использует новый парсер)"""
        result = self.parse_datetime(time_text + " " + original_command)
        if result["success"] and result["datetime"]:
            return result["datetime"]
        raise ValueError("Не удалось распознать время")

    # Существующие методы остаются без изменений
    def extract_number_from_text(self, text: str, default: int = None) -> int:
        """Извлекает число из текста"""
        text_lower = text.lower()

        if "час" in text_lower and not any(word in text_lower for word in self.number_words if word != "час"):
            return 1
        
        # Сначала ищем составные числа (самые длинные)
        composite_numbers = [comp for comp in self.number_words.keys() if ' ' in comp]
        composite_numbers.sort(key=len, reverse=True)
        
        for composite in composite_numbers:
            if composite in text_lower:
                return self.number_words[composite]
        
        # Затем простые числа
        for word, number in self.number_words.items():
            if ' ' not in word and word in text_lower:
                if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
                    return number
        
        # Пытаемся найти цифры
        match = re.search(r'(\d+)', text_lower)
        if match:
            return int(match.group(1))
        
        if default is not None:
            return default
        
        raise ValueError(f"Не удалось извлечь число из текста: '{text}'")

    def extract_hours_minutes_from_text(self, text: str) -> Tuple[Optional[int], int]:
        """Извлекает часы и минуты из текстового времени"""
        words = text.split()
        hours = None
        minutes = 0
        
        # Специальные комбинации
        time_combinations = [
            ('одиннадцать', 'тридцать', 'шесть'), 
            ('двенадцать', 'сорок', 'пять'),
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
            
            # Ищем часы
            if hours is None:
                if word in self.hour_variants:
                    hours = self.hour_variants[word]
                    i += 1
                    continue
                
                # Если следующее слово указывает на часы
                if i + 1 < len(words) and words[i+1] in ['час', 'часа', 'часов']:
                    if word in self.number_words:
                        hours = self.number_words[word]
                        i += 2
                        continue
            
            # Ищем минуты
            if hours is not None:
                remaining_text = ' '.join(words[i:])
                
                # Сначала ищем составные числа для минут
                found_composite = False
                for composite in sorted(self.number_words.keys(), 
                                      key=lambda x: len(x), reverse=True):
                    if ' ' in composite and composite in remaining_text:
                        potential_minutes = self.number_words[composite]
                        if potential_minutes < 60:
                            minutes = potential_minutes
                            i += len(composite.split())
                            found_composite = True
                            break
                
                if found_composite:
                    continue
                
                # Затем простые числа для минут
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

    def parse_absolute_text_time(self, time_text: str, base_time: datetime, original_command: str) -> datetime:
        """Парсит абсолютное время в текстовой форме"""
        original_lower = original_command.lower()
        is_pm = any(word in original_lower for word in ['вечера', 'дня'])
        is_am = any(word in original_lower for word in ['утра', 'ночи'])
        
        hours, minutes = self.extract_hours_minutes_from_text(time_text)
        
        if hours is None:
            hours = self.extract_hour_from_context(original_command)
        
        if hours is not None:
            # Корректируем время в зависимости от периода суток
            if is_pm and hours < 12:
                hours += 12
            elif is_am and hours == 12:
                hours = 0
            
            # Особый случай для "ночи"
            if "ночи" in original_lower and hours >= 12:
                hours -= 12
            
            alarm_time = base_time.replace(hour=hours, minute=minutes, second=0, microsecond=0)
            
            # Если время уже прошло, ставим на следующий день
            if alarm_time <= base_time:
                alarm_time += timedelta(days=1)
            
            return alarm_time
        
        raise ValueError("Не удалось распознать время")

    def parse_relative_time(self, time_text: str, base_time: datetime) -> datetime:
        """Парсит относительное время (через X минут/часов)"""
        time_lower = time_text.lower()
        
        # Обработка минут
        if "минут" in time_lower:
            minutes = self.extract_number_from_text(time_text)
            return base_time + timedelta(minutes=minutes)
        
        # Специальные случаи
        if "полчаса" in time_lower or "пол часа" in time_lower:
            return base_time + timedelta(minutes=30)
        
        if "полтора" in time_lower:
            return base_time + timedelta(minutes=90)
            
        # Часы без минут
        if "час" in time_lower and "минут" not in time_lower:
            hours = self.extract_number_from_text(time_text, default=1)
            return base_time + timedelta(hours=hours)
        
        # Часы с минутами
        if "час" in time_lower and "минут" in time_lower:
            # Ищем часы
            hours = 0
            minutes = 0
            
            # Пытаемся найти часы
            for word in time_lower.split():
                if word in self.hour_variants or word in self.number_words:
                    if word in self.hour_variants:
                        hours = self.hour_variants[word]
                    else:
                        hours = self.number_words.get(word, 0)
                    break
            
            # Пытаемся найти минуты
            for word in time_lower.split():
                if word in self.minute_variants or word in self.number_words:
                    if word in self.minute_variants:
                        minutes = self.minute_variants[word]
                    else:
                        num = self.number_words.get(word, 0)
                        if num < 60:  # Убеждаемся, что это минуты, а не часы
                            minutes = num
                    break
            
            return base_time + timedelta(hours=hours, minutes=minutes)
        
        raise ValueError("Не удалось распознать относительное время")

    def text_to_number(self, text: str) -> int:
        """Конвертирует текстовое представление числа в числовое"""
        if text.isdigit():
            return int(text)
        
        for composite, number in self.number_words.items():
            if composite == text:
                return number
        
        return self.number_words.get(text, 0)

    def extract_hour_from_context(self, command: str) -> int:
        """Извлекает час из контекста команды"""
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