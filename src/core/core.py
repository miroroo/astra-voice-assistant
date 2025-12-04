import asyncio
import time
import logging

class Core:
    '''Ядро'''
    def __init__(self, astra_manager):
        self.astra_manager = astra_manager
        self.command = None
        self.event_bus = astra_manager.get_event_bus()
        self.state_manager = astra_manager.get_state_manager()
        self.module_manager = astra_manager.get_module_manager()
        self.voice_module = astra_manager.get_voice_module()
    
        self._running = False
        self._main_loop = None
        self.keyword = "астра"
        self.last_dialog_time = None
        self.listening_timeout = 30
        self.logger = logging.getLogger(__name__)
        
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Настройка обработчиков событий."""
        self.event_bus.subscribe("state_SLEEP_enter", self._on_sleep_enter)
        self.event_bus.subscribe("state_LISTENING_enter", self._on_listening_enter)
        self.event_bus.subscribe("state_PROCESSING_enter", self._on_processing_enter)
        self.event_bus.subscribe("message_reminder", self._on_message_triggered)

    async def _on_message_triggered(self, data):
        """Обработчик срабатывания будильника."""
        message = data.get("message", "Будильник!")
        if message:
            self.astra_manager.speak(f"{message}")
        else:
            message = data.get()
        
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
                await self.state_manager.change_state(self.state_manager.SLEEP)
        except asyncio.CancelledError:
            pass

    async def _on_listening_enter(self):
        """Обработчик входа в состояние LISTENING."""
        # Устанавливаем длинный порог паузы для LISTENING режима
        self.voice_module.set_listening_mode(True)
    
        current_time = time.time()
        require_keyword = True
    
        if self.last_dialog_time:
            time_since_last_dialog = current_time - self.last_dialog_time
            if time_since_last_dialog < self.listening_timeout:
                require_keyword = False
    
        try:
            loop = asyncio.get_event_loop()
        
            if require_keyword:
                await self.state_manager.change_state(self.state_manager.SLEEP)
            else:
                self.command = await loop.run_in_executor(None, self.voice_module.run)
                if self.command and self.command.strip():
                    await self.state_manager.change_state(self.state_manager.PROCESSING)
                else:
                    await self.state_manager.change_state(self.state_manager.SLEEP)
        
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.critical(f"[Core] Ошибка при прослушивании: {e}")
            await self.state_manager.change_state(self.state_manager.LISTENING)

    async def _on_processing_enter(self):
        """Обработчик входа в состояние PROCESSING."""
        try:
            if self.command:
                result = await self.module_manager.execute_command(self.command)
                self.logger.info(f"[Core]: {result}")
                self.astra_manager.update_widget_text(result)
                self.astra_manager.speak(result) 
                
                self.last_dialog_time = time.time()
            else:
                self.logger.info("[Core] Нет команды для обработки")
        except Exception as e:
            self.logger.critical(f"[Core] Ошибка обработки команды: {e}")
        finally:
            if self.state_manager.get_state() == self.state_manager.PROCESSING:
                self.command = None
                await self.state_manager.change_state(self.state_manager.LISTENING)

    async def start(self):
        """Асинхронный запуск ядра."""
        self.logger.info("[Core] Запуск")
        self._running = True
        self._main_loop = asyncio.get_running_loop()
        await self.state_manager.change_state(self.state_manager.SLEEP)
        # Бесконечный цикл для удержания программы
        while self._running:
            await asyncio.sleep(0.1)

    async def shutdown(self):
        """Асинхронное завершение работы."""
        self.logger.info("[Core] Завершение работы")
        self._running = False