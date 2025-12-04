import logging

from .deepseek import DeepSeekModule
from .calendar import CalendarModule
from .dialog import DialogModule
from .jokes import JokeModule
from .news import NewsModule
from .play import RandomModule
from .system import SystemModule
from .weather import WeatherModule
from .introducing import IntroducingModule
from .alarm import AlarmModule
from .sleep import SleepModule
from .module import Module

from typing import List, Type


def get_all_modules() -> List[Type[Module]]:
    """Возвращает список всех модулей для регистрации."""
    return [
        IntroducingModule,
        AlarmModule,
        SleepModule,
        WeatherModule,
        SystemModule,
        CalendarModule,
        DialogModule,
        RandomModule,
        NewsModule,
        JokeModule,



        DeepSeekModule,
    ]

def register_all_modules(astra_manager):
    """Регистрирует все модули в менеджере модулей."""
    module_classes = get_all_modules()
    logger = logging.getLogger(__name__)
    
    registered_modules = []
    for module_class in module_classes:
        try:
            module_instance = module_class(astra_manager)
            astra_manager.module_manager.register_module(module_instance)
            registered_modules.append(module_instance.get_name())
        except Exception as e:
            logger.critical(f"[Registry] Ошибка при регистрации модуля {module_class.__name__}: {e}")
    
    logger.info(f"[Registry] Успешно зарегистрировано модулей: {len(registered_modules)}")
