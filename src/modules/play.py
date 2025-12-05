import random
import re
from .module import Module

class RandomModule(Module):
    """Модуль для игрового взаимодействия."""
    
    def __init__(self, astra_manager):
        super().__init__(astra_manager)
        self.module_name = self.get_name()
        self.state_manager = self.astra_manager.get_state_manager()
    
    async def can_handle(self, command: str) -> bool:
        """Проверяет возможность обработки команды."""
        if not command or not isinstance(command, str):
            return False
        
        cmd = command.lower().strip()
        keywords = ['монет','орёл', 'решка', 'кубик', 'кость', 'дайс', 'число', 'рандом', 'поигра', 'сыграй']
        
        for keyword in keywords:
            if keyword in cmd:
                self.state_manager.set_active_context(
                    self.module_name,
                    priority=15,
                    context_type="game",
                    timeout_seconds=180
                )
                return True
        return False
    
    async def execute(self, command: str) -> str:
        """Обрабатывает игровую команду."""
        if not command:
            return "Что поиграем? Монетку, кубик или случайное число?"
        
        cmd = command.lower().strip()
        
        if any(word in cmd for word in ['монет', 'орёл', 'решка']):
            return await self._flip_coin()
        elif any(word in cmd for word in ['кубик', 'кость', 'дайс']):
            return await self._roll_dice(cmd)
        else:
            return await self._random_number(cmd)
    
    async def _flip_coin(self) -> str:
        """Подбрасывает монетку."""
        result = random.choice(["орёл", "решка"])
        sound = random.choice(["*подбрасываю монетку*", "*монетка крутится*"])
        emoji = "🦅" if result == "орёл" else "⭐️"
        
        responses = [
            f"{sound} Выпал {result}! {emoji}",
            f"{sound} Это {result}! {emoji}",
            f"{sound} {result.capitalize()}! {emoji}"
        ]
        return random.choice(responses)
    
    async def _roll_dice(self, command: str) -> str:
        """Бросает кубик."""
        dice_count = 1
        sides = 6
        
        # Определяем параметры
        count_match = re.search(r'(\d+)\s*кубик', command)
        if count_match:
            dice_count = min(int(count_match.group(1)), 10)
        
        sides_match = re.search(r'd(\d+)', command)
        if sides_match:
            sides = min(max(2, int(sides_match.group(1))), 100)
        
        # Бросаем
        results = [random.randint(1, sides) for _ in range(dice_count)]
        sound = random.choice(["*бросаю кубик*", "*кости летят*"])
        
        # Формируем ответ
        if dice_count == 1:
            return f"{sound} Выпало {results[0]}! 🎲"
        else:
            results_str = ', '.join(map(str, results))
            total = sum(results)
            return f"{sound} {dice_count} кубика: {results_str}. Сумма: {total} 🎲"
    
    async def _random_number(self, command: str) -> str:
        """Генерирует случайное число."""
        # По умолчанию 1-100
        min_val, max_val = 1, 100
        
        # Проверяем диапазон
        range_match = re.search(r'от\s*(\d+)\s*до\s*(\d+)', command)
        if range_match:
            min_val, max_val = int(range_match.group(1)), int(range_match.group(2))
        
        # Корректируем
        if min_val > max_val:
            min_val, max_val = max_val, min_val
        
        # Генерируем
        number = random.randint(min_val, max_val)
        sound = random.choice(["*думаю*", "*выбираю*"])
        
        if min_val == 1 and max_val == 100:
            return f"{sound} Число от 1 до 100: {number}! 🔢"
        else:
            return f"{sound} Число от {min_val} до {max_val}: {number}! 🔢"