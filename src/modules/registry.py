from src.modules.introducig import IntroducingModule


def register_all_modules(module_manager):
    """Регистрирует все модули в менеджере модулей."""
    
    # Регистрируем модуль представления
    introducing_module = IntroducingModule(system_name="Астра", version="1.0")
    module_manager.register_module(introducing_module)
    
    # Регистрируйте другие модули здесь
    # weather_module = WeatherModule()
    # module_manager.register_module(weather_module)
    
    print(f"[Registry] Всего зарегистрировано модулей: {len(module_manager.modules)}")