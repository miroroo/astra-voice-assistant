import asyncio
import time
from src.config.default import Context

class Core:
    '''Ядро'''
    def __init__(self, astra_manager):
        self.astra_manager = astra_manager
        self.command = None
        self.event_bus = astra_manager.get_event_bus()
        self.state_manager = astra_manager.get_state_manager()
        self.context = Context()
        self.module_manager = astra_manager.get_module_manager()
        self.voice_module = astra_manager.get_voice_module()
        self.context.core_instance = self
    
        self._running = False
        self._main_loop = None
        self.keyword = "астра"
        self.last_dialog_time = None
        self.listening_timeout = 30  # УВЕЛИЧЕННЫЙ таймаут для LISTENING режима
        
        self._setup_event_handlers()
        print("[Core] Инициализирован")
    
    def _setup_event_handlers(self):
        """Настройка обработчиков событий."""
        self.event_bus.subscribe("state_SLEEP_enter", self._on_sleep_enter)
        self.event_bus.subscribe("state_LISTENING_enter", self._on_listening_enter)
        self.event_bus.subscribe("state_PROCESSING_enter", self._on_processing_enter)
        self.event_bus.subscribe("sleep_requested", self._on_sleep_requested)
        self.event_bus.subscribe("alarm_triggered", self._on_alarm_triggered)

    async def _on_alarm_triggered(self, data):
        """Обработчик срабатывания будильника."""
        message = data.get("message", "Будильник!")
        self.astra_manager.speak(f"{message}")
        
        # Временное пробуждение для показа уведомления
        current_state = self.state_manager.get_state()
        was_sleeping = (current_state == self.state_manager.SLEEP)
        
        if was_sleeping: 
            await self.state_manager.change_state(self.state_manager.SLEEP)

    async def _on_sleep_requested(self):
        """Обработчик запроса на переход в сон."""
        self.last_dialog_time = None
        await self.state_manager.change_state(self.state_manager.SLEEP)

    async def _on_sleep_enter(self):
        """Обработчик входа в состояние SLEEP."""
        # Устанавливаем короткий порог паузы для SLEEP режима
        self.voice_module.set_listening_mode(False)

        try:
            loop = asyncio.get_event_loop()
            command = await loop.run_in_executor(None, self.voice_module.run)
            # Проверяем, содержит ли команда ключевое слово
            if self.keyword in command:
                self.command = command.replace(self.keyword, "").strip()
                await self.state_manager.change_state(self.state_manager.PROCESSING)
            else:
                # Если ключевое слово не найдено, остаемся в состоянии SLEEP
                await self.state_manager.change_state(self.state_manager.SLEEP)
        except asyncio.CancelledError:
            pass

    async def _on_listening_enter(self):
        """Обработчик входа в состояние LISTENING."""
        # Устанавливаем длинный порог паузы для LISTENING режима
        self.voice_module.set_listening_mode(True)
    
        # УВЕЛИЧИВАЕМ интервал для повторных команд без ключевого слова
        current_time = time.time()
        require_keyword = True
    
        if self.last_dialog_time:
            time_since_last_dialog = current_time - self.last_dialog_time
            if time_since_last_dialog < self.listening_timeout:  # УВЕЛИЧЕННОЕ время
                require_keyword = False
                print(f"[Core] Продолжение диалога, ключевое слово не требуется (прошло {time_since_last_dialog:.1f}с)")
    
        try:
            loop = asyncio.get_event_loop()
        
            if require_keyword:
                print("[Core] Требуется ключевое слово, переход в SLEEP")
                await self.state_manager.change_state(self.state_manager.SLEEP)
            else:
                print("[Core] Ожидание команды (без ключевого слова)...")
                self.command = await loop.run_in_executor(None, self.voice_module.run)
                if self.command and self.command.strip():  # Проверяем что команда не пустая
                    print(f"[Core] Получена команда: {self.command}")
                    await self.state_manager.change_state(self.state_manager.PROCESSING)
                else:
                    print("[Core] Команда не распознана, переход в SLEEP")
                    await self.state_manager.change_state(self.state_manager.SLEEP)
        
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"[Core] Ошибка при прослушивании: {e}")
            # В случае ошибки возвращаемся в состояние прослушивания
            await self.state_manager.change_state(self.state_manager.LISTENING)

    async def _on_processing_enter(self):
        """Обработчик входа в состояние PROCESSING."""

        try:
            if self.command:
                print(f"[Core] Обработка команды: {self.command}")
                result = await self.module_manager.execute_command(self.command)
                self.astra_manager.speak(result)
                
                self.last_dialog_time = time.time()
                print(f"[Core] Время диалога обновлено: {self.last_dialog_time}")
            else:
                print("[Core] Нет команды для обработки")
        except Exception as e:
            print(f"[Core] Ошибка обработки команды: {e}")
        finally:
            if self.state_manager.get_state() == self.state_manager.PROCESSING:
                self.command = None
                print("[Core] Переход в состояние LISTENING")
                await self.state_manager.change_state(self.state_manager.LISTENING)

    async def start(self):
        """Асинхронный запуск ядра."""
        print("[Core] Запуск")
        self._running = True
        self._main_loop = asyncio.get_running_loop()
        
        await self.state_manager.change_state(self.state_manager.SLEEP)
        # Бесконечный цикл для удержания программы
        while self._running:
            await asyncio.sleep(0.1)

    async def shutdown(self):
        """Асинхронное завершение работы."""
        print("[Core] Завершение работы")
        self._running = False