import re
import time
from dataclasses import dataclass

import psutil
import pyautogui
import win32con
import win32gui
import win32process


@dataclass
class WindowInfo:
    hwnd: int
    title: str
    pid: int | None
    process_name: str
    exe_path: str


APP_ALIASES = {
    # browsers
    "chrome": ["chrome.exe"],
    "google chrome": ["chrome.exe"],
    "хром": ["chrome.exe"],
    "гугл хром": ["chrome.exe"],
    "браузер": ["chrome.exe", "msedge.exe", "firefox.exe"],

    "edge": ["msedge.exe"],
    "эдж": ["msedge.exe"],

    "firefox": ["firefox.exe"],
    "фаерфокс": ["firefox.exe"],

    # messengers
    "telegram": ["telegram.exe"],
    "телеграм": ["telegram.exe"],
    "телега": ["telegram.exe"],

    "discord": ["discord.exe"],
    "дискорд": ["discord.exe"],

    # editors / IDE
    "vscode": ["code.exe"],
    "vs code": ["code.exe"],
    "visual studio code": ["code.exe"],
    "ви эс код": ["code.exe"],
    "код": ["code.exe"],

    "pycharm": ["pycharm64.exe", "pycharm.exe"],
    "пайчарм": ["pycharm64.exe", "pycharm.exe"],

    # Windows apps
    "блокнот": ["notepad.exe"],
    "notepad": ["notepad.exe"],

    "проводник": ["explorer.exe"],
    "explorer": ["explorer.exe"],

    "калькулятор": ["calculatorapp.exe", "calc.exe"],
    "calculator": ["calculatorapp.exe", "calc.exe"],

    "paint": ["mspaint.exe"],
    "пэйнт": ["mspaint.exe"],

    # media / stores
    "spotify": ["spotify.exe"],
    "спотифай": ["spotify.exe"],

    "steam": ["steam.exe"],
    "стим": ["steam.exe"],
}


def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\sа-яА-ЯёЁ-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def get_window_process_info(hwnd: int) -> tuple[int | None, str, str]:
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid)

        process_name = process.name().lower()

        try:
            exe_path = process.exe()
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            exe_path = ""

        return pid, process_name, exe_path

    except Exception:
        return None, "", ""


def is_real_window(hwnd: int) -> bool:
    if not win32gui.IsWindowVisible(hwnd):
        return False

    title = win32gui.GetWindowText(hwnd).strip()

    if not title:
        return False

    try:
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bottom - top

        if width <= 50 or height <= 50:
            return False

    except Exception:
        return False

    return True


def get_open_windows() -> list[WindowInfo]:
    windows: list[WindowInfo] = []

    def callback(hwnd, _):
        if not is_real_window(hwnd):
            return

        title = win32gui.GetWindowText(hwnd).strip()
        pid, process_name, exe_path = get_window_process_info(hwnd)

        windows.append(
            WindowInfo(
                hwnd=hwnd,
                title=title,
                pid=pid,
                process_name=process_name,
                exe_path=exe_path,
            )
        )

    win32gui.EnumWindows(callback, None)

    return windows


def get_target_process_names(user_name: str) -> list[str]:
    name = normalize_text(user_name)

    # точное совпадение по алиасу
    if name in APP_ALIASES:
        return [item.lower() for item in APP_ALIASES[name]]

    # частичное совпадение: "открой гугл хром" -> "хром"
    for alias, processes in APP_ALIASES.items():
        if alias in name:
            return [item.lower() for item in processes]

    # если пользователь сказал прямо chrome.exe
    if name.endswith(".exe"):
        return [name]

    return []


def activate_window(hwnd: int) -> bool:
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(0.15)
        win32gui.SetForegroundWindow(hwnd)
        return True
    except Exception as e:
        print("Ошибка SetForegroundWindow:", e)

        try:
            # fallback: Alt+Tab иногда помогает Windows разрешить смену фокуса
            pyautogui.hotkey("alt", "tab")
            time.sleep(0.2)
        except Exception:
            pass

        return False


def list_open_windows() -> str:
    windows = get_open_windows()

    if not windows:
        return "Я не нашёл открытых окон."

    lines = []

    for window in windows[:12]:
        app_name = window.process_name or "неизвестный процесс"
        lines.append(f"{app_name}: {window.title}")

    return "Открытые окна: " + "; ".join(lines)


def switch_to_app(app_name: str) -> str:
    target_processes = get_target_process_names(app_name)

    if not target_processes:
        return f"Я пока не знаю приложение «{app_name}». Добавь его в APP_ALIASES."

    windows = get_open_windows()

    candidates = [
        window for window in windows
        if window.process_name in target_processes
    ]

    if not candidates:
        readable = ", ".join(target_processes)
        return f"Я не нашёл открытое окно приложения {readable}."

    # Берём первое видимое окно этого приложения
    window = candidates[0]

    ok = activate_window(window.hwnd)

    if ok:
        return f"Переключаюсь на {window.process_name.replace('.exe', '')}."

    return f"Нашёл {window.process_name}, но не смог вывести окно на передний план."


def switch_to_window(name: str) -> str:
    """
    Умное переключение:
    1. Сначала ищем по процессу: chrome.exe, telegram.exe, code.exe.
    2. Если не нашли алиас приложения — ищем по заголовку окна.
    """
    normalized = normalize_text(name)

    target_processes = get_target_process_names(normalized)

    if target_processes:
        return switch_to_app(normalized)

    windows = get_open_windows()

    for window in windows:
        if normalized in normalize_text(window.title):
            ok = activate_window(window.hwnd)

            if ok:
                return f"Переключаюсь на окно {window.title}."

            return f"Нашёл окно {window.title}, но не смог его активировать."

    return f"Я не нашёл окно или приложение с названием {normalized}."


def minimize_active_window() -> str:
    hwnd = win32gui.GetForegroundWindow()

    if not hwnd:
        return "Я не вижу активного окна."

    try:
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
        return "Сворачиваю активное окно."
    except Exception as e:
        print("Ошибка сворачивания окна:", e)
        return "Не получилось свернуть активное окно."


def maximize_active_window() -> str:
    hwnd = win32gui.GetForegroundWindow()

    if not hwnd:
        return "Я не вижу активного окна."

    try:
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
        return "Разворачиваю активное окно."
    except Exception as e:
        print("Ошибка разворачивания окна:", e)
        return "Не получилось развернуть активное окно."


def restore_active_window() -> str:
    hwnd = win32gui.GetForegroundWindow()

    if not hwnd:
        return "Я не вижу активного окна."

    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        return "Восстанавливаю активное окно."
    except Exception as e:
        print("Ошибка восстановления окна:", e)
        return "Не получилось восстановить активное окно."


def close_active_window() -> str:
    try:
        pyautogui.hotkey("alt", "f4")
        return "Закрываю активное окно."
    except Exception as e:
        print("Ошибка закрытия окна:", e)
        return "Не получилось закрыть активное окно."


def switch_to_next_window() -> str:
    try:
        pyautogui.hotkey("alt", "tab")
        return "Переключаюсь на следующее окно."
    except Exception as e:
        print("Ошибка переключения окна:", e)
        return "Не получилось переключиться на другое окно."