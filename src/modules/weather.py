import asyncio
import requests
import os
from typing import Dict, Optional, Any
from .module import Module

class WeatherModule(Module):
    """Модуль для получения информации о погоде."""
    
    def __init__(self, astra_manager):
        super().__init__(astra_manager)
        self.api_key = os.getenv('OPENWEATHER_API_KEY', 'fd239c8c5a026acdf794ef98ae179527')
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"

    async def can_handle(self, command: str) -> bool:
        """Проверяет, может ли модуль обработать команду."""
        weather_commands = [
            'погода', 'weather', 'температура', 'прогноз', 
            'какая погода', 'сколько градусов', 'холодно', 'жарко'
        ]
        normalized_command = command.lower()
        return any(cmd in normalized_command for cmd in weather_commands)

    async def execute(self, command: str) -> str:
        """Выполняет команду погоды."""
        city = self._extract_city(command)
        if not city:
            return "Для какого города вы хотите узнать погоду?"
        
        weather_data = await self._get_weather_data(city)
        return self._format_weather_response(weather_data)

    def _extract_city(self, command: str) -> Optional[str]:
        """Извлекает название города из команды."""
        command_lower = command.lower()
        
        # Паттерны для извлечения города
        patterns = [
            'погода в ',
            'погода ',
            'погода в городе'
            'weather in ',
            'weather ',
            'температура в ',
            'температура '
        ]
        
        for pattern in patterns:
            if pattern in command_lower:
                start_index = command_lower.find(pattern) + len(pattern)
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
            f"Погода в {city}, {country}:\n"
            f"• {description}\n"
            f"• Температура: {temp}°C (ощущается как {feels_like}°C)\n"
            f"• Влажность: {humidity}%\n"
            f"• Ветер: {wind_speed} м/с"
        )

        return response