import re
from typing import Callable

from confirmation import (
    is_dangerous_command,
    is_confirm_phrase,
    is_cancel_phrase,
    set_pending_command,
    get_pending_command,
    clear_pending_command,
)

from help_commands import handle_help_command

from screen_error_actions import (
    explain_screen_error,
    explain_screen_code_problem,
)

from vision import analyze_screen

from window_action import (
    minimize_active_window,
    maximize_active_window,
    restore_active_window,
    close_active_window,
    switch_to_next_window,
    switch_to_window,
    list_open_windows,
)

from keyboard_actions import handle_keyboard_command
from media_actions import handle_media_command
from text_input_actions import handle_text_input_command

from clipboard_actions import (
    read_clipboard,
    summarize_clipboard,
    explain_clipboard,
    fix_clipboard_code,
    clear_clipboard,
)

from web_actions import handle_web_command
from actions import open_app, is_known_app

from mouse_actions import handle_mouse_command

from dictation_mode import handle_dictation_mode, SILENT_RESPONSE

CommandHandler = Callable[[str, str], str | None]

COMMAND_STARTERS = [
    "нажми",
    "нажать",
    "энтер",
    "enter",
    "escape",
    "эскейп",
    "скопируй",
    "копировать",
    "вставь",
    "сохрани",
    "отмени",
    "выдели",
    "закрой",
    "открой",
    "запусти",
    "включи",
    "напиши",
    "введи",
    "набери",
    "напечатай",
    "сверни",
    "разверни",
    "переключись",
    "перейди",
    "активируй",
    "прочитай",
    "объясни",
    "исправь",
    "найди",
    "загугли",
    "поищи",
    "сделай",
]


def normalize_command_text(text: str) -> str:
    text = str(text).lower().strip()

    wake_words = [
        "джарвис",
        "jarvis",
        "джервис",
        "жарвис",
    ]

    for word in wake_words:
        text = re.sub(rf"\b{re.escape(word)}\b", " ", text)

    text = re.sub(r"\s+", " ", text).strip()
    return text


def split_compound_commands(text: str) -> list[str]:
    starters_pattern = "|".join(re.escape(word) for word in COMMAND_STARTERS)

    pattern = re.compile(
        rf"\s+(?:и|потом|затем|после этого)\s+(?=(?:{starters_pattern})\b)",
        flags=re.IGNORECASE,
    )

    parts = pattern.split(text)

    return [part.strip() for part in parts if part.strip()]


# ------------------- ОТДЕЛЬНЫЕ ОБРАБОТЧИКИ -------------------


def handle_help(text: str, lower: str) -> str | None:
    return handle_help_command(text)

def handle_mouse(text: str, lower: str) -> str | None:
    return handle_mouse_command(text)

def handle_screen_error(text: str, lower: str) -> str | None:
    if any(phrase in lower for phrase in [
        "объясни ошибку",
        "что за ошибка",
        "что это за ошибка",
        "как исправить ошибку",
        "ошибка на экране",
        "проанализируй ошибку",
        "разбери ошибку",
        "объясни traceback",
        "проанализируй traceback",
        "что значит traceback",
        "почему ошибка",
    ]):
        return explain_screen_error()

    if any(phrase in lower for phrase in [
        "проверь код на экране",
        "что не так с кодом",
        "что не так с кодом на экране",
        "найди проблему в коде",
        "проанализируй код на экране",
    ]):
        return explain_screen_code_problem()

    return None


def handle_screen_vision(text: str, lower: str) -> str | None:
    screen_phrases = [
        "что на экране",
        "что сейчас на экране",
        "посмотри на экран",
        "что ты видишь",
        "опиши экран",
        "прочитай экран",
        "проанализируй экран",
    ]

    if not any(phrase in lower for phrase in screen_phrases):
        return None

    detailed = any(
        word in lower
        for word in [
            "подробно",
            "детально",
            "проанализируй",
            "объясни",
            "что происходит",
            "разбери",
        ]
    )

    return analyze_screen(
        question=text,
        detailed=detailed,
    )


def handle_windows(text: str, lower: str) -> str | None:
    if any(phrase in lower for phrase in [
        "какие окна открыты",
        "список окон",
        "покажи окна",
        "что открыто",
    ]):
        return list_open_windows()

    if any(phrase in lower for phrase in [
        "сверни окно",
        "сверни активное окно",
        "сверни это окно",
    ]):
        return minimize_active_window()

    if any(phrase in lower for phrase in [
        "разверни окно",
        "разверни активное окно",
        "разверни это окно",
        "на весь экран",
    ]):
        return maximize_active_window()

    if any(phrase in lower for phrase in [
        "восстанови окно",
        "уменьши окно",
        "верни окно",
    ]):
        return restore_active_window()

    if any(phrase in lower for phrase in [
        "переключись на следующее окно",
        "следующее окно",
        "другое окно",
        "переключи окно",
    ]):
        return switch_to_next_window()

    if any(phrase in lower for phrase in [
        "закрой активное окно",
        "закрой это окно",
        "закрой окно",
    ]):
        return close_active_window()

    switch_patterns = [
        r"переключись на (.+)",
        r"перейди на (.+)",
        r"активируй окно (.+)",
        r"открой окно (.+)",
    ]

    for pattern in switch_patterns:
        match = re.search(pattern, lower)

        if match:
            window_name = match.group(1).strip()
            return switch_to_window(window_name)

    return None


