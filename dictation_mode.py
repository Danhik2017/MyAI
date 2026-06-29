import re

import pyautogui

from text_input_actions import paste_text

import time

SILENT_RESPONSE = "__SILENT__"

_dictation_enabled = False


START_DICTATION_PHRASES = [
    "начни диктовку",
    "включи диктовку",
    "режим диктовки",
    "старт диктовка",
    "начать диктовку",
]

STOP_DICTATION_PHRASES = [
    "стоп диктовка",
    "останови диктовку",
    "выключи диктовку",
    "закончи диктовку",
    "конец диктовки",
]

WAKE_WORDS = [
    "джарвис",
    "jarvis",
    "джервис",
    "жарвис",
]


def press_enter(times: int = 1) -> str:
    try:
        for _ in range(times):
            pyautogui.press("enter")
            time.sleep(0.05)

        return SILENT_RESPONSE

    except Exception as e:
        print("Ошибка Enter в диктовке:", e)
        return "Не получилось сделать новую строку."

def is_dictation_enabled() -> bool:
    return _dictation_enabled


def remove_wake_words(text: str) -> str:
    text = str(text).strip()

    for word in WAKE_WORDS:
        text = re.sub(
            rf"\b{re.escape(word)}\b",
            " ",
            text,
            flags=re.IGNORECASE,
        )

    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_command_text(text: str) -> str:
    text = remove_wake_words(text)
    text = text.lower().strip()
    text = text.replace(".", " ")
    text = text.replace(",", " ")
    text = text.replace("!", " ")
    text = text.replace("?", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def enable_dictation() -> str:
    global _dictation_enabled
    _dictation_enabled = True
    return "Режим диктовки включён. Говори текст, а для выхода скажи стоп диктовка."


def disable_dictation() -> str:
    global _dictation_enabled
    _dictation_enabled = False
    return "Режим диктовки выключен."


def is_start_dictation_command(text: str) -> bool:
    lower = normalize_command_text(text)
    return any(phrase in lower for phrase in START_DICTATION_PHRASES)


def is_stop_dictation_command(text: str) -> bool:
    lower = normalize_command_text(text)
    return any(phrase in lower for phrase in STOP_DICTATION_PHRASES)


def fix_spaces_around_punctuation(text: str) -> str:
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)
    text = re.sub(r"([,.!?;:])([^\s])", r"\1 \2", text)
    text = re.sub(r"\s+([)\]»])", r"\1", text)
    text = re.sub(r"([(\[«])\s+", r"\1", text)

    # Важно: не превращаем пробелы в переносы строк
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()

def spoken_text_to_written(text: str) -> str:
    """
    Превращает голосовую диктовку в обычный текст.

    Пример:
    "привет запятая как дела вопросительный знак"
    ->
    "привет, как дела?"
    """
    text = remove_wake_words(text)
    text = text.lower().strip()

    replacements = [

        ("точка с запятой", ";"),
        ("двоеточие", ":"),
        ("запятая", ","),
        ("точка", "."),
        ("вопросительный знак", "?"),
        ("восклицательный знак", "!"),

        ("открой скобку", "("),
        ("открытая скобка", "("),
        ("закрой скобку", ")"),
        ("закрытая скобка", ")"),

        ("открой квадратную скобку", "["),
        ("закрой квадратную скобку", "]"),

        ("кавычки", '"'),
        ("кавычка", '"'),

        ("длинное тире", " — "),
        ("тире", " — "),
        ("дефис", "-"),
        ("слэш", "/"),
        ("обратный слэш", "\\"),
    ]

    for spoken, written in replacements:
        text = text.replace(spoken, written)

    text = fix_spaces_around_punctuation(text)

    return text


def should_add_space_after(text: str) -> bool:
    if not text:
        return False

    if text.endswith("\n"):
        return False

    if text.endswith(" "):
        return False

    return True


def dictation_backspace_word() -> str:
    try:
        pyautogui.hotkey("ctrl", "backspace")
        return SILENT_RESPONSE
    except Exception as e:
        print("Ошибка удаления слова в диктовке:", e)
        return "Не получилось удалить последнее слово."


def dictation_backspace_char() -> str:
    try:
        pyautogui.press("backspace")
        return SILENT_RESPONSE
    except Exception as e:
        print("Ошибка удаления символа в диктовке:", e)
        return "Не получилось удалить символ."


def handle_dictation_mode(text: str) -> str | None:
    """
    Возвращает:
    - None, если это не команда диктовки
    - обычный текст ответа, если нужно сказать вслух
    - SILENT_RESPONSE, если текст вставлен и озвучивать ничего не нужно
    """
    global _dictation_enabled

    lower = normalize_command_text(text)

    if not _dictation_enabled:
        if is_start_dictation_command(text):
            return enable_dictation()

        return None

    # В режиме диктовки сначала проверяем выход
    if is_stop_dictation_command(text):
        return disable_dictation()

    # Служебные команды внутри диктовки
    if lower in [
        "удали последнее слово",
        "стереть последнее слово",
        "сотри последнее слово",
    ]:
        return dictation_backspace_word()

    if lower in [
        "удали символ",
        "стереть символ",
        "сотри символ",
        "backspace",
        "бэкспейс",
    ]:
        return dictation_backspace_char()

    if lower in [
        "новая строка",
        "новую строку",
        "перенос строки",
    ]:
        return press_enter(1)

    if lower == "абзац":
        return press_enter(2)

    if lower in [
        "пробел",
        "поставь пробел",
    ]:
        paste_text(" ")
        return SILENT_RESPONSE

    # Обычная диктовка
    written_text = spoken_text_to_written(text)

    if not written_text.strip():
        return SILENT_RESPONSE

    if should_add_space_after(written_text):
        written_text += " "

    print("DICTATION TEXT:", repr(written_text))

    paste_text(written_text)

    return SILENT_RESPONSE