import re
import time

import pyautogui
import pyperclip
import win32api
import win32clipboard
import win32con
import win32gui


TEXT_COMMAND_PREFIXES = [
    "напиши в поле",
    "введи в поле",
    "набери в поле",
    "напечатай в поле",
    "напиши",
    "введи",
    "набери",
    "напечатай",
]


CODE_REPLACEMENTS = {
    "открытая скобка": "(",
    "закрытая скобка": ")",
    "левая скобка": "(",
    "правая скобка": ")",
    "двоеточие": ":",
    "точка с запятой": ";",
    "запятая": ",",
    "точка": ".",
    "кавычка": '"',
    "кавычки": '"',
    "одинарная кавычка": "'",
    "апостроф": "'",
    "равно": "=",
    "плюс": "+",
    "минус": "-",
    "нижнее подчеркивание": "_",
    "слэш": "/",
    "обратный слэш": "\\",
}

def clean_text_to_type(text: str) -> str:
    text = str(text).strip()

    # Убираем фразы, которые STT иногда добавляет как часть диктовки
    trash_phrases = [
        "в кавычках",
        "с кавычками",
        "без кавычек",
    ]

    lowered = text.lower()

    for phrase in trash_phrases:
        lowered = lowered.replace(phrase, "")

    text = lowered.strip()

    # Убираем внешние кавычки, если весь текст обёрнут в них
    quote_pairs = [
        ('"', '"'),
        ("'", "'"),
        ("«", "»"),
        ("“", "”"),
        ("„", "“"),
        ("`", "`"),
    ]

    changed = True

    while changed:
        changed = False
        text = text.strip()

        for left, right in quote_pairs:
            if text.startswith(left) and text.endswith(right) and len(text) >= 2:
                text = text[1:-1].strip()
                changed = True

    return text

def normalize_input_command(text: str) -> str:
    text = str(text).strip()

    wake_words = [
        "джарвис",
        "jarvis",
        "джервис",
        "жарвис",
    ]

    for word in wake_words:
        text = re.sub(
            rf"\b{re.escape(word)}\b",
            " ",
            text,
            flags=re.IGNORECASE,
        )

    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_text_to_type(command: str) -> str | None:
    normalized = normalize_input_command(command)
    lower = normalized.lower()

    sorted_prefixes = sorted(TEXT_COMMAND_PREFIXES, key=len, reverse=True)

    for prefix in sorted_prefixes:
        if lower.startswith(prefix + " "):
            return normalized[len(prefix):].strip()

    return None


def apply_code_replacements(text: str | None) -> str:
    if text is None:
        return ""

    result = str(text)

    for phrase, symbol in CODE_REPLACEMENTS.items():
        result = result.replace(phrase, symbol)

    return result


def get_active_window_title() -> str:
    try:
        hwnd = win32gui.GetForegroundWindow()
        return win32gui.GetWindowText(hwnd)
    except Exception:
        return ""


def set_clipboard_text(text: str) -> bool:
    """
    Надёжная установка Unicode-текста в буфер обмена Windows.
    pyperclip иногда работает нормально, но Win32-вариант стабильнее.
    """
    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
        win32clipboard.CloseClipboard()
        return True

    except Exception as e:
        print("Ошибка Win32 clipboard:", e)

        try:
            win32clipboard.CloseClipboard()
        except Exception:
            pass

        try:
            pyperclip.copy(text)
            return True
        except Exception as e2:
            print("Ошибка pyperclip:", e2)
            return False


def get_clipboard_text() -> str:
    try:
        return pyperclip.paste()
    except Exception:
        return ""


def send_ctrl_v_win32():
    """
    Отправка Ctrl+V через Win32.
    Иногда это срабатывает лучше, чем pyautogui.hotkey("ctrl", "v").
    """
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    time.sleep(0.03)

    win32api.keybd_event(ord("V"), 0, 0, 0)
    time.sleep(0.03)
    win32api.keybd_event(ord("V"), 0, win32con.KEYEVENTF_KEYUP, 0)

    time.sleep(0.03)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)


def paste_text(text: str) -> str:
    text = str(text)

    if not text.strip():
        return "Я не понял, какой текст нужно ввести."

    try:
        active_before = get_active_window_title()
        print("ACTIVE WINDOW BEFORE PASTE:", repr(active_before))

        ok = set_clipboard_text(text)

        if not ok:
            return "Не получилось записать текст в буфер обмена."

        time.sleep(0.3)

        clipboard_text = get_clipboard_text()
        print("CLIPBOARD BEFORE PASTE:", repr(clipboard_text))

        if clipboard_text.strip() != text.strip():
            print("WARNING: clipboard text differs from target text")

        # Первый способ: Win32 Ctrl+V
        send_ctrl_v_win32()
        time.sleep(0.3)

        # Второй способ fallback: pyautogui Ctrl+V
        # Если первый способ уже сработал, второй может вставить текст второй раз.
        # Поэтому сначала оставь fallback выключенным.
        # pyautogui.hotkey("ctrl", "v")

        active_after = get_active_window_title()
        print("ACTIVE WINDOW AFTER PASTE:", repr(active_after))

        return "Ввёл текст."

    except Exception as e:
        print("Ошибка ввода текста:", e)
        return "Не получилось ввести текст."


def handle_text_input_command(text: str) -> str | None:
    text_to_type = extract_text_to_type(text)

    if text_to_type is None:
        return None

    text_to_type = clean_text_to_type(text_to_type)
    text_to_type = apply_code_replacements(text_to_type)
    text_to_type = clean_text_to_type(text_to_type)

    if not text_to_type.strip():
        return "Я не понял, какой текст нужно ввести."

    print("TEXT INPUT:", repr(text_to_type))

    return paste_text(text_to_type)