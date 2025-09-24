import asyncio
from src.config.default import Context
from src.core.event_bus import EventBus
from src.core.state_manager import StateManager
from src.modules.module_manager import ModuleManager
from src.modules.registry import register_all_modules
import threading

class Core:
    '''Ядро'''
    def __init__(self):
        self.command = None
        self.event_bus = EventBus()
        self.state_manager = StateManager(self.event_bus)
        self.context = Context()
        self.context.core_instance = self
        self.module_manager = ModuleManager()
        register_all_modules(self.module_manager)
        
        self._running = False
        self._voice_thread = None
        self._main_loop = None  # Будем хранить ссылку на основной цикл
        
        self._setup_event_handlers()
        print("[Core] Инициализирован")
    
    def _setup_event_handlers(self):
        """Настройка обработчиков событий."""
        # Подписываем асинхронные обработчики напрямую
        self.event_bus.subscribe("state_SLEEP_enter", self._on_sleep_enter)
        self.event_bus.subscribe("state_LISTENING_enter", self._on_listening_enter)
        self.event_bus.subscribe("state_PROCESSING_enter", self._on_processing_enter)
        self.event_bus.subscribe("wakeword_detected", self._on_wakeword_detected)
    
    async def _on_sleep_enter(self):
        """Обработчик входа в состояние SLEEP."""
        print("[Core] Вход в режим сна")
        self._init_voice_trigger()

    async def _on_listening_enter(self):
        """Обработчик входа в состояние LISTENING."""
        self.command = await self._async_input("Ввод_listen: ")
        await self.state_manager.change_state(self.state_manager.PROCESSING)

    async def _on_processing_enter(self):
        """Обработчик входа в состояние PROCESSING."""
        print("[Core] Начинаю обработку команды")

        if self.command:
            result = await self.module_manager.execute_command(self.command)
            print(f"[Core] Результат обработки: {result}")
        else:
            print("[Core] Нет команды для обработки")
       
        self.command = None
        await self.state_manager.change_state(self.state_manager.SLEEP)

    async def _on_wakeword_detected(self):
        """Обработчик события обнаружения ключевого слова."""
        if self.state_manager.get_state() == self.state_manager.SLEEP:
            await self.state_manager.change_state(self.state_manager.LISTENING)
    
    async def _async_input(self, prompt: str) -> str:
        """Асинхронная версия input().
        Args:
            prompt (str): Строка вывода в терминал  
        Returns:
            str: Ответ пользователя"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: input(prompt).strip().lower())
    
    def _init_voice_trigger(self):
        """Инициализация модуля инженера голоса."""
        def voice_trigger_worker():
            import time
            while self._running and self.state_manager.get_state() == self.state_manager.SLEEP:
                time.sleep(0.1)
                command = input("Ввод_sleep: ").strip().lower()
                if command == "бот":
                    # Используем run_coroutine_threadsafe для безопасного вызова из другого потока
                    if self._main_loop is not None:
                        asyncio.run_coroutine_threadsafe(
                            self._on_wakeword_detected(), 
                            self._main_loop
                        )
                    else:
                        print("[Core] Основной цикл событий не установлен")
        
        if self._voice_thread is None or not self._voice_thread.is_alive():
            self._voice_thread = threading.Thread(target=voice_trigger_worker, daemon=True)
            self._voice_thread.start()

    async def start(self):
        """Асинхронный запуск ядра."""
        print("[Core] Запуск")
        self._running = True
        self._main_loop = asyncio.get_running_loop()  # Сохраняем ссылку на текущий цикл
        
        # Запускаем начальное состояние
        await self.state_manager.change_state(self.state_manager.SLEEP)

    async def shutdown(self):
        """Асинхронное завершение работы."""
        print("[Core] Завершение работы")
        self._running = False