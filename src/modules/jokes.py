import logging
import aiohttp
import random
from typing import Dict, List, Optional
from src.modules.module import Module

class JokeModule(Module):
    def __init__(self, astra_manager):
        super().__init__(astra_manager)
        self.logger = logging.getLogger(__name__)
        self.module_name = self.get_name()
        
        self.official_joke_api = "https://official-joke-api.appspot.com"
        self.chuck_norris_api = "https://api.chucknorris.io"
        
        # Категории для каждого API
        self.official_categories = ["general", "programming", "knock-knock"]
        self.chuck_categories = [
            "animal", "career", "celebrity", "dev", "explicit", 
            "fashion", "food", "history", "money", "movie", 
            "music", "political", "religion", "science", 
            "sport", "travel"
        ]
        
        # Маппинг команд на категории
        self.command_mapping = {
            "расскажи шутку": "random",
            "пошути про программистов": "programming",
            "смешной анекдот": "random",
            "шутка": "random",
            "анекдот": "random",
            "программист": "programming",
            "разработчик": "programming",
            "айти": "programming"
        }
    
    async def on_context_cleared(self, event_data=None):
        pass
        
    async def can_handle(self, command: str) -> bool:
        command_lower = command.lower().strip()
        
        # Проверяем наличие ключевых слов
        keywords = ["шутк", "анекдот", "пошути", "смеш", "программист", "разработчик", "айти"]
        return any(keyword in command_lower for keyword in keywords)
    
    async def execute(self, command: str) -> str:
        command_lower = command.lower().strip()
        
        # Определяем тип запроса
        joke_type = "random"
        for cmd_key, cmd_type in self.command_mapping.items():
            if cmd_key in command_lower:
                joke_type = cmd_type
                break
        
        try:
            if joke_type == "programming":
                # Для шуток про программистов используем оба API
                joke = await self._get_programming_joke()
            else:
                # Случайная шутка из любого API
                joke = await  self._get_official_joke()
            
            return joke
            
        except Exception as e:
            self.logger.error(f"[Jokes] Ошибка при получении шутки: {e}")
            return "Извините, не могу найти шутку. Попробуйте позже!"

    
    async def _get_programming_joke(self) -> str:
        """Получить шутку про программистов"""
        # Сначала пробуем Official Joke API (у него есть категория programming)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.official_joke_api}/jokes/programming/random",
                    timeout=aiohttp.ClientTimeout(total=3)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and isinstance(data, list) and len(data) > 0:
                            joke = data[0]
                            return f"{joke['setup']}\n...\n{joke['punchline']}"
        except Exception as e:
            self.logger.debug(f"[Jokes] Official Joke API не ответил: {e}")
        
        # Если Official API не сработал, пробуем Chuck Norris (категория dev)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.chuck_norris_api}/jokes/random?category=dev",
                    timeout=aiohttp.ClientTimeout(total=3)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['value']
        except Exception as e:
            self.logger.debug(f"[Jokes] Chuck Norris API не ответил: {e}")
        
        # Если оба API не работают, возвращаем запасную шутку
        backup_jokes = [
            "Почему программисты путают Хэллоуин и Рождество? Потому что Oct 31 == Dec 25!",
            "Сколько программистов нужно, чтобы поменять лампочку? Ни одного, это hardware проблема!",
            "Программист звонит в службу поддержки: 'У меня проблема с компьютером.' Поддержка: 'Нажмите F1.' Программист: 'А где клавиша F1?'",
            "Почему Python не пошел на вечеринку? Потому что у него были проблемы с import!",
            "Какой язык программирования самый быстрый? Ассемблер. Потому что все остальные языки на нем написаны!"
        ]
        return random.choice(backup_jokes)
    
    async def _get_official_joke(self) -> str:
        """Получить шутку из Official Joke API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.official_joke_api}/random_joke",
                    timeout=aiohttp.ClientTimeout(total=3)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return f"{data['setup']}\n...\n{data['punchline']}"
                    else:
                        raise Exception(f"HTTP {response.status}")
        except Exception as e:
            self.logger.debug(f"[Jokes] Official Joke API error: {e}")
            # Пробуем другую категорию
            category = random.choice(self.official_categories)
            return await self._get_official_joke_by_category(category)
    
    async def _get_official_joke_by_category(self, category: str) -> str:
        """Получить шутку из Official Joke API по категории"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.official_joke_api}/jokes/{category}/random",
                    timeout=aiohttp.ClientTimeout(total=3)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and isinstance(data, list) and len(data) > 0:
                            joke = data[0]
                            return f"{joke['setup']}\n...\n{joke['punchline']}"
                        else:
                            raise Exception("No jokes found")
                    else:
                        raise Exception(f"HTTP {response.status}")
        except Exception as e:
            self.logger.debug(f"[Jokes] Official Joke API category error: {e}")
            # Если не получилось, возвращаем случайную шутку из запасных
            return await self._get_backup_joke()
    
    
    async def _get_backup_joke(self) -> str:
        """Запасные шутки на случай недоступности API"""
        backup_jokes = [
            "Что сказал 0 числу 8? - Ничего, он просто посмотрел на него свысока!",
            "Почему математики не любят леса? - Потому что там много корней!",
            "Что говорит программист, когда ему жарко? - 'if (temperature > 25) { takeOff(Jacket); }'",
            "Почему компьютер никогда не болеет? - Потому что у него есть антивирус!",
            "Как программисты называют ошибку, которая случается раз в миллион лет? - Хэллоуин!",
            "Почему программисты не любят природу? - Слишком много багов!"
        ]
        return random.choice(backup_jokes)