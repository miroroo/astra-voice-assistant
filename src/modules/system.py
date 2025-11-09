from datetime import datetime
import os
import platform
import pyautogui
import subprocess
import asyncio
from pathlib import Path
from typing import Optional, Dict, List
from .module import Module

class SystemModule(Module):
    def __init__(self, astra_manager):
        super().__init__(astra_manager)
        self.module_name = "SystemModule"  # Добавляем имя модуля для контекстов
        self.state_manager = self.astra_manager.get_state_manager()
        self.event_bus = self.astra_manager.get_event_bus()
        
        self.supported_commands = [
            "скриншот", "снимок экрана",
            "открой", "запусти", "открыть",
            "закрой", "заверши", "выход",
            "громкость", "звук",
            "выключи компьютер", "перезагрузка",
            "блокировка", "рабочий стол",
            "список приложений", "активные приложения",
            "информация о системе", "состояние системы"
        ]
        
        self.screenshots_folder = self._get_screenshots_folder()
        self.system_type = platform.system().lower()
        
        # Словарь приложений
        self.applications = self._get_applications_map()
        
        # Отслеживаем открытые приложения
        self.opened_apps = {}
        
        # Подписка на события
        self.event_bus.subscribe("context_cleared", self.handle_context_cleared)
        self.event_bus.subscribe("shutdown", self.handle_shutdown)
        self.event_bus.subscribe("state_PROCESSING_enter", self.handle_processing_enter)

    async def handle_processing_enter(self, data=None):
        """Активируем контекст при начале обработки команды"""
        if self.state_manager.is_context_active(self.module_name):
            self.state_manager.extend_context_timeout(self.module_name)

    async def can_handle(self, command: str) -> bool:
        normalized_command = command.lower()
        if any(cmd in normalized_command for cmd in self.supported_commands):
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
        normalized_command = command.lower()
        
        # Сохраняем команду в контексте
        self.state_manager.set_module_data(self.module_name, "last_command", command)
        
        try:
            if any(cmd in normalized_command for cmd in ["скриншот", "снимок экрана"]):
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
            
            elif any(cmd in normalized_command for cmd in ["открой", "запусти", "открыть"]):
                return await self.open_application(command)
            
            elif any(cmd in normalized_command for cmd in ["закрой", "заверши", "выход"]):
                return await self.close_application(command)
            
            elif any(cmd in normalized_command for cmd in ["громкость", "звук"]):
                return await self.control_volume(command)
            
            elif "выключи компьютер" in normalized_command:
                return await self.shutdown_computer()
            
            elif "перезагрузка" in normalized_command:
                return await self.reboot_computer()
            
            elif "блокировка" in normalized_command:
                return await self.lock_screen()
            
            elif "рабочий стол" in normalized_command:
                return await self.show_desktop()
            
            elif any(cmd in normalized_command for cmd in ["список приложений", "активные приложения"]):
                return await self.list_applications()
            
            elif any(cmd in normalized_command for cmd in ["информация о системе", "состояние системы"]):
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
                process = subprocess.Popen(app_command, shell=True)
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
        
        if app_name in self.opened_apps:
            try:
                process = self.opened_apps[app_name]
                process.terminate()
                del self.opened_apps[app_name]
                
                # Удаляем из контекста
                self.state_manager.clear_module_data(self.module_name, f"opened_{app_name}")
                
                await self.event_bus.publish_async("application_closed", {
                    "app_name": app_name,
                    "process_id": process.pid
                })
                
                return f"Приложение '{app_name}' успешно закрыто"
            except Exception as e:
                return f"Ошибка при закрытии '{app_name}': {str(e)}"
        
        try:
            if self.system_type == "windows":
                subprocess.run(f"taskkill /f /im {app_name}.exe", shell=True)
            elif self.system_type == "linux":
                subprocess.run(["pkill", app_name])
            elif self.system_type == "darwin":
                subprocess.run(["pkill", app_name])
            
            await self.event_bus.publish_async("application_closed", {"app_name": app_name})
            return f"Попытка закрыть приложение '{app_name}'"
        except Exception as e:
            return f"Не удалось закрыть приложение '{app_name}': {str(e)}"

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
        command_lower = command.lower()
        
        # Удаляем команды открытия/закрытия
        open_patterns = ["открой", "запусти", "открыть"]
        close_patterns = ["закрой", "заверши", "выход"]
        
        for pattern in open_patterns + close_patterns:
            if pattern in command_lower:
                # Извлекаем часть после команды
                name_part = command.split(pattern, 1)[-1].strip()
                if name_part:
                    return name_part
        
        return ""
    

    def _get_applications_map(self) -> Dict[str, Dict[str, str]]:
       """Возвращает словарь приложений для разных операционных систем."""
       applications = {
            "блокнот": {
            "windows": "notepad",
            "linux": "gedit",  # или "kate", "leafpad" в зависимости от DE
            "darwin": "TextEdit"
            },
        "калькулятор": {
            "windows": "calc",
            "linux": "gnome-calculator",  # или "kcalc", "qalculate-gtk"
            "darwin": "Calculator"
            },
        "проводник": {
            "windows": "explorer",
            "linux": "nautilus",  # или "dolphin", "thunar"
            "darwin": "Finder"
            },
        "браузер": {
            "windows": "start chrome",  # или "start firefox", "start msedge"
            "linux": "google-chrome",   # или "firefox", "chromium-browser"
            "darwin": "open -a 'Google Chrome'"
            },
        "chrome": {
            "windows": "chrome",
            "linux": "google-chrome",
            "darwin": "open -a 'Google Chrome'"
            },
        "firefox": {
            "windows": "firefox",
            "linux": "firefox",
            "darwin": "open -a Firefox"
            },
        "word": {
            "windows": "winword",
            "linux": "libreoffice",  # альтернатива
            "darwin": "open -a 'Microsoft Word'"
            },
        "excel": {
            "windows": "excel",
            "linux": "libreoffice",  # альтернатива
            "darwin": "open -a 'Microsoft Excel'"
            },
        "панель управления": {
            "windows": "control",
            "linux": "gnome-control-center",
            "darwin": "system-preferences"
            },
        "диспетчер задач": {
            "windows": "taskmgr",
            "linux": "gnome-system-monitor",
            "darwin": "Activity Monitor"
            },
        "терминал": {
            "windows": "cmd",
            "linux": "gnome-terminal",  # или "konsole", "xterm"
            "darwin": "Terminal"
            },
        "камера": {
            "windows": "start microsoft.windows.camera:",
            "linux": "cheese",  # или "guvcview"
            "darwin": "Photo Booth"
            },
        "пaint": {
            "windows": "mspaint",
            "linux": "kolourpaint",  # или "gimp", "pinta"
            "darwin": "Preview"  # может открывать и редактировать изображения
            },
        "музыка": {
            "windows": "start mswindowsmusic:",
            "linux": "rhythmbox",  # или "amarok", "clementine"
            "darwin": "open -a Music"
            },
        "видео": {
            "windows": "start mswindowsvideo:",
            "linux": "vlc",  # или "smplayer"
            "darwin": "open -a 'QuickTime Player'"
            },
        "календарь": {
            "windows": "outlookcal:",
            "linux": "gnome-calendar",
            "darwin": "open -a Calendar"
            },
        "почта": {
            "windows": "outlookmail:",
            "linux": "thunderbird",
            "darwin": "open -a Mail"
            }
        }
    
        # Дополнительные приложения для конкретных ОС
       if self.system_type == "windows":
             applications.update({
            "панель управления": "control",
            "диспетчер устройств": "devmgmt.msc",
            "настройки": "start ms-settings:",
            "блокнот++": "notepad++",  # если установлен
             })
       elif self.system_type == "linux":
            applications.update({
            "файлы": "nautilus",
            "настройки": "gnome-control-center",
            "текстовый редактор": "gedit",
            })
       elif self.system_type == "darwin":
            applications.update({
            "настройки": "system-preferences",
            "фото": "open -a Photos",
            "сообщения": "open -a Messages",
            })
    
       return applications

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

    async def handle_context_cleared(self, module_name: str = None):
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
                    print(f"Ошибка при закрытии {app_name}: {e}")
            self.opened_apps.clear()

    async def handle_shutdown(self, data=None):
        """Обработчик выключения системы"""
        await self.handle_context_cleared()

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
            # Восстанавливаем только имена, процессы нельзя сериализовать
            self.opened_apps = {app: None for app in context["opened_apps"]}