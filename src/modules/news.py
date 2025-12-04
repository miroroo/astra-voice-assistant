import logging
import aiohttp
from typing import Dict, Any
from src.modules.module import Module

class NewsModule(Module):
    def __init__(self, astra_manager):
        super().__init__(astra_manager)
        self.state_manager = astra_manager.get_state_manager()
        self.logger = logging.getLogger(__name__)
        self.api_key = "1dde02817f5d763a914b326223f667af"  # Получите полный ключ на gnews.io
        self.base_url = "https://gnews.io/api/v4"
        self.default_language = "ru"  # Исправлено: было default_country
        self.categories = {
            "бизнесе": "business",
            "технологиях": "technology", 
            "спорте": "sports",
            "развлечениях": "entertainment",
            "здоровье": "health",
            "науке": "science",
            "общие": "general"
        }
        
    def get_name(self) -> str:
        return "NewsModule"
    
    async def on_context_cleared(self, event_data=None):
        pass
        
    async def can_handle(self, command: str) -> bool:
        command_lower = command.lower()
        
        # Если есть активный контекст - принимаем любую команду
        if self.state_manager.get_module_priority(self.get_name()) > 0:
            return True
        
        # Без контекста проверяем ключевые слова новостей
        news_keywords = ["новости", "новость", "события", "что нового", "сводка"]
        category_keywords = list(self.categories.keys())
        
        return any(keyword in command_lower for keyword in news_keywords + category_keywords)
    
    async def execute(self, command: str) -> str:
        command_lower = command.lower()
        has_context = self.state_manager.get_module_priority(self.get_name()) > 0
        
        # Обработка команд выхода
        if any(cmd in command_lower for cmd in ["выход", "стоп", "закончить", "отмена"]):
            self.state_manager.clear_active_context(self.get_name())
            return "Выход из режима новостей"
        
        # Определяем запрос пользователя
        if has_context:
            # Пользователь в контексте новостей
            if any(cmd in command_lower for cmd in ["еще", "дальше", "следующие", "продолжить"]):
                return await self._get_more_news()
            else:
                # Пользователь уточняет запрос
                return await self._process_news_query(command)
        else:
            # Новый запрос новостей
            self.state_manager.set_active_context(
                self.get_name(), 
                priority=10,
                context_type="news",
                timeout_seconds=60
            )
            return await self._process_news_query(command)
    
    async def _process_news_query(self, command: str) -> str:
        """Обработка запроса новостей"""
        command_lower = command.lower()
        
        # Проверяем категории
        selected_category = None
        for ru_category, en_category in self.categories.items():
            if ru_category in command_lower:
                selected_category = en_category
                break
        
        # Проверяем ключевые слова
        search_query = None
        if any(word in command_lower for word in ["про", "о", "об", "насчет", "на тему"]):
            # Извлекаем тему после ключевых слов
            words = command_lower.split()
            for i, word in enumerate(words):
                if word in ["про", "о", "об", "насчет", "на"] and i + 1 < len(words):
                    search_query = " ".join(words[i+1:])
                    break
        
        # Если есть конкретный запрос - поиск, иначе топ новостей
        if search_query:
            return await self._search_news(search_query)
        elif selected_category:
            return await self._get_top_news(category=selected_category)
        else:
            return await self._get_top_news()
    
    async def _get_top_news(self, category: str = None, page: int = 1) -> str:
        """Получение топ новостей через GNews API"""
        try:
            params = {
                "lang": self.default_language,
                "max": 5,
                "page": page,  # Добавлен параметр страницы
                "apikey": self.api_key
            }
            
            if category:
                params["category"] = category
            else:
                params["topic"] = "breaking-news"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/top-headlines", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_news_response(data, category)
                    else:
                        error_text = await response.text()
                        self.logger.error(f"GNews API error: {response.status}, {error_text}")
                        return f"Ошибка при получении новостей: {response.status}"
                        
        except Exception as e:
            self.logger.error(f"Error fetching news: {e}")
            return "Не удалось получить новости. Проверьте подключение к интернету."
    
    async def _search_news(self, query: str, page: int = 1) -> str:
        """Поиск новостей по запросу через GNews API"""
        try:
            params = {
                "q": query,
                "lang": self.default_language,
                "max": 5,
                "page": page,  # Добавлен параметр страницы
                "apikey": self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/search", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_news_response(data, query=query)
                    else:
                        return f"Ошибка при поиске новостей: {response.status}"
                        
        except Exception as e:
            self.logger.error(f"Error searching news: {e}")
            return "Не удалось выполнить поиск новостей."
    
    async def _get_more_news(self) -> str:
        """Получение следующих новостей"""
        # Здесь нужно хранить состояние предыдущего запроса
        return "Показываю следующие новости...\n" + await self._get_top_news(page=2)
    
    def _format_news_response(self, data: Dict[str, Any], category: str = None, query: str = None) -> str:
        """Форматирование ответа с новостями"""
        if not data.get("articles"):
            return "Новости не найдены."
        
        articles = data["articles"][:3]
        
        # Формируем заголовок
        if category:
            ru_category = next((k for k, v in self.categories.items() if v == category), category)
            response = f"📰 Главные новости ({ru_category}):\n\n"
        elif query:
            response = f"📰 Новости по запросу '{query}':\n\n"
        else:
            response = "📰 Главные новости:\n\n"
        
        # Добавляем статьи
        for i, article in enumerate(articles, 1):
            title = article.get("title", "Без заголовка")
            source = article.get("source", {}).get("name", "Неизвестный источник")
            description = article.get("description", "")
            
            response += f"{i}. {title}\n"
            if source:
                response += f"Источник - {source}\n"
            
            # Обрезаем описание если оно слишком длинное
            if description:
                if len(description) > 200:
                    description = description[:200] + "..."
                response += f"{description}\n"
            
            response += "\n"
        
        response += "Скажите 'еще' для продолжения или назовите другую тему."
        return response 