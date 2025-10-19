import asyncio
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
        self.context.core_instance = self
    
        self._running = False
        self._main_loop = None
        self._user_id = "Default"
        self._current_input_task = None
        
        self._setup_event_handlers()
        print("[Core] Инициализирован")
    
    def _setup_event_handlers(self):
        """Настройка обработчиков событий."""
        self.event_bus.subscribe("state_SLEEP_enter", self._on_sleep_enter)
        self.event_bus.subscribe("state_LISTENING_enter", self._on_listening_enter)
        self.event_bus.subscribe("state_PROCESSING_enter", self._on_processing_enter)
        self.event_bus.subscribe("wakeword_detected", self._on_wakeword_detected)
        self.event_bus.subscribe("sleep_requested", self._on_sleep_requested)
        self.event_bus.subscribe("alarm_triggered", self._on_alarm_triggered)

    async def _on_alarm_triggered(self, data):
        """Обработчик срабатывания будильника."""
        message = data.get("message", "Будильник!")
        print(f"{message}")
        
        # Временное пробуждение для показа уведомления
        current_state = self.state_manager.get_state()
        was_sleeping = (current_state == self.state_manager.SLEEP)
        
        if was_sleeping:
            # Отменяем текущую задачу ввода сна
            if self._current_input_task and not self._current_input_task.done():
                self._current_input_task.cancel()
            
            # Ждем подтверждения пользователя
            print("Нажмите Enter чтобы продолжить...")
            await self._async_input("")
            
            # Возвращаемся в режим сна
            await self.state_manager.change_state(self.state_manager.SLEEP)
    
    async def _on_sleep_requested(self):
        """Обработчик запроса на переход в сон."""
        await self.state_manager.change_state(self.state_manager.SLEEP)

    async def _on_sleep_enter(self):
        """Обработчик входа в состояние SLEEP."""
        print("[Core] Вход в режим сна")
        # Отменяем предыдущую задачу ввода, если она есть
        if self._current_input_task and not self._current_input_task.done():
            self._current_input_task.cancel()
        
        # Запускаем задачу для ожидания ключевого слова
        self._current_input_task = asyncio.create_task(self._sleep_input_loop())

    async def _sleep_input_loop(self):
        """Цикл ввода для режима сна."""
        while self._running and self.state_manager.get_state() == self.state_manager.SLEEP:
            try:
                command = await self._async_input("Ввод_sleep: ")
                if command == "бот":
                    await self._on_wakeword_detected()
                    break  # Выходим из цикла после пробуждения
            except asyncio.CancelledError:
                break

    async def _on_listening_enter(self):
        """Обработчик входа в состояние LISTENING."""
        print("[Core] Переход в режим listening")
        # Отменяем предыдущую задачу ввода, если она есть
        if self._current_input_task and not self._current_input_task.done():
            self._current_input_task.cancel()
        
        # Запускаем задачу для получения команды
        self._current_input_task = asyncio.create_task(self._listening_input())

    async def _listening_input(self):
        """Ввод команды в состоянии LISTENING."""
        try:
            self.command = await self._async_input("Ввод_listen: ")
            await self.state_manager.change_state(self.state_manager.PROCESSING)
        except asyncio.CancelledError:
            pass

    async def _on_processing_enter(self):
        """Обработчик входа в состояние PROCESSING."""
        print("[Core] Начинаю обработку команды")

        try:
            if self.command:
                result = await self.module_manager.execute_command(self.command)
                print(f"[Core] Результат обработки: {result}")
            else:
                print("[Core] Нет команды для обработки")
        except Exception as e:
            print(f"[Core] Ошибка обработки команды: {e}")
        finally:
            if self.state_manager.get_state() == self.state_manager.PROCESSING:
                self.command = None
                await self.state_manager.change_state(self.state_manager.LISTENING)

    async def _on_wakeword_detected(self):
        """Обработчик события обнаружения ключевого слова."""
        if self.state_manager.get_state() == self.state_manager.SLEEP:
            print("[Core] Обнаружено ключевое слово, просыпаюсь")
            self.state_manager.clear_all_contexts()
            await self.state_manager.change_state(self.state_manager.LISTENING)
    
    async def _async_input(self, prompt: str) -> str:
        """Асинхронная версия input()."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: input(prompt).strip().lower())

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
        
        # Отменяем текущую задачу ввода
        if self._current_input_task and not self._current_input_task.done():
            self._current_input_task.cancel()

    