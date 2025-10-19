import asyncio
from src.manager import AstraManager

async def main():
    """Главная функция приложения."""
    astra_manager = AstraManager()
    try:
        await astra_manager.start()
        # Ждем завершения работы ядра
        while astra_manager.core._running:
            await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        print("\nЗавершение работы по запросу пользователя")
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        await astra_manager.stop()

if __name__ == "__main__":
    asyncio.run(main())