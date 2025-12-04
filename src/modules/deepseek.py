import asyncio
import logging
import aiohttp
from typing import Optional
from src.config.api_config import DEEPSEEK_API_KEY
from src.modules.module import Module

class DeepSeekModule(Module):
    def __init__(self, astra_manager):
        super().__init__(astra_manager)
        self.logger = logging.getLogger(__name__)
        self.state_manager = astra_manager.get_state_manager()
        self.api_key = None
        self.api_base_url = "https://api.deepseek.com/v1"
        self.model = "deepseek-chat"
        self.max_tokens = 2000
        self.temperature = 0.7
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Инициализация API
        self._init_api()
        
    def _init_api(self):
        """Инициализация API ключа"""
        
        self.api_key = DEEPSEEK_API_KEY
        
        if not self.api_key:
            self.logger.warning("API ключ DeepSeek не найден. Модуль будет работать в демо-режиме.")
    
    def _load_from_config(self) -> Optional[str]:
        """Загрузка API ключа из конфигурации Astra"""
        try:
            # Пытаемся получить ключ из конфигурации Astra
            config = self.astra_manager.get_config()
            if config and hasattr(config, 'get'):
                return config.get('deepseek_api_key')
        except:
            pass
        return None
    
    async def _ensure_session(self):
        """Создание сессии aiohttp при необходимости"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
    
    def get_name(self) -> str:
        return "DeepSeekModule"
    
    async def on_context_cleared(self, event_data=None):
        pass
        
    async def can_handle(self, command: str) -> bool:
        # Всегда возвращаем True, как требуется
        return True
    
    async def execute(self, command: str) -> str:
        """
        Основной метод обработки команд.
        Получает запрос пользователя и возвращает ответ от DeepSeek API.
        """
        try:
            
            # Обрабатываем команды управления модулем
            if command.lower() in ["глубокий поиск помощь", "дипсик помощь", "/help deepseek"]:
                return await self._show_help()
            
            if command.lower() in ["статус дипсик", "статус глубокий поиск"]:
                return await self._show_status()
            
            # Получаем ответ от DeepSeek API
            response = await self._get_deepseek_response(command)
            
            # Логируем запрос и ответ
            self.logger.info(f"Запрос к DeepSeek: {command[:100]}...")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Ошибка в DeepSeekModule: {str(e)}", exc_info=True)
            return f"❌ Произошла ошибка при обработке запроса. Подробности в логах."
    
    async def _get_deepseek_response(self, query: str) -> str:
        """
        Получение ответа от DeepSeek API
        """
        # Проверяем наличие API ключа
        if not self.api_key:
            return self._get_demo_response(query)
        
        try:
            await self._ensure_session()
            
            # Формируем промпт с контекстом
            messages = [
                {
                    "role": "system",
                    "content": """Ты - полезный AI-ассистент DeepSeek, интегрированный в голосового помощника Astra.
                    Отвечай кратко, четко и по делу. Если пользователь спрашивает о твоих возможностях,
                    расскажи что ты можешь помочь с различными вопросами, генерацией текста,
                    решением задач, объяснением концепций и т.д.
                    Если вопрос требует уточнения - вежливо попроси уточнить.
                    Отвечай на русском языке, если пользователь пишет на русском."""
                },
                {
                    "role": "user",
                    "content": query
                }
            ]
            
            # Подготавливаем данные для запроса
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stream": False
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Отправляем запрос к API
            async with self.session.post(
                f"{self.api_base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    
                    if "choices" in result and len(result["choices"]) > 0:
                        answer = result["choices"][0]["message"]["content"]
                        # Убираем возможные метаданные
                        answer = answer.strip()
                        
                        # Логируем использование токенов
                        usage = result.get("usage", {})
                        self.logger.info(f"Использовано токенов: {usage.get('total_tokens', 0)}")
                        
                        return answer
                    else:
                        self.logger.error(f"Неожиданный формат ответа API: {result}")
                        return "❌ Получен неожиданный формат ответа от API."
                
                elif response.status == 401:
                    self.logger.error("Неверный API ключ DeepSeek")
                    return "❌ Ошибка авторизации. Проверьте API ключ DeepSeek."
                
                elif response.status == 429:
                    self.logger.error("Превышен лимит запросов к DeepSeek API")
                    return "⚠️ Превышен лимит запросов. Попробуйте позже или проверьте баланс."
                
                else:
                    error_text = await response.text()
                    self.logger.error(f"Ошибка API DeepSeek (код {response.status}): {error_text}")
                    return f"❌ Ошибка API (код {response.status}). Подробности в логах."
        
        except aiohttp.ClientError as e:
            self.logger.error(f"Ошибка сети при запросе к DeepSeek API: {str(e)}")
            return "❌ Ошибка сети при подключении к DeepSeek API."
        
        except asyncio.TimeoutError:
            self.logger.error("Таймаут при запросе к DeepSeek API")
            return "⏱️ Превышено время ожидания ответа от DeepSeek API."
        
        except Exception as e:
            self.logger.error(f"Непредвиденная ошибка: {str(e)}", exc_info=True)
            return self._get_demo_response(query)
    
    async def _get_demo_response(self, query: str) -> str:
        """
        Демо-ответ, если API ключ не настроен
        """
        demo_responses = [
            f"🔧 Режим демонстрации. Ваш запрос: '{query[:100]}...'",
            "📝 Для использования полных возможностей DeepSeek, пожалуйста, настройте API ключ.",
            "ℹ️ Инструкция по получению ключа: скажите 'дипсик помощь'",
            "💡 В реальном режиме я могу отвечать на сложные вопросы, генерировать текст и помогать с анализом."
        ]
        
        # Добавляем базовые ответы на частые запросы
        query_lower = query.lower()
        if "привет" in query_lower or "здравствуй" in query_lower:
            return "Привет! Я DeepSeek-ассистент в демо-режиме. Настройте API ключ для полного функционала."
        elif "помощь" in query_lower or "команды" in query_lower:
            return await self._show_help()
        elif "время" in query_lower:
            from datetime import datetime
            return f"Текущее время: {datetime.now().strftime('%H:%M:%S')} (демо-режим)"
        
        import random
        return random.choice(demo_responses)
    
    async def _show_help(self) -> str:
        """Показ справки по модулю"""
        help_text = ""
