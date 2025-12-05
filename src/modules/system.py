from datetime import datetime
import logging
import os
import platform
import pyautogui
import subprocess
import asyncio
from pathlib import Path
from typing import Optional, Dict, List

from src.modules.application_data import applications_data
from .module import Module

class SystemModule(Module):
    def __init__(self, astra_manager):
        super().__init__(astra_manager)
        self.module_name = self.get_name()
        self.state_manager = self.astra_manager.get_state_manager()
        self.event_bus = self.astra_manager.get_event_bus()
        self.logger = logging.getLogger(__name__)
        
        self.supported_commands = [
            "скриншот", "снимок экрана",
            "открой", "запусти", "открыть", "включи", "включить",
            "закрой", "заверши", "выход", "закрыть"
            "громкость", "звук",
            "выключи компьютер", "перезагрузка",
            "блокировка", "рабочий стол",
            "список приложений", "активные приложения",
            "информация о системе", "состояние системы"
        ]
        
        self.screenshots_folder = self._get_screenshots_folder()
        self.system_type = platform.system().lower()
        
        # Словарь приложений
        self.applications = applications_data
        
        # Отслеживаем открытые приложения
        self.opened_apps = {}
        
        # Подписка на события
        self.event_bus.subscribe("context_cleared", self.on_context_cleared)
        self.event_bus.subscribe("shutdown", self.handle_shutdown)
        self.event_bus.subscribe("state_PROCESSING_enter", self.handle_processing_enter)

    async def handle_processing_enter(self, data=None):
        """Активируем контекст при начале обработки команды"""
        if self.state_manager.is_context_active(self.module_name):
            self.state_manager.extend_context_timeout(self.module_name)

    async def can_handle(self, command: str) -> bool:
        if any(cmd in command for cmd in self.supported_commands):
            # Активируем контекст системного модуля с высоким приоритетом
            self.state_manager.set_active_context(
                self.module_name, 
                priority=15,  # Высокий приоритет для системных команд
                context_type="system",
                timeout_seconds=300  # 5 минут
            )
            return True
        return False

    async def execute(self, command: str) -> str:
        
        # Сохраняем команду в контексте
        self.state_manager.set_module_data(self.module_name, "last_command", command)
        
        try:
            if any(cmd in command for cmd in ["скриншот", "снимок экрана"]):
                screenshot_name = self._extract_screenshot_name(command)
                result = await self.take_screenshot(screenshot_name)
                
                # Сохраняем информацию о скриншоте в контексте
                if result["success"]:
                    self.state_manager.set_module_data(
                        self.module_name, 
                        "last_screenshot", 
                        result["filepath"]
                    )
                
                return result["message"]
            
            elif any(cmd in command for cmd in ["открой", "запусти", "открыть", "включи", "включить"]):
                return await self.open_application(command)
            
            elif any(cmd in command for cmd in ["закрой", "заверши", "выход", "закрыть", ]):
                return await self.close_application(command)
            
            elif any(cmd in command for cmd in ["громкость", "звук"]):
                return await self.control_volume(command)
            
            elif "выключи компьютер" in command:
                return await self.shutdown_computer()
            
            elif "перезагрузка" in command:
                return await self.reboot_computer()
            
            elif "блокировка" in command:
                return await self.lock_screen()
            
            elif "рабочий стол" in command:
                return await self.show_desktop()
            
            elif any(cmd in command for cmd in ["список приложений", "активные приложения"]):
                return await self.list_applications()
            
            elif any(cmd in command for cmd in ["информация о системе", "состояние системы"]):
                return await self.get_system_info()
            
            return "Не удалось обработать команду системы"
            
        except Exception as e:
            # Сохраняем ошибку в контексте
            self.state_manager.set_module_data(self.module_name, "last_error", str(e))
            return f"Ошибка выполнения команды: {str(e)}"

    async def take_screenshot(self, custom_name: Optional[str] = None) -> Dict[str, str]:
        try:
            if custom_name:
                clean_name = self._clean_filename(custom_name)
                filename = f"{clean_name}.png"
            else:
                filename = f"screenshot_{self._get_timestamp()}.png"
            
            filepath = self.screenshots_folder / filename
            
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            
            # Публикуем событие через ваш EventBus
            await self.event_bus.publish_async("screenshot_created", {
                "filepath": str(filepath),
                "filename": filename,
                "timestamp": self._get_timestamp()
            })
            
            if custom_name:
                message = f"Скриншот сохранен как '{custom_name}'"
            else:
                message = f"Скриншот сохранен: {filename}"
            
            return {
                "success": True,
                "message": message,
                "filepath": str(filepath),
                "filename": filename
            }
            
        except Exception as e:
            await self.event_bus.publish_async("screenshot_error", {
                "error": str(e)
            })
            return {
                "success": False,
                "message": f"Ошибка создания скриншота: {str(e)}"
            }

    async def open_application(self, command: str) -> str:
        app_name = self._extract_application_name(command)
        
        if not app_name:
            return "Не указано название приложения для открытия"
        
        app_info = self.applications.get(app_name.lower())
        if not app_info:
            return f"Приложение '{app_name}' не найдено в списке доступных"
        
        app_command = app_info.get(self.system_type)
        if not app_command:
            return f"Приложение '{app_name}' не поддерживается на вашей операционной системе"
        
        try:
            if self.system_type == "windows":
                # process = subprocess.Popen(app_command, shell=True)
                process = subprocess.Popen("start " + app_command, shell=True)
                # process = subprocess.Popen("start " + app_command + "://", shell=True)
                    
            else:
                process = subprocess.Popen([app_command])
            
            self.opened_apps[app_name] = process
            
            # Сохраняем в контексте
            self.state_manager.set_module_data(
                self.module_name, 
                f"opened_{app_name}", 
                process.pid
            )
            
            await self.event_bus.publish_async("application_opened", {
                "app_name": app_name,
                "command": app_command,
                "process_id": process.pid
            })
            
            return f"Приложение '{app_name}' успешно запущено"
            
        except Exception as e:
            await self.event_bus.publish_async("application_error", {
                "app_name": app_name,
                "error": str(e)
            })
            return f"Ошибка при запуске '{app_name}': {str(e)}"

    async def close_application(self, command: str) -> str:
        app_name = self._extract_application_name(command)
    
        if not app_name:
            return "Не указано название приложения для закрытия"
    
        # Сначала пробуем закрыть приложения, запущенные через наш модуль
        if app_name in self.opened_apps:
            try:
                process = self.opened_apps[app_name]
                if process and process.poll() is None:  # Процесс еще работает
                    process.terminate()
                    try:
                        # Ждем завершения процесса
                        await asyncio.wait_for(asyncio.create_task(process.wait()), timeout=5)
                    except asyncio.TimeoutError:
                        # Если не завершился, принудительно закрываем
                        process.kill()
            
                del self.opened_apps[app_name]
            
                # Удаляем из контекста
                self.state_manager.clear_module_data(self.module_name, f"opened_{app_name}")
            
                await self.event_bus.publish_async("application_closed", {"app_name": app_name})
            
                return f"Приложение '{app_name}' успешно закрыто"
            except Exception as e:
                return f"Ошибка при закрытии '{app_name}': {str(e)}"
    
        # Если приложение не было запущено через нас, ищем в applications_data
        app_info = self.applications.get(app_name)
        if not app_info:
            return f"Приложение '{app_name}' не найдено в списке приложений"
    
        # Получаем список процессов для закрытия
        processes_to_kill = app_info.get("processes", [])
        if not processes_to_kill:
            return f"Для приложения '{app_name}' не указаны процессы для закрытия"
    
        success = False
        try:
            if self.system_type == "windows":
                # Для Windows используем taskkill
                for process_name in processes_to_kill:
                    try:
                        result = subprocess.run(
                        f"taskkill /f /im {process_name}", 
                        shell=True, 
                        capture_output=True, 
                        text=True,
                        timeout=10
                        )
                        if result.returncode == 0 or "завершен" in result.stdout.lower():
                            success = True
                            self.logger.info(f"[System] Успешно закрыт процесс: {process_name}")
                    except subprocess.TimeoutExpired:
                        continue
                    except Exception as e:
                        self.logger.error(f"[System] Ошибка при закрытии {process_name}: {e}")
        
            elif self.system_type == "linux":
                #  Для Linux используем pkill
                for process_name in processes_to_kill:
                    try:
                        # Убираем расширение .exe для Linux
                        linux_process_name = process_name.replace('.exe', '')
                        result = subprocess.run(
                        ["pkill", "-f", linux_process_name],
                        capture_output=True,
                        text=True,
                        timeout=10
                        )
                        if result.returncode == 0:
                            success = True
                            self.logger.info(f"[System] Успешно закрыт процесс: {linux_process_name}")
                    except subprocess.TimeoutExpired:
                        continue
                    except Exception as e:
                        self.logger.error(f"[System] Ошибка при закрытии {linux_process_name}: {e}")
                    
        
            await self.event_bus.publish_async("application_closed", {"app_name": app_name})
        
            if success:
                return f"Приложение '{app_name}' успешно закрыто"
            else:
                return f"Не удалось найти запущенное приложение '{app_name}'"
            
        except Exception as e:
            return f"Не удалось закрыть приложение '{app_name}': {str(e)}"
        

    def _get_process_names_for_app(self, app_name: str) -> List[str]:
        """Получить возможные имена процессов для приложения"""
        app_data = self.applications_data.get(app_name.lower())
        if app_data and "processes" in app_data:
            return app_data["processes"]
        return [f"{app_name}.exe", app_name]
    

    def _get_applications_map(self) -> Dict[str, Dict[str, str]]:
        """Возвращает словарь приложений для разных операционных систем."""
        return {name: {k: v for k, v in data.items() if k != "processes"} 
            for name, data in self.applications_data.items()}


    async def get_system_info(self) -> str:
        """Получить информацию о системе"""
        try:
            info = {
                "OS": platform.system(),
                "OS Version": platform.version(),
                "Architecture": platform.architecture()[0],
                "Processor": platform.processor(),
                "Machine": platform.machine(),
                "Active Contexts": len(self.state_manager.get_active_contexts()),
                "Current State": self.state_manager.get_state()
            }
            
            info_str = "\n".join([f"{k}: {v}" for k, v in info.items()])
            
            # Сохраняем информацию в контексте
            self.state_manager.set_module_data(self.module_name, "system_info", info)
            
            return f"Информация о системе:\n{info_str}"
            
        except Exception as e:
            return f"Ошибка получения информации о системе: {str(e)}"

    async def control_volume(self, command: str) -> str:
        """Управление громкостью"""
        normalized_command = command.lower()
        
        try:
            if "громкость вверх" in normalized_command or "звук вверх" in normalized_command or "увеличь громкость" in normalized_command:
                pyautogui.press('volumeup')
                action = "увеличена"
            elif "громкость вниз" in normalized_command or "звук вниз" in normalized_command or "уменьши громкость" in normalized_command:
                pyautogui.press('volumedown')
                action = "уменьшена"
            elif "выключи звук" in normalized_command or "отключи звук" in normalized_command or "без звука" in normalized_command:
                pyautogui.press('volumemute')
                action = "отключен"
            elif "максимум" in normalized_command:
                for _ in range(10):  # Несколько раз для максимума
                    pyautogui.press('volumeup')
                action = "установлена на максимум"
            elif "минимум" in normalized_command:
                for _ in range(10):  # Несколько раз для минимума
                    pyautogui.press('volumedown')
                action = "установлена на минимум"
            else:
                return "Не поняла команду управления громкостью"
            
            await self.event_bus.publish_async("volume_changed", {"action": action})
            return f"Громкость {action}"
            
        except Exception as e:
            return f"Ошибка управления громкостью: {str(e)}"

    async def shutdown_computer(self) -> str:
        """Выключение компьютера"""
        try:
            if self.system_type == "windows":
                os.system("shutdown /s /t 5")
                message = "Компьютер будет выключен через 5 секунд"
            elif self.system_type == "linux":
                os.system("shutdown -h now")
                message = "Компьютер выключается"
            elif self.system_type == "darwin":
                os.system("shutdown -h now")
                message = "Компьютер выключается"
            else:
                return "Операционная система не поддерживается"
            
            await self.event_bus.publish_async("system_shutdown", {})
            return message
            
        except Exception as e:
            return f"Ошибка при выключении: {str(e)}"

    async def reboot_computer(self) -> str:
        """Перезагрузка компьютера"""
        try:
            if self.system_type == "windows":
                os.system("shutdown /r /t 5")
                message = "Компьютер будет перезагружен через 5 секунд"
            elif self.system_type == "linux":
                os.system("reboot")
                message = "Компьютер перезагружается"
            elif self.system_type == "darwin":
                os.system("shutdown -r now")
                message = "Компьютер перезагружается"
            else:
                return "Операционная система не поддерживается"
            
            await self.event_bus.publish_async("system_reboot", {})
            return message
            
        except Exception as e:
            return f"Ошибка при перезагрузке: {str(e)}"

    async def lock_screen(self) -> str:
        """Блокировка экрана"""
        try:
            if self.system_type == "windows":
                os.system("rundll32.exe user32.dll,LockWorkStation")
            elif self.system_type == "linux":
                os.system("gnome-screensaver-command -l")
            elif self.system_type == "darwin":
                os.system("pmset displaysleepnow")
            
            await self.event_bus.publish_async("screen_locked", {})
            return "Экран заблокирован"
            
        except Exception as e:
            return f"Ошибка при блокировке экрана: {str(e)}"

    async def show_desktop(self) -> str:
        """Показать рабочий стол"""
        try:
            if self.system_type == "windows":
                pyautogui.hotkey('win', 'd')
            elif self.system_type == "linux":
                pyautogui.hotkey('ctrl', 'alt', 'd')
            elif self.system_type == "darwin":
                pyautogui.hotkey('command', 'd')
            
            await self.event_bus.publish_async("desktop_shown", {})
            return "Показываю рабочий стол"
            
        except Exception as e:
            return f"Ошибка при показе рабочего стола: {str(e)}"

    async def list_applications(self) -> str:
        """Показать список доступных приложений"""
        available_apps = ", ".join(self.applications.keys())
        return f"Доступные приложения: {available_apps}"

    def _extract_application_name(self, command: str) -> str:
        """Извлечение названия приложения из команды"""   
        # Удаляем команды открытия/закрытия
        open_patterns = ["открой", "запусти", "открыть", "включи", "открыть"]
        close_patterns = ["закрой", "заверши", "выход", "закрыть"]
        
        for pattern in open_patterns + close_patterns:
            if pattern in command:
                # Извлекаем часть после команды
                name_part = command.split(pattern, 1)[-1].strip()
                if name_part:
                    return name_part
        
        return ""
    

    def _extract_screenshot_name(self, command: str) -> Optional[str]:
        """Извлечение названия скриншота из команды"""
        command_lower = command.lower()
        
        patterns = [
            "скриншот с названием",
            "снимок с названием", 
            "скриншот назови",
            "снимок назови",
            "скриншот как",
            "снимок как"
        ]
        
        for pattern in patterns:
            if pattern in command_lower:
                name_part = command.split(pattern, 1)[-1].strip()
                if name_part:
                    return name_part
        
        return None

    def _clean_filename(self, filename: str) -> str:
        """Очистка имени файла от запрещенных символов"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename.strip()
    
    def _get_timestamp(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _get_screenshots_folder(self) -> Path:
        """Определяем папку для скриншотов в Pictures"""
        pictures = Path.home() / "Pictures"
        screenshots_dir = pictures / "Скриншоты Астра"
        screenshots_dir.mkdir(exist_ok=True)
        return screenshots_dir

    async def on_context_cleared(self, module_name: str = None):
        """Обработчик очистки контекста - адаптирован под вашу систему"""
        # Очищаем только если это наш модуль или очищаются все контексты
        if module_name is None or module_name == self.module_name:
            for app_name, process in list(self.opened_apps.items()):
                try:
                    process.terminate()
                    await self.event_bus.publish_async("application_closed", {
                        "app_name": app_name,
                        "reason": "context_cleared"
                    })
                except Exception as e:
                    self.logger.critical(f"[System] Ошибка при закрытии {app_name}: {e}")
            self.opened_apps.clear()

    async def handle_shutdown(self, data=None):
        """Обработчик выключения системы"""
        await self.on_context_cleared()

    def get_module_context(self) -> Dict:
        """Получить контекст модуля для отладки"""
        return {
            "module_name": self.module_name,
            "opened_apps": list(self.opened_apps.keys()),
            "screenshots_folder": str(self.screenshots_folder),
            "system_type": self.system_type,
            "supported_commands": self.supported_commands
        }

    def get_context(self) -> Dict:
        """Получить текущий контекст модуля"""
        return {
            "opened_apps": list(self.opened_apps.keys()),
            "screenshots_folder": str(self.screenshots_folder),
            "system_type": self.system_type
        }

    def set_context(self, context: Dict):
        """Установить контекст модуля"""
        if "opened_apps" in context:
            self.opened_apps = {app: None for app in context["opened_apps"]}