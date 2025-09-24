from src.core.event_bus import EventBus

class StateManager:
    """Управление конечным автоматом (FSM) состояний."""
    
    # Определение состояний
    SLEEP = "SLEEP"
    LISTENING = "LISTENING" 
    PROCESSING = "PROCESSING"
    
    def __init__(self, event_bus: EventBus):
        self.current_state = self.SLEEP
        self.event_bus = event_bus
        # инициируем начальное состояние - сон
        self._transitions = {
            self.SLEEP: [self.LISTENING, self.SLEEP],
            self.LISTENING: [self.PROCESSING, self.SLEEP],
            self.PROCESSING: [self.LISTENING, self.SLEEP]
        }
        # возможный переход состояний (например из сна нельзя перейти в выполнение)
    
    def can_transition_to(self, new_state: str) -> bool:
        """Метод проверки возможности перехода между состояниями.
        Args:
            new_state (str): Новое состояние
            
        Returns:
            bool: True если переход возможен
        """
        return new_state in self._transitions.get(self.current_state, [])
        # если новое состояние удовлетворяем правилам перехода, то возвращаем True
    
    async def change_state(self, new_state: str):
        """Метод смены состояния
        Args:
            new_state (str): Новое состояние
        """

        if not self.can_transition_to(new_state):
            raise ValueError(f"Невозможно перейти из {self.current_state} в {new_state}")
        
        old_state = self.current_state
        self.current_state = new_state

        # вывод в терминал перехода
        print(f"[StateManager] {old_state} → {new_state}")
        
        # Публикуем события о выходе из старого статуса, о входе в новый статус, о смене статуса
        await self.event_bus.publish_async(f"state_{old_state}_exit")
        await self.event_bus.publish_async(f"state_{new_state}_enter")
        await self.event_bus.publish_async("state_changed", old_state, new_state)
        

    def get_state(self) -> str:
        """Получить текущее состояние.
        Returns:
            bool: Состояние ядра на момент запроса
        """
        return self.current_state
        # функция для получения статуса Астры
    