def handle_keyboard(text: str, lower: str) -> str | None:
    return handle_keyboard_command(text)


def handle_media(text: str, lower: str) -> str | None:
    return handle_media_command(text)


def handle_text_input(text: str, lower: str) -> str | None:
    return handle_text_input_command(text)


def handle_clipboard(text: str, lower: str) -> str | None:
    if any(phrase in lower for phrase in [
        "прочитай буфер обмена",
        "что в буфере обмена",
        "что я скопировал",
        "прочитай скопированное",
    ]):
        return read_clipboard()

    if any(phrase in lower for phrase in [
        "перескажи буфер обмена",
        "кратко перескажи скопированное",
        "суммируй скопированное",
        "сделай краткое содержание скопированного",
    ]):
        return summarize_clipboard()

    if any(phrase in lower for phrase in [
        "объясни буфер обмена",
        "объясни скопированное",
        "объясни скопированный текст",
        "объясни скопированный код",
        "что значит скопированный код",
    ]):
        return explain_clipboard()

    if any(phrase in lower for phrase in [
        "исправь скопированный код",
        "проверь скопированный код",
        "найди ошибку в скопированном коде",
        "что не так со скопированным кодом",
    ]):
        return fix_clipboard_code()

    if any(phrase in lower for phrase in [
        "очисти буфер обмена",
        "очистить буфер обмена",
    ]):
        return clear_clipboard()

    return None


def handle_known_app_before_web(text: str, lower: str) -> str | None:
    """
    Важно: этот обработчик стоит ДО web.
    Иначе 'открой блокнот' может ошибочно попасть в открытие сайта.
    """
    open_prefixes = [
        "открой ",
        "запусти ",
        "включи ",
    ]

    for prefix in open_prefixes:
        if lower.startswith(prefix):
            app_candidate = lower.replace(prefix, "", 1).strip()

            if is_known_app(app_candidate):
                return open_app(app_candidate)

    return None


def handle_web(text: str, lower: str) -> str | None:
    return handle_web_command(text)


def handle_app(text: str, lower: str) -> str | None:
    open_prefixes = [
        "открой ",
        "запусти ",
        "включи ",
    ]

    for prefix in open_prefixes:
        if lower.startswith(prefix):
            app_name = lower.replace(prefix, "", 1).strip()
            return open_app(app_name)

    app_candidate = lower.strip()

    if is_known_app(app_candidate):
        return open_app(app_candidate)

    return None


COMMAND_HANDLERS: list[tuple[str, CommandHandler]] = [
    ("help", handle_help),
    ("screen_error", handle_screen_error),
    ("screen_vision", handle_screen_vision),
    ("windows", handle_windows),
    ("keyboard", handle_keyboard),
    ("media", handle_media),
    ("mouse", handle_mouse),
    ("text_input", handle_text_input),
    ("clipboard", handle_clipboard),
    ("known_app_before_web", handle_known_app_before_web),
    ("web", handle_web),
    ("app", handle_app),
]


def route_single_command(text: str, confirmed: bool = False) -> str | None:
    lower = normalize_command_text(text)

    print("LOCAL COMMAND RAW:", repr(text))
    print("LOCAL COMMAND LOWER:", repr(lower))

    if is_dangerous_command(lower) and not confirmed:
        return set_pending_command(lower)

    for handler_name, handler in COMMAND_HANDLERS:
        try:
            result = handler(text, lower)

            if result:
                print("COMMAND HANDLER:", handler_name)
                return result

        except Exception as e:
            print(f"Ошибка обработчика {handler_name}:", e)
            return f"Произошла ошибка в обработчике команды {handler_name}."

    return None


def handle_local_command(text: str) -> str | None:
    dictation_result = handle_dictation_mode(text)

    if dictation_result is not None:
        return dictation_result

    pending = get_pending_command()

    if pending:
        if is_confirm_phrase(text):
            command_text = pending["text"]
            clear_pending_command()

            print("CONFIRMED COMMAND:", repr(command_text))

            return route_single_command(
                command_text,
                confirmed=True,
            )

        if is_cancel_phrase(text):
            clear_pending_command()
            return "Отменил команду."

    commands = split_compound_commands(text)

    if len(commands) <= 1:
        return route_single_command(text)

    print("COMPOUND COMMANDS:", commands)

    results = []

    for command in commands:
        result = route_single_command(command)

        if result is None:
            results.append(f"не понял команду «{command}»")
        else:
            results.append(result)

        if get_pending_command():
            return result

    return "Выполнил команды по порядку."