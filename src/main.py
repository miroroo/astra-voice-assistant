from .manager import AstraManager
import time
import asyncio

async def main():
    """Главная функция приложения."""
    try:
        # Создаем и запускаем ядро
        astra_core = AstraManager()
        astra_core.start()
        print(f"Текущее состояние: {astra_core.get_state()}")
        TEST_MODE = True


        # Главный цикл (можно заменить на что-то более сложное)
        while True:
            if TEST_MODE:
                # Тестовый ввод
                await astra_core.force_state_change("LISTENING")
                await astra_core.force_state_change("PROCESSING")
                break
            else:
                # Реальный голосовой ввод
                pass

                
            
    except KeyboardInterrupt:
        print("\nЗавершение работы по запросу пользователя")
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        if 'astra_core' in locals():
            astra_core.core.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
    