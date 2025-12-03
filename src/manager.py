from src.core.core import Core
from src.core.event_bus import EventBus
from src.core.state_manager import StateManager
from src.modules.module_manager import ModuleManager
from src.modules.registry import register_all_modules
from src.voice_engine.listener import VoiceModule
from src.voice_engine.tts_engine import TTSModule
from src.ui.overlay_widget import TextWindow
import logging
import asyncio
import sys
import asyncio
from PyQt6.QtWidgets import QApplication
from qasync import QEventLoop

class AstraManager:
    """Главный менеджер"""
    
    def __init__(self):
        self.event_bus = EventBus()
        self.state_manager = StateManager(self.event_bus)
        self.module_manager = ModuleManager(self)
        self.overlay_manager = OverlayManager()
        self.logger = logging.getLogger(__name__)
        
        # Инициализация PyQt overlay
        self.overlay_initialized = False
        
        self.voice_module = VoiceModule(
            self.event_bus,
            keyword="астра",
            pause_threshold=5,
            listening_pause_threshold=6, 
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
            self.logger.info("TTS модуль инициализирован")
        except Exception as e:
            self.logger.critical(f"Ошибка инициализации TTS: {e}")
            self.tts_module = None
        
        self.logger.info("[AstraManager] Инициализирован")


    async def _initialize_overlay(self):
        """Инициализировать overlay асинхронно"""
        try:
            self.overlay_initialized = await self.overlay_manager.start()
            if self.overlay_initialized:
                self.logger.info("Виджет успешно запущен")
                # Даем время окну отобразиться
                await asyncio.sleep(0.5)
            else:
                self.logger.error("Ошибка запуска виджета")
            return self.overlay_initialized
        except Exception as e:
            self.logger.error(f"Ошибка инициализации виджета: {e}")
            return False

    def update_widget_text(self, text: str):
        """Обновить текст в overlay"""
        try:
            self.overlay_manager.update_text(text)
        except Exception as e:
            self.logger.error(f"Ошибка обновления overlay: {e}")
    
    async def start(self):
        """Запустить Астру."""
        self.logger.info("Запуск Astra...")
        await self._initialize_overlay()
        
        await self.core.start()


    async def stop(self):
        """Остановить Астру."""

        self.update_widget_text("Завершение работы...")
        await asyncio.sleep(0.5)
        await self.core.shutdown()
        await self.overlay_manager.stop()
        self.logger.info("Astra остановлена")
    
    async def force_state_change(self, new_state: str):
        """Принудительно сменить состояние"""
        try:
            await self.state_manager.change_state(new_state)
        except ValueError as e:
            self.logger.critical(f"Ошибка: {e}")

    def speak(self, text):
        """Безопасное произношение текста"""
        if self.tts_module is None:
            self.logger.critical("TTS модуль не доступен")
            return
        try:
            self.tts_module.say(text)
        except Exception as e:
            self.logger.critical(f"[TTS Ошибка] {e}")
    
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
    


class OverlayManager:
    """Менеджер для управления overlay окном"""
    
    def __init__(self):
        self.app = None
        self.window = None
        self.loop = None
        self._running = False
        
    async def start(self):
        """Запустить overlay"""
        try:
            # Создаем QApplication если его еще нет
            if not QApplication.instance():
                self.app = QApplication(sys.argv)
            else:
                self.app = QApplication.instance()
            
            # Настраиваем asyncio event loop для Qt
            self.loop = QEventLoop(self.app)
            asyncio.set_event_loop(self.loop)
            
            # Создаем окно
            self.window = TextWindow()
            self.window.show()
            self._running = True
            
            print("✓ Overlay window created and shown")
            return True
            
        except Exception as e:
            print(f"✗ Ошибка запуска overlay: {e}")
            return False
    
    def update_text(self, text: str):
        """Обновить текст в overlay"""
        try:
            if self.window and self._running:
                self.window.update_text(text)
                return True
            return False
        except Exception as e:
            print(f"Ошибка обновления текста: {e}")
            return False
    
    def show(self):
        """Показать overlay"""
        if self.window and self._running:
            self.window.show()
    
    def hide(self):
        """Скрыть overlay"""
        if self.window and self._running:
            self.window.hide()
    
    async def stop(self):
        """Остановить overlay"""
        try:
            if self.window:
                self.window.close()
                self.window = None
            if self.app:
                self.app.quit()
            self._running = False
        except Exception as e:
            print(f"Ошибка остановки overlay: {e}")

