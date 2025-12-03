import asyncio
import sys
from src.manager import AstraManager
import logging

async def main():
    """Главная функция приложения."""
    astra_manager = AstraManager()
    logger = logging.getLogger(__name__)

    try:
        await astra_manager.start()
        while astra_manager.core._running:
            await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        logger.critical("\nЗавершение работы по запросу пользователя")
    except Exception as e:
        logger.critical(f"Ошибка: {e}")
    finally:
        await astra_manager.stop()

if __name__ == "__main__":
    asyncio.run(main())