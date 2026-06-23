import time


CONFIRMATION_TIMEOUT_SECONDS = 30

_pending_command: dict | None = None


DANGEROUS_PHRASES = [
    # window / app
    "закрой окно",
    "закрой активное окно",
    "закрой это окно",
    "закрой приложение",
    "закрой программу",

    # browser / tabs
    "закрой вкладку",
    "закрыть вкладку",

    # clipboard
    "очисти буфер обмена",
    "очистить буфер обмена",

    # future file/system commands
    "удали",
    "удалить",
    "сотри",
    "очисти папку",
    "очистить папку",
    "выключи компьютер",
    "перезагрузи компьютер",
    "заверши работу",
    "запусти команду",
    "выполни команду",

    # messages / external actions
    "отправь сообщение",
    "отправь письмо",
    "отправить сообщение",
    "отправить письмо",

    # мышь
    "нажми отправить",
    "кликни отправить",
    "нажми удалить",
    "кликни удалить",
    "нажми оплатить",
    "кликни оплатить",
    "нажми купить",
    "кликни купить",
]


CONFIRM_PHRASES = [
    "подтверждаю",
    "да подтверждаю",
    "выполняй",
    "сделай",
    "да сделай",
    "можно",
    "да можно",
]


CANCEL_PHRASES = [
    "отмена",
    "отмени",
    "не надо",
    "не выполняй",
    "стоп",
    "cancel",
]


def normalize_confirmation_text(text: str) -> str:
    return str(text).lower().strip().replace(".", "").replace(",", "")


def is_dangerous_command(text: str) -> bool:
    lower = normalize_confirmation_text(text)
    return any(phrase in lower for phrase in DANGEROUS_PHRASES)


def is_confirm_phrase(text: str) -> bool:
    lower = normalize_confirmation_text(text)
    return lower in CONFIRM_PHRASES


def is_cancel_phrase(text: str) -> bool:
    lower = normalize_confirmation_text(text)
    return lower in CANCEL_PHRASES


def set_pending_command(command_text: str, description: str | None = None) -> str:
    global _pending_command

    _pending_command = {
        "text": command_text,
        "description": description or command_text,
        "created_at": time.time(),
    }

    return (
        f"Команда «{description or command_text}» может изменить данные или закрыть окно. "
        f"Скажи «подтверждаю», чтобы выполнить, или «отмена», чтобы отменить."
    )


def get_pending_command() -> dict | None:
    global _pending_command

    if _pending_command is None:
        return None

    age = time.time() - _pending_command["created_at"]

    if age > CONFIRMATION_TIMEOUT_SECONDS:
        _pending_command = None
        return None

    return _pending_command


def clear_pending_command():
    global _pending_command
    _pending_command = None