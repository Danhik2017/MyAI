import re

from vision import analyze_screen
from actions import open_app

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

from text_input_actions import handle_text_input_command

from actions import open_app, is_known_app

def handle_local_command(text: str) -> str | None:
    lower = text.lower().strip()

    print("LOCAL COMMAND RAW:", repr(text))
    print("LOCAL COMMAND LOWER:", repr(lower))

    screen_phrases = [
        "что на экране",
        "что сейчас на экране",
        "посмотри на экран",
        "что ты видишь",
        "опиши экран",
        "прочитай экран",
        "проанализируй экран",
        "посмотри что происходит",
    ]

    if any(phrase in lower for phrase in screen_phrases):
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

    keyboard_answer = handle_keyboard_command(lower)

    if keyboard_answer:
        return keyboard_answer

    text_input_answer = handle_text_input_command(text)

    if text_input_answer:
        return text_input_answer

    open_phrases = [
        "открой ",
        "запусти ",
        "включи ",
    ]

    for phrase in open_phrases:
        if lower.startswith(phrase):
            app_name = lower.replace(phrase, "", 1).strip()
            return open_app(app_name)

    app_candidate = lower.strip()

    if is_known_app(app_candidate):
        return open_app(app_candidate)

    return None
