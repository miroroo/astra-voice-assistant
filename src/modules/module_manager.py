from typing import List
from src.modules.module import Module

    
class ModuleManager:
    """Менеджер модулей, отвечающий за регистрацию и координацию работы модулей."""
    
    def __init__(self):
        """Инициализирует менеджер модулей с пустым списком зарегистрированных модулей."""
        self.modules: List[Module] = []
        

    def register_module(self, module: Module):
        """Регистрирует модуль в менеджере для последующего использования.
        Args:
            module (Module): Модуль для регистрации
        """
        
        self.modules.append(module)
        print(f"[ModuleManager] Зарегистрирован модуль: {module.__class__.__name__}")


    async def execute_command(self, command: str) -> str:
        """Выполняет обработку команды путем опроса всех зарегистрированных модулей.
        Args:
            command (str): Команда для проверки
            
        Returns:
            str: Результат обработки команды
        """

        for module in self.modules:
            if await module.can_handle(command):
                return await module.execute(command)
        return "Не могу обработать команду"
    


