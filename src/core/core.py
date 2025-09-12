from .state_manager import StateManager
from .event_bus import EventBus
from ..config.default import Context
import threading
import asyncio

class Core:
    def __init__(self):

        # ЕДИНЫЙ экземпляр EventBus
        self.event_bus = EventBus()
    
        self.state_manager = StateManager(self.event_bus)
        self.context = Context()
        self.context.core_instance = self
        
        
        self._setup_event_handlers()
        print("[Core] Инициализирован")
    
    def _setup_event_handlers(self):
        """Настройка обработчиков событий."""
        
        self.event_bus.subscribe("state_SLEEP_enter", self._on_sleep_enter)
        self.event_bus.subscribe("state_LISTENING_enter", self._on_listening_enter)
        self.event_bus.subscribe("state_PROCESSING_enter", self._on_processing_enter)
        self.event_bus.subscribe("wakeword_detected", self._on_wakeword_detected)
    
    def _on_sleep_enter(self):
        """Обработчик входа в состояние SLEEP."""
        print("[Core] Вход в режим сна")
        self._init_voice_trigger()  

    
    async def _on_listening_enter(self):
        """Обработчик входа в состояние LISTENING."""
        print("[Core] Начинаю слушать команду")       


    def _on_processing_enter(self):
        """Обработчик входа в состояние PROCESSING."""
        print("[Core] Начинаю обработку команды")
        print("[Astra] Я пока мало всего знаю")
        
    
    async def _on_wakeword_detected(self):
        """Обработчик события обнаружения ключевого слова."""
        if input("") == "Astra":
            self._on_listening_enter()

        print("[Core] Обнаружено ключевое слово!")
        if self.state_manager.get_state() == self.state_manager.SLEEP:
            await self.state_manager.change_state(self.state_manager.LISTENING)
    
    def _init_voice_trigger(self):
        """Инициализация модуля инженера голоса."""
        def voice_trigger_worker():
            # Имитация работы голосового триггера
            import time
            while self.state_manager.get_state() == self.state_manager.SLEEP:
                print("[VoiceTrigger] Слушаю...")
                time.sleep(2)
                # Имитация обнаружения ключевого слова
                if self.state_manager.get_state() == self.state_manager.SLEEP:
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(
                            self.event_bus.publish_async("wakeword_detected"))
                        loop.close()
                        
                    except Exception as e:
                        print(f"Ошибка публикации: {e}")
        
        thread = threading.Thread(target=voice_trigger_worker, daemon=True)
        thread.start()
        # тут я сама не до конца разобралась
    
    def start(self):
        """Запуск ядра."""
        print("[Core] Запуск")
        # Начинаем со состояния SLEEP

    
    def shutdown(self):
        """Корректное завершение работы."""
        print("[Core] Завершение работы")
        # Остановить все потоки и ресурсы