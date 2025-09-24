from abc import ABC, abstractmethod


class Module(ABC):
    @abstractmethod
    async def execute(self, command: str) -> str:
        pass

    async def can_handle(self, command: str) -> bool:
        """Метод проверки возможности обработки команды данным модулем.
        Args:
            command (str): Команда для проверки
            
        Returns:
            bool: True если модуль поддерживает команду
        """

        return False
