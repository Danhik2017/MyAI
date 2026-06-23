import re
import time

import pyautogui
import pyperclip


TEXT_COMMAND_PREFIXES = [
    "напиши",
    "введи",
    "набери",
    "напечатай",
    "напиши в поле",
    "введи в поле",
    "набери в поле",
]

CODE_REPLACEMENTS = {
    "открытая скобка": "(",
    "закрытая скобка": ")",
    "двоеточие": ":",
    "точка с запятой": ";",
    "кавычка": '"',
    "одинарная кавычка": "'",
    "равно": "=",
    "нижнее подчеркивание": "_",
    "слэш": "/",
    "обратный слэш": "\\",
}

def normalize_input_command(text: str) -> str:
    text = text.strip()

    # Убираем wake word, если он попал в распознанный текст
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

    # Сначала более длинные команды, чтобы "напиши в поле" не сломалось на "напиши"
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

def paste_text(text: str, restore_clipboard: bool = True) -> str:
    text = str(text)

    if not text.strip():
        return "Я не понял, какой текст нужно ввести."

    old_clipboard = ""

    try:
        if restore_clipboard:
            try:
                old_clipboard = pyperclip.paste()
            except Exception:
                old_clipboard = ""

        pyperclip.copy(text)
        time.sleep(0.05)

        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.05)

        if restore_clipboard:
            try:
                pyperclip.copy(old_clipboard)
            except Exception:
                pass

        return "Ввёл текст."

    except Exception as e:
        print("Ошибка ввода текста:", e)
        return "Не получилось ввести текст."


def handle_text_input_command(text: str) -> str | None:
    text_to_type = extract_text_to_type(text)

    if text_to_type is None:
        return None

    text_to_type = apply_code_replacements(text_to_type)

    if not text_to_type.strip():
        return "Я не понял, какой текст нужно ввести."

    print("TEXT INPUT:", repr(text_to_type))

    return paste_text(text_to_type)