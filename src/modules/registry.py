from .introducing import IntroducingModule
from .alarm import AlarmModule
from .sleep import SleepModule
from typing import List, Type
from src.modules.module import Module

def get_all_modules() -> List[Type[Module]]:
    """Возвращает список всех модулей для регистрации."""
    return [
        IntroducingModule,
        AlarmModule,
        SleepModule,
    ]

def register_all_modules(astra_manager):
    """Регистрирует все модули в менеджере модулей."""
    module_classes = get_all_modules()
    
    registered_modules = []
    for module_class in module_classes:
        try:
            module_instance = module_class(astra_manager)
            astra_manager.module_manager.register_module(module_instance)
            registered_modules.append(module_instance.get_name())
        except Exception as e:
            print(f"[Registry] Ошибка при регистрации модуля {module_class.__name__}: {e}")
    
    print(f"[Registry] Успешно зарегистрировано модулей: {len(registered_modules)}")
    # print(f"[Registry] Модули: {', '.join(registered_modules)}")