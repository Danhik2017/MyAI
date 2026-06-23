import re
import time

import pyautogui


pyautogui.PAUSE = 0.05
pyautogui.FAILSAFE = True


def press_media_key(key: str, presses: int = 1, delay: float = 0.05) -> str:
    try:
        for _ in range(presses):
            pyautogui.press(key)
            time.sleep(delay)

        return "Готово."

    except Exception as e:
        print("Ошибка медиа-клавиши:", e)
        return "Не получилось выполнить медиа-команду."


def volume_up(steps: int = 3) -> str:
    press_media_key("volumeup", presses=steps)
    return "Делаю громче."


def volume_down(steps: int = 3) -> str:
    press_media_key("volumedown", presses=steps)
    return "Делаю тише."


def volume_mute() -> str:
    press_media_key("volumemute")
    return "Переключаю звук."


def media_play_pause() -> str:
    press_media_key("playpause")
    return "Пауза или продолжение."


def media_next_track() -> str:
    press_media_key("nexttrack")
    return "Переключаю на следующий трек."


def media_previous_track() -> str:
    press_media_key("prevtrack")
    return "Переключаю на предыдущий трек."


def normalize_media_text(text: str) -> str:
    text = str(text).lower().strip()

    wake_words = [
        "джарвис",
        "jarvis",
        "джервис",
        "жарвис",
    ]

    for word in wake_words:
        text = re.sub(rf"\b{re.escape(word)}\b", " ", text)

    text = re.sub(r"[^\w\sа-яА-ЯёЁ-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def extract_steps(text: str, default: int = 3) -> int:
    """
    Позволяет говорить:
    - сделай громче на 5
    - сделай тише на 2 деления
    """
    match = re.search(r"\bна\s+(\d+)", text)

    if not match:
        return default

    try:
        steps = int(match.group(1))
    except ValueError:
        return default

    return max(1, min(steps, 20))


def handle_media_command(text: str) -> str | None:
    lower = normalize_media_text(text)

    print("MEDIA COMMAND:", repr(lower))

    if any(phrase in lower for phrase in [
        "сделай громче",
        "громче",
        "увеличь громкость",
        "прибавь громкость",
        "звук громче",
    ]):
        return volume_up(extract_steps(lower))

    if any(phrase in lower for phrase in [
        "сделай тише",
        "тише",
        "уменьши громкость",
        "убавь громкость",
        "звук тише",
    ]):
        return volume_down(extract_steps(lower))

    if any(phrase in lower for phrase in [
        "выключи звук",
        "включи звук",
        "отключи звук",
        "mute",
        "мьют",
        "без звука",
    ]):
        return volume_mute()

    if any(phrase in lower for phrase in [
        "пауза",
        "поставь на паузу",
        "продолжи",
        "продолжить",
        "play pause",
        "плей пауза",
        "останови музыку",
        "включи музыку",
    ]):
        return media_play_pause()

    if any(phrase in lower for phrase in [
        "следующий трек",
        "следующая песня",
        "переключи трек",
        "переключи песню",
        "дальше",
    ]):
        return media_next_track()

    if any(phrase in lower for phrase in [
        "предыдущий трек",
        "предыдущая песня",
        "верни трек",
        "назад трек",
    ]):
        return media_previous_track()

    return None