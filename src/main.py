import asyncio
from src.manager import AstraManager

async def main():
    """Главная функция приложения."""
    try:
        # Создаем и запускаем ядро
        astra_core = AstraManager()
        await astra_core.start()
        print(f"Текущее состояние: {astra_core.get_state()}")
        
        # Главный цикл (можно заменить на что-то более сложное)
        while astra_core.core._running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\nЗавершение работы по запросу пользователя")
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        if "astra_core" in locals():
            await astra_core.core.shutdown()


if __name__ == "__main__":
    asyncio.run(main())