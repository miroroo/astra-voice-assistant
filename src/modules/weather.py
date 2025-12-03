import asyncio
import requests
from typing import Dict, Optional, Any
from .module import Module
from ..config.api_config import OPENWEATHER_API_KEY

class WeatherModule(Module):
    """Модуль для получения информации о погоде."""
    
    def __init__(self, astra_manager):
        super().__init__(astra_manager)
        self.api_key = OPENWEATHER_API_KEY
        self.state_manager = self.astra_manager.get_state_manager()
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.weather_commands = [
            'погода', 'weather', 'температура', 'прогноз', 
            'какая погода', 'сколько градусов', 'холодно', 'жарко'
        ]
        self.module_name = self.get_name()
        self.event_bus = self.astra_manager.get_event_bus()
        self.event_bus.subscribe("context_cleared", self.on_context_cleared)
    
    async def on_context_cleared(self, module_name: str):
        if self.module_name == self.get_name():
            pass
    
    async def can_handle(self, command: str) -> bool:
        if any(cmd in command for cmd in self.weather_commands):
            # Активируем контекст системного модуля с высоким приоритетом
            self.state_manager.set_active_context(
                self.module_name, 
                priority=10,  # Высокий приоритет для системных команд
                context_type="system",
                timeout_seconds=300  # 5 минут
            )
            return True
        return False

    async def execute(self, command: str) -> str:
        """Выполняет команду погоды."""
        city = self._extract_city(command)
        if not city:
            return "Для какого города вы хотите узнать погоду?"
        
        weather_data = await self._get_weather_data(city)
        return self._format_weather_response(weather_data)

    def _extract_city(self, command: str) -> Optional[str]:
        """Извлекает название города из команды."""
        
        # Паттерны для извлечения города
        patterns = [
        'погода в городе ',
        'погода в ',
        'weather in ',
        'погода ',
        'weather ',
        'температура в ',
        'температура '
        ]
        
        for pattern in patterns:
            if pattern in command:
                start_index = command.find(pattern) + len(pattern)
                city = command[start_index:].strip()
                # Убираем лишние слова в конце
                city = city.split(' ')[0]
                city_mapping = {
                'ярославле': 'Ярославль',
                'москве': 'Москва',
                'саратове': 'Саратов',
                'санкт-петербурге': 'Санкт-Петербург',
                'казани': 'Казань',
                'новосибирске': 'Новосибирск',
                'екатеринбурге': 'Екатеринбург',
                'нижнем новгороде': 'Нижний Новгород'
                }
            
                # Если город в списке маппинга, используем правильное название
                if city.lower() in city_mapping:
                    return city_mapping[city.lower()]
                
                return city.title() if city else None
        
        return None

    async def _get_weather_data(self, city: str) -> Dict[str, Any]:
        """Получает данные о погоде из API."""
        if not self.api_key:
            return {
                "success": False,
                "error": "API ключ не настроен",
                "city": city
            }

        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'ru'
            }

            # Используем асинхронный запрос
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: requests.get(self.base_url, params=params, timeout=10)
            )
            response.raise_for_status()

            data = response.json()

            return {
                "success": True,
                "city": data['name'],
                "country": data['sys']['country'],
                "temperature": round(data['main']['temp']),
                "feels_like": round(data['main']['feels_like']),
                "description": data['weather'][0]['description'],
                "humidity": data['main']['humidity'],
                "pressure": data['main']['pressure'],
                "wind_speed": data['wind']['speed'],
                "visibility": data.get('visibility', 'N/A')
            }

        except requests.exceptions.RequestException as e:
            return {
                "success":False,"error": f"Ошибка подключения: {str(e)}",
                "city": city
            }
        except KeyError as e:
            return {
                "success": False,
                "error": "Город не найден",
                "city": city
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Неожиданная ошибка: {str(e)}",
                "city": city
            }

    def _format_weather_response(self, weather_data: Dict[str, Any]) -> str:
        """Форматирует данные о погоде в читаемый текст."""
        if not weather_data.get('success'):
            error_msg = weather_data.get('error', 'Неизвестная ошибка')
            return f"Не удалось получить погоду для {weather_data.get('city', 'города')}."

        city = weather_data['city']
        country = weather_data['country']
        temp = weather_data['temperature']
        feels_like = weather_data['feels_like']
        description = weather_data['description'].capitalize()
        humidity = weather_data['humidity']
        wind_speed = weather_data['wind_speed']

        response = (
            f"Погода в городе {city}:\n"
            f"• {description}\n"
            f"• Температура: {temp}°C (ощущается как {feels_like}°C)\n"
            f"• Влажность: {humidity}%\n"
            f"• Ветер: {wind_speed} м/с"
        )

        return response