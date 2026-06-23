import subprocess
import platform
from pathlib import Path


SYSTEM = platform.system().lower()


WINDOWS_APPS = {
    "блокнот": r"C:\Windows\System32\notepad.exe",
    "notepad": r"C:\Windows\System32\notepad.exe",

    "калькулятор": "calc.exe",
    "calculator": "calc.exe",

    "paint": "mspaint.exe",
    "пэйнт": "mspaint.exe",

    "проводник": "explorer.exe",
    "папка": "explorer.exe",
    "explorer": "explorer.exe",

    "хром": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "браузер": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",

    "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",

    "vscode": r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "vs code": r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "visual studio code": r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
}


def normalize_app_name(text: str) -> str:
    return (
        text.lower()
        .replace("приложение", "")
        .replace("программу", "")
        .replace("пожалуйста", "")
        .strip()
    )


def open_app(app_name: str) -> str:
    app_name = normalize_app_name(app_name)

    if SYSTEM != "windows":
        return "Пока открытие приложений настроено только для Windows."

    command = WINDOWS_APPS.get(app_name)

    if not command:
        available = ", ".join(sorted(WINDOWS_APPS.keys()))
        return f"Я пока не умею открывать «{app_name}». Доступные приложения: {available}."

    command = command.replace("%USERNAME%", Path.home().name)

    try:
        subprocess.Popen([command], shell=False)
        return f"Открываю {app_name}."

    except FileNotFoundError:
        return f"Не нашёл файл приложения для «{app_name}». Проверь путь в actions.py."

    except Exception as e:
        print("Ошибка открытия приложения:", e)
        return f"Не получилось открыть {app_name}."