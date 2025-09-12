class Context:
    """Контейнер для общих данных и зависимостей ядра."""
    
    def __init__(self):
        self.config = {}  # Конфигурация приложения
        self.services = {}  # Сервисы (например, голосовой движок)
        self.data = {}  # Общие данные
        self.core_instance = None  # Ссылка на экземпляр Core

    def set(self, key, value):
        """Установить значение в контекст."""
        self.data[key] = value

    def get(self, key, default=None):
        """Получить значение из контекста."""
        return self.data.get(key, default)