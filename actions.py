import re
import subprocess
import platform

SYSTEM = platform.system().lower()


WINDOWS_APPS = {
    "блокнот": ["notepad.exe"],
    "notepad": ["notepad.exe"],

    "калькулятор": ["calc.exe"],
    "calculator": ["calc.exe"],

    "paint": ["mspaint.exe"],
    "пэйнт": ["mspaint.exe"],

    "проводник": ["explorer.exe"],
    "explorer": ["explorer.exe"],

    "хром": ["cmd", "/c", "start", "", "chrome"],
    "chrome": ["cmd", "/c", "start", "", "chrome"],
    "браузер": ["cmd", "/c", "start", "", "chrome"],

    "edge": ["cmd", "/c", "start", "", "msedge"],

    "vscode": ["cmd", "/c", "start", "", "code"],
    "vs code": ["cmd", "/c", "start", "", "code"],
    "visual studio code": ["cmd", "/c", "start", "", "code"],
}


def normalize_app_name(text: str) -> str:
    text = text.lower().strip()

    # убираем пунктуацию: chrome. -> chrome
    text = re.sub(r"[^\w\sа-яА-ЯёЁ-]", " ", text)

    trash_words = [
        "приложение",
        "программу",
        "пожалуйста",
        "мне",
        "давай",
        "можешь",
        "можно",
        "надо",
        "нужно",
    ]

    for word in trash_words:
        text = text.replace(word, " ")

    text = re.sub(r"\s+", " ", text).strip()

    return text


def open_app(app_name: str) -> str:
    if SYSTEM != "windows":
        return "Пока открытие приложений настроено только для Windows."

    app_name = normalize_app_name(app_name)

    print("OPEN APP NORMALIZED:", repr(app_name))

    command = WINDOWS_APPS.get(app_name)

    if not command:
        available = ", ".join(sorted(WINDOWS_APPS.keys()))
        return f"Я пока не умею открывать «{app_name}». Доступные приложения: {available}."

    try:
        subprocess.Popen(command, shell=False)
        return f"Открываю {app_name}."

    except FileNotFoundError:
        return f"Не нашёл приложение «{app_name}». Проверь команду запуска: {command}."

    except Exception as e:
        print("Ошибка открытия приложения:", e)
        return f"Не получилось открыть {app_name}."