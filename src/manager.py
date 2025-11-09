from src.core.core import Core
from src.core.state_manager import StateManager
from src.core.event_bus import EventBus
from src.modules.module_manager import ModuleManager
from src.modules.registry import register_all_modules
from src.voice_engine.listener import VoiceModule
import logging

from src.voice_engine.tts_engine import TTSModule

class AstraManager:
    """Главный менеджер"""
    def __init__(self):

        self.event_bus = EventBus()
        self.state_manager = StateManager(self.event_bus)
        self.module_manager = ModuleManager(self)
        
        self.voice_module = VoiceModule(
            self.event_bus,
            keyword="астра",
            pause_threshold=3,
            listening_pause_threshold=7, 
            log_level=logging.INFO,
        )
        
        self.core = Core(self)
        
        register_all_modules(self)

        try:
            self.tts_module = TTSModule(
                rate=180,
                volume=1.0,
                lang='ru',
                gender='female'
            )
            print("✓ TTS модуль инициализирован")
        except Exception as e:
            print(f"✗ Ошибка инициализации TTS: {e}")
            self.tts_module = None

        self.event_bus.subscribe('tts_speak', self._handle_tts_request)
        
        print("[AstraManager] Инициализирован")

    
    async def start(self):
        """Запустить Астру."""
        await self.core.start()
    

    async def stop(self):
        """Остановить Астру."""
        await self.core.shutdown()
    

    async def force_state_change(self, new_state: str):
        """Принудительно сменить состояние (для тестирования)"""
        try:
            await self.state_manager.change_state(new_state)
        except ValueError as e:
            print(f"Ошибка: {e}")


    def _handle_tts_request(self, event):
        """Обработчик событий для TTS"""
        text = event.data.get('text', '')
        if text:
            self.speak(text)


    def speak(self, text):
        """Безопасное произношение текста"""
        if self.tts_module is None:
            print("TTS модуль не доступен")
            return
            
        try:
            print(f"[TTS] Произношу: {text}")
            self.tts_module.say(text)
        except Exception as e:
            print(f"[TTS Ошибка] {e}")


    # Метод для отправки TTS команд из других модулей
    def trigger_tts(self, text):
        """Запустить TTS через систему событий"""
        self.event_bus.emit('tts_speak', {'text': text})
    

    def get_state(self) -> str:
        """Получить текущее состояние."""
        return self.state_manager.get_state()
    

    def get_state_manager(self):
        return self.state_manager
    

    def get_event_bus(self):
        return self.event_bus
    

    def get_module_manager(self):
        return self.module_manager  
    

    def get_voice_module(self):
        return self.voice_module