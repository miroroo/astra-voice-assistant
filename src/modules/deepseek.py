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
        self.module_name = self.get_name()
        self.api_key = DEEPSEEK_API_KEY
        
        if not self.api_key:
            self.logger.warning("[DeepSeek] API ключ DeepSeek не найден. Модуль будет работать в демо-режиме.")
    

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

            # Получаем ответ от DeepSeek API
            response = await self._get_deepseek_response(command)
            
            # Логируем запрос и ответ
            self.logger.info(f"[DeepSeek] Запрос к DeepSeek: {command[:100]}...")
            
            return response
            
        except Exception as e:
            self.logger.error(f"[DeepSeek] Ошибка в DeepSeekModule: {str(e)}", exc_info=True)
            return f"Произошла ошибка при обработке запроса. Подробности в логах."
    
    async def _get_deepseek_response(self, query: str) -> str:
        """
        Получение ответа от DeepSeek API
        """

        try:
            if self.session is None or self.session.closed:
                self.session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=30)
                )    
            
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

                        answer = answer.strip()
                        
                        return answer
                    else:
                        self.logger.error(f"[DeepSeek] Неожиданный формат ответа API: {result}")
                        return "Получен неожиданный формат ответа от API."
                
                elif response.status == 401:
                    self.logger.error("[DeepSeek] Неверный API ключ DeepSeek")
                    return "Ошибка авторизации. Проверьте API ключ DeepSeek."
                
                elif response.status == 429:
                    self.logger.error("[DeepSeek] Превышен лимит запросов к DeepSeek API")
                    return "Превышен лимит запросов. Попробуйте позже или проверьте баланс."
                
                elif response.status == 402:
                    self.logger.error("[DeepSeek] Не хватает баланса на карте")
                    return "Пополните кошелёк."
                
                else:
                    error_text = await response.text()
                    self.logger.error(f"[DeepSeek] Ошибка API DeepSeek (код {response.status}): {error_text}")
                    return f"Ошибка API (код {response.status}). Подробности в логах."
        
        except aiohttp.ClientError as e:
            self.logger.error(f"[DeepSeek] Ошибка сети при запросе к DeepSeek API: {str(e)}")
            return "Ошибка сети при подключении к DeepSeek API."
        
        except asyncio.TimeoutError:
            self.logger.error("[DeepSeek] Таймаут при запросе к DeepSeek API")
            return "⏱️ Превышено время ожидания ответа от DeepSeek API."
        
        except Exception as e:
            self.logger.error(f"[DeepSeek] Непредвиденная ошибка: {str(e)}", exc_info=True)
            return "Неизвестная ошибка"
    