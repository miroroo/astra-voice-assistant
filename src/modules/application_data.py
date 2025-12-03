applications_data = {
        # Браузеры
        "браузер": {
            "windows": "chrome",
            "linux": "google-chrome",
            "darwin": "open -a 'Google Chrome'",
            "processes": ["chrome.exe", "msedge.exe", "firefox.exe"]
        },
        "хром": {
            "windows": "chrome",
            "linux": "google-chrome", 
            "darwin": "open -a 'Google Chrome'",
            "processes": ["chrome.exe", "google-chrome"]
        },
        "chrome": {
            "windows": "chrome",
            "linux": "google-chrome",
            "darwin": "open -a 'Google Chrome'", 
            "processes": ["chrome.exe", "google-chrome"]
        },
        "гугл хром": {
            "windows": "chrome",
            "linux": "google-chrome",
            "darwin": "open -a 'Google Chrome'",
            "processes": ["chrome.exe", "google-chrome"]
        },
        "файрфокс": {
            "windows": "firefox",
            "linux": "firefox",
            "darwin": "open -a Firefox",
            "processes": ["firefox.exe", "firefox"]
        },
        "firefox": {
            "windows": "firefox", 
            "linux": "firefox",
            "darwin": "open -a Firefox",
            "processes": ["firefox.exe", "firefox"]
        },
        "эдж": {
            "windows": "start msedge",
            "linux": "microsoft-edge", 
            "darwin": "open -a 'Microsoft Edge'",
            "processes": ["msedge.exe", "MicrosoftEdge.exe"]
        },
        "edge": {
            "windows": "start msedge",
            "linux": "microsoft-edge",
            "darwin": "open -a 'Microsoft Edge'",
            "processes": ["msedge.exe", "MicrosoftEdge.exe"]
        },
        "опера": {
            "windows": "opera",
            "linux": "opera",
            "darwin": "open -a Opera",
            "processes": ["opera.exe", "opera"]
        },
        
        # Текстовые редакторы и IDE
        "вскод": {
            "windows": "code",
            "linux": "code",
            "darwin": "open -a 'Visual Studio Code'",
            "processes": ["code.exe", "code"]
        },
        "vscode": {
            "windows": "code",
            "linux": "code",
            "darwin": "open -a 'Visual Studio Code'",
            "processes": ["code.exe", "code"]
        },
        "вижуал студио код": {
            "windows": "code",
            "linux": "code",
            "darwin": "open -a 'Visual Studio Code'",
            "processes": ["code.exe", "code"]
        },
        "блокнот": {
            "windows": "notepad",
            "linux": "gedit",
            "darwin": "TextEdit",
            "processes": ["notepad.exe", "gedit", "TextEdit"]
        },
        "notepad": {
            "windows": "notepad",
            "linux": "gedit",
            "darwin": "TextEdit",
            "processes": ["notepad.exe", "gedit", "TextEdit"]
        },
        "notepad++": {
            "windows": "notepad++",
            "linux": "notepadqq",
            "darwin": "",
            "processes": ["notepad++.exe", "notepadqq"]
        },
        "sublime": {
            "windows": "sublime_text",
            "linux": "sublime_text",
            "darwin": "open -a 'Sublime Text'",
            "processes": ["sublime_text.exe", "sublime_text"]
        },
        "атом": {
            "windows": "atom",
            "linux": "atom",
            "darwin": "open -a Atom",
            "processes": ["atom.exe", "atom"]
        },
        "пайчарм": {
            "windows": "pycharm",
            "linux": "pycharm",
            "darwin": "open -a 'PyCharm CE'",
            "processes": ["pycharm.exe", "pycharm"]
        },
        "intellij": {
            "windows": "idea",
            "linux": "idea",
            "darwin": "open -a 'IntelliJ IDEA CE'",
            "processes": ["idea.exe", "idea"]
        },
        
        # Офисные приложения
        "ворд": {
            "windows": "winword",
            "linux": "libreoffice",
            "darwin": "open -a 'Microsoft Word'",
            "processes": ["winword.exe", "Microsoft Word"]
        },
        "word": {
            "windows": "winword",
            "linux": "libreoffice", 
            "darwin": "open -a 'Microsoft Word'",
            "processes": ["winword.exe", "Microsoft Word"]
        },
        "ексель": {
            "windows": "excel",
            "linux": "libreoffice",
            "darwin": "open -a 'Microsoft Excel'", 
            "processes": ["excel.exe", "Microsoft Excel"]
        },
        "excel": {
            "windows": "excel",
            "linux": "libreoffice",
            "darwin": "open -a 'Microsoft Excel'",
            "processes": ["excel.exe", "Microsoft Excel"]
        },
        "повер поинт": {
            "windows": "powerpnt",
            "linux": "libreoffice",
            "darwin": "open -a 'Microsoft PowerPoint'",
            "processes": ["powerpnt.exe", "Microsoft PowerPoint"]
        },
        "powerpoint": {
            "windows": "powerpnt",
            "linux": "libreoffice",
            "darwin": "open -a 'Microsoft PowerPoint'",
            "processes": ["powerpnt.exe", "Microsoft PowerPoint"]
        },
        "офис": {
            "windows": "winword",
            "linux": "libreoffice",
            "darwin": "open -a 'Microsoft Word'",
            "processes": ["winword.exe", "excel.exe", "powerpnt.exe"]
        },
        "libreoffice": {
            "windows": "libreoffice",
            "linux": "libreoffice",
            "darwin": "open -a 'LibreOffice'",
            "processes": ["libreoffice.exe", "libreoffice"]
        },
        "openoffice": {
            "windows": "soffice",
            "linux": "soffice",
            "darwin": "open -a 'OpenOffice'",
            "processes": ["soffice.exe", "soffice"]
        },
        
        # Системные утилиты
        "проводник": {
            "windows": "explorer",
            "linux": "nautilus",
            "darwin": "Finder",
            "processes": ["explorer.exe", "nautilus"]
        },
        "панель управления": {
            "windows": "control",
            "linux": "gnome-control-center",
            "darwin": "system-preferences",
            "processes": ["control.exe", "gnome-control-center"]
        },
        "диспетчер задач": {
            "windows": "taskmgr",
            "linux": "gnome-system-monitor",
            "darwin": "Activity Monitor",
            "processes": ["taskmgr.exe", "gnome-system-monitor"]
        },
        "терминал": {
            "windows": "cmd",
            "linux": "gnome-terminal",
            "darwin": "Terminal", 
            "processes": ["cmd.exe", "powershell.exe", "gnome-terminal", "Terminal"]
        },
        "командная строка": {
            "windows": "cmd",
            "linux": "gnome-terminal",
            "darwin": "Terminal",
            "processes": ["cmd.exe", "powershell.exe", "gnome-terminal"]
        },
        "повершел": {
            "windows": "powershell",
            "linux": "pwsh",
            "darwin": "pwsh",
            "processes": ["powershell.exe", "pwsh"]
        },
        "настройки": {
            "windows": "start ms-settings:",
            "linux": "gnome-control-center",
            "darwin": "system-preferences",
            "processes": ["systemsettings.exe", "gnome-control-center"]
        },
        
        # Мультимедиа
        "калькулятор": {
            "windows": "calc",
            "linux": "gnome-calculator", 
            "darwin": "Calculator",
            "processes": ["calculator.exe", "calc.exe", "gnome-calculator"]
        },
        "камера": {
            "windows": "start microsoft.windows.camera:",
            "linux": "cheese",
            "darwin": "Photo Booth",
            "processes": ["windows.camera.exe", "cheese"]
        },
        "пэйнт": {
            "windows": "mspaint",
            "linux": "kolourpaint",
            "darwin": "Preview",
            "processes": ["mspaint.exe", "kolourpaint"]
        },
        "фотографии": {
            "windows": "start ms-photos:",
            "linux": "shotwell",
            "darwin": "open -a Photos",
            "processes": ["photos.exe", "shotwell"]
        },
        "музыка": {
            "windows": "start mswindowsmusic:",
            "linux": "rhythmbox",
            "darwin": "open -a Music",
            "processes": ["msedge.exe", "spotify.exe", "rhythmbox"]
        },
        "видео": {
            "windows": "start mswindowsvideo:",
            "linux": "vlc",
            "darwin": "open -a 'QuickTime Player'",
            "processes": ["vlc.exe", "wmplayer.exe"]
        },
        "vlc": {
            "windows": "vlc",
            "linux": "vlc",
            "darwin": "open -a VLC",
            "processes": ["vlc.exe", "vlc"]
        },
        "media player": {
            "windows": "wmplayer",
            "linux": "vlc",
            "darwin": "open -a 'QuickTime Player'",
            "processes": ["wmplayer.exe", "vlc"]
        },
        "кино": {
            "windows": "start mswindowsvideo:",
            "linux": "vlc",
            "darwin": "open -a 'QuickTime Player'",
            "processes": ["vlc.exe", "wmplayer.exe"]
        },
        "плеер": {
            "windows": "wmplayer",
            "linux": "vlc",
            "darwin": "open -a VLC",
            "processes": ["vlc.exe", "wmplayer.exe", "vlc"]
        },
        
        # Коммуникации
        "почта": {
            "windows": "outlookmail:",
            "linux": "thunderbird",
            "darwin": "open -a Mail",
            "processes": ["outlook.exe", "thunderbird"]
        },
        "аутлук": {
            "windows": "outlook",
            "linux": "thunderbird",
            "darwin": "open -a 'Microsoft Outlook'",
            "processes": ["outlook.exe", "thunderbird"]
        },
        "thunderbird": {
            "windows": "thunderbird",
            "linux": "thunderbird",
            "darwin": "open -a Thunderbird",
            "processes": ["thunderbird.exe", "thunderbird"]
        },
        "телеграм": {
            "windows": "telegram",
            "linux": "telegram-desktop",
            "darwin": "open -a Telegram",
            "processes": ["telegram.exe", "telegram-desktop"]
        },
        "telegram": {
            "windows": "start telegram://",
            "linux": "telegram-desktop",
            "darwin": "open -a Telegram",
            "processes": ["telegram.exe", "telegram-desktop"]
        },
        "дискорд": {
            "windows": "discord", 
            "linux": "discord",
            "darwin": "open -a Discord",
            "processes": ["discord.exe", "discord"]
        },
        "скайп": {
            "windows": "skype",
            "linux": "skype",
            "darwin": "open -a Skype",
            "processes": ["skype.exe", "skype"]
        },
        "зум": {
            "windows": "zoom",
            "linux": "zoom",
            "darwin": "open -a Zoom",
            "processes": ["zoom.exe", "zoom"]
        },
        "тимс": {
            "windows": "teams",
            "linux": "teams",
            "darwin": "open -a 'Microsoft Teams'",
            "processes": ["teams.exe", "teams"]
        },
        "ватсап": {
            "windows": "whatsapp",
            "linux": "whatsapp-desktop",
            "darwin": "open -a WhatsApp",
            "processes": ["whatsapp.exe", "whatsapp-desktop"]
        },
        
        # Утилиты и инструменты
        "календарь": {
            "windows": "outlookcal:",
            "linux": "gnome-calendar",
            "darwin": "open -a Calendar",
            "processes": ["outlook.exe", "gnome-calendar"]
        },
        "заметки": {
            "windows": "sticky",
            "linux": "gnome-sticky-notes",
            "darwin": "open -a Notes",
            "processes": ["stikynot.exe", "gnome-sticky-notes"]
        },
        "напоминания": {
            "windows": "",
            "linux": "gnome-todo",
            "darwin": "open -a Reminders",
            "processes": ["gnome-todo"]
        },
        "диск": {
            "windows": "explorer",
            "linux": "nautilus",
            "darwin": "Finder",
            "processes": ["explorer.exe", "nautilus"]
        },
        "корзина": {
            "windows": "explorer shell:RecycleBinFolder",
            "linux": "nautilus trash://",
            "darwin": "open -a Finder /Users/$(whoami)/.Trash",
            "processes": ["explorer.exe", "nautilus"]
        },
        
        # Игры и развлечения
        "стим": {
            "windows": "start steam://",
            "linux": "steam",
            "darwin": "open -a Steam",
            "processes": ["steam.exe", "steam"]
        },
        "steam": {
            "windows": "start steam://",
            "linux": "steam",
            "darwin": "open -a Steam",
            "processes": ["steam.exe", "steam"]
        },
        "игры": {
            "windows": "start ms-gamingoverlay:",
            "linux": "steam",
            "darwin": "open -a Steam",
            "processes": ["steam.exe", "gamebar.exe"]
        },
        
        # Графические редакторы
        "photoshop": {
            "windows": "photoshop",
            "linux": "gimp",
            "darwin": "open -a Photoshop",
            "processes": ["photoshop.exe", "gimp"]
        },
        "gimp": {
            "windows": "gimp",
            "linux": "gimp",
            "darwin": "open -a GIMP",
            "processes": ["gimp.exe", "gimp"]
        },
        "рисование": {
            "windows": "mspaint",
            "linux": "kolourpaint",
            "darwin": "Preview",
            "processes": ["mspaint.exe", "kolourpaint"]
        },
        
        # Файловые менеджеры
        "файлы": {
            "windows": "explorer",
            "linux": "nautilus",
            "darwin": "Finder",
            "processes": ["explorer.exe", "nautilus"]
        },
        "проводник windows": {
            "windows": "explorer",
            "linux": "nautilus",
            "darwin": "Finder",
            "processes": ["explorer.exe", "nautilus"]
        },
        
        # Разное
        "адресная книга": {
            "windows": "wab",
            "linux": "evolution",
            "darwin": "open -a Contacts",
            "processes": ["wab.exe", "evolution"]
        },
        "контакты": {
            "windows": "wab",
            "linux": "evolution",
            "darwin": "open -a Contacts",
            "processes": ["wab.exe", "evolution"]
        }
}
    