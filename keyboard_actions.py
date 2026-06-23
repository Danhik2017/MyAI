import re
import pyautogui


# Небольшая пауза между действиями, чтобы Windows/приложения успевали реагировать
pyautogui.PAUSE = 0.05

# Fail-safe: если мышку резко увести в левый верхний угол экрана,
# pyautogui остановит выполнение
pyautogui.FAILSAFE = True


HOTKEY_COMMANDS = {
    # clipboard
    "скопируй": ("ctrl", "c"),
    "копировать": ("ctrl", "c"),
    "скопировать": ("ctrl", "c"),

    "вставь": ("ctrl", "v"),
    "вставить": ("ctrl", "v"),

    "вырежи": ("ctrl", "x"),
    "вырезать": ("ctrl", "x"),

    # editing
    "сохрани": ("ctrl", "s"),
    "сохранить": ("ctrl", "s"),

    "отмени": ("ctrl", "z"),
    "отменить": ("ctrl", "z"),

    "верни": ("ctrl", "y"),
    "повтори": ("ctrl", "y"),
    "повторить": ("ctrl", "y"),

    "выдели всё": ("ctrl", "a"),
    "выделить всё": ("ctrl", "a"),
    "выдели все": ("ctrl", "a"),

    "найди": ("ctrl", "f"),
    "поиск": ("ctrl", "f"),

    # browser / tabs
    "новая вкладка": ("ctrl", "t"),
    "открой новую вкладку": ("ctrl", "t"),
    "создай новую вкладку": ("ctrl", "t"),

    "закрой вкладку": ("ctrl", "w"),
    "закрыть вкладку": ("ctrl", "w"),

    "восстанови вкладку": ("ctrl", "shift", "t"),
    "верни вкладку": ("ctrl", "shift", "t"),

    "обнови страницу": ("ctrl", "r"),
    "перезагрузи страницу": ("ctrl", "r"),

    "следующая вкладка": ("ctrl", "tab"),
    "переключись на следующую вкладку": ("ctrl", "tab"),

    "предыдущая вкладка": ("ctrl", "shift", "tab"),
    "переключись на предыдущую вкладку": ("ctrl", "shift", "tab"),

    # system / dev
    "диспетчер задач": ("ctrl", "shift", "esc"),
    "открой диспетчер задач": ("ctrl", "shift", "esc"),

    "комментарий": ("ctrl", "/"),
    "закомментируй": ("ctrl", "/"),
    "раскомментируй": ("ctrl", "/"),
}


SINGLE_KEY_COMMANDS = {
    "нажми энтер": "enter",
    "нажми enter": "enter",
    "энтер": "enter",

    "нажми escape": "esc",
    "нажми эскейп": "esc",
    "escape": "esc",
    "эскейп": "esc",

    "нажми пробел": "space",
    "пробел": "space",

    "нажми таб": "tab",
    "нажми tab": "tab",
    "таб": "tab",

    "нажми назад": "backspace",
    "backspace": "backspace",
    "бэкспейс": "backspace",

    "нажми удалить": "delete",
    "delete": "delete",
    "делит": "delete",

    "стрелка вверх": "up",
    "нажми вверх": "up",

    "стрелка вниз": "down",
    "нажми вниз": "down",

    "стрелка влево": "left",
    "нажми влево": "left",

    "стрелка вправо": "right",
    "нажми вправо": "right",

    "home": "home",
    "end": "end",
    "page up": "pageup",
    "page down": "pagedown",
}


def normalize_keyboard_text(text: str) -> str:
    text = text.lower().strip()

    # убираем wake word, если оно попало в распознанный текст
    wake_words = [
        "джарвис",
        "jarvis",
        "джервис",
        "жарвис",
    ]

    for word in wake_words:
        text = text.replace(word, " ")

    text = re.sub(r"[^\w\sа-яА-ЯёЁ/+-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def execute_hotkey(keys: tuple[str, ...]) -> str:
    try:
        pyautogui.hotkey(*keys)
        return "Готово."
    except Exception as e:
        print("Ошибка hotkey:", e)
        return "Не получилось выполнить сочетание клавиш."


def execute_single_key(key: str) -> str:
    try:
        pyautogui.press(key)
        return "Нажал."
    except Exception as e:
        print("Ошибка press:", e)
        return "Не получилось нажать клавишу."


def handle_keyboard_command(text: str) -> str | None:
    lower = normalize_keyboard_text(text)

    print("KEYBOARD COMMAND:", repr(lower))

    # Сначала проверяем точные/частичные hotkey-команды
    for phrase, keys in HOTKEY_COMMANDS.items():
        if phrase in lower:
            return execute_hotkey(keys)

    # Потом одиночные клавиши
    for phrase, key in SINGLE_KEY_COMMANDS.items():
        if phrase in lower:
            return execute_single_key(key)

    return None