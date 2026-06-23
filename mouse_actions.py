import re
import time

import os
from pathlib import Path

from PIL import ImageDraw

import pyautogui


pyautogui.PAUSE = 0.05
pyautogui.FAILSAFE = True


DEFAULT_MOVE_PIXELS = 150
DEFAULT_SCROLL_AMOUNT = 5


def normalize_mouse_text(text: str) -> str:
    text = str(text).lower().strip()

    wake_words = [
        "джарвис",
        "jarvis",
        "джервис",
        "жарвис",
    ]

    for word in wake_words:
        text = re.sub(rf"\b{re.escape(word)}\b", " ", text)

    text = text.replace(".", " ")
    text = text.replace(",", " ")
    text = re.sub(r"\s+", " ", text).strip()

    return text


def extract_number(text: str, default: int) -> int:
    match = re.search(r"\bна\s+(\d+)", text)

    if not match:
        match = re.search(r"\b(\d+)\b", text)

    if not match:
        return default

    try:
        value = int(match.group(1))
    except ValueError:
        return default

    return max(1, min(value, 2000))


def mouse_click() -> str:
    try:
        pyautogui.click()
        return "Кликнул."
    except Exception as e:
        print("Ошибка клика мышью:", e)
        return "Не получилось кликнуть."


def mouse_double_click() -> str:
    try:
        pyautogui.doubleClick()
        return "Двойной клик."
    except Exception as e:
        print("Ошибка двойного клика:", e)
        return "Не получилось сделать двойной клик."


def mouse_right_click() -> str:
    try:
        pyautogui.rightClick()
        return "Правый клик."
    except Exception as e:
        print("Ошибка правого клика:", e)
        return "Не получилось сделать правый клик."


def mouse_click_center() -> str:
    try:
        width, height = pyautogui.size()
        pyautogui.click(width // 2, height // 2)
        return "Кликнул по центру экрана."
    except Exception as e:
        print("Ошибка клика по центру:", e)
        return "Не получилось кликнуть по центру."


def mouse_scroll_up(amount: int = DEFAULT_SCROLL_AMOUNT) -> str:
    try:
        pyautogui.scroll(amount)
        return "Прокручиваю вверх."
    except Exception as e:
        print("Ошибка прокрутки вверх:", e)
        return "Не получилось прокрутить вверх."


def mouse_scroll_down(amount: int = DEFAULT_SCROLL_AMOUNT) -> str:
    try:
        pyautogui.scroll(-amount)
        return "Прокручиваю вниз."
    except Exception as e:
        print("Ошибка прокрутки вниз:", e)
        return "Не получилось прокрутить вниз."


def mouse_move(dx: int = 0, dy: int = 0) -> str:
    try:
        pyautogui.moveRel(dx, dy, duration=0.15)
        return "Переместил мышь."
    except Exception as e:
        print("Ошибка перемещения мыши:", e)
        return "Не получилось переместить мышь."


def get_mouse_position() -> str:
    try:
        x, y = pyautogui.position()
        return f"Мышь сейчас в позиции икс {x}, игрек {y}."
    except Exception as e:
        print("Ошибка получения позиции мыши:", e)
        return "Не получилось определить позицию мыши."


def handle_mouse_command(text: str) -> str | None:
    lower = normalize_mouse_text(text)

    print("MOUSE COMMAND:", repr(lower))

    if any(phrase in lower for phrase in [
        "покажи сетку",
        "покажи сетку экрана",
        "сетка экрана",
        "покажи координаты экрана",
    ]):
        return show_screen_grid()

    if any(phrase in lower for phrase in [
        "перемести мышь на",
        "перемести курсор на",
        "курсор на",
    ]):
        coords = extract_coordinates(lower)

        if coords:
            x, y = coords
            return mouse_move_to(x, y)

    if any(phrase in lower for phrase in [
        "клик по икс",
        "клик x",
        "клик по x",
        "клик по координатам",
        "нажми по координатам",
    ]):
        coords = extract_coordinates(lower)

        if coords:
            x, y = coords
            return mouse_click_at(x, y)

        return "Я не понял координаты для клика."

    position_clicks = {
        "клик в центр": "центр",
        "клик по центру": "центр",
        "нажми в центр": "центр",

        "клик в левый верхний угол": "левый верхний угол",
        "клик в правый верхний угол": "правый верхний угол",
        "клик в левый нижний угол": "левый нижний угол",
        "клик в правый нижний угол": "правый нижний угол",

        "клик сверху": "верх",
        "клик снизу": "низ",
        "клик слева": "лево",
        "клик справа": "право",
    }

    for phrase, position_name in position_clicks.items():
        if phrase in lower:
            return click_screen_position(position_name)

    if any(phrase in lower for phrase in [
        "где мышь",
        "позиция мыши",
        "координаты мыши",
        "где курсор",
        "позиция курсора",
    ]):
        return get_mouse_position()

    if any(phrase in lower for phrase in [
        "клик по центру",
        "нажми по центру",
        "нажми в центр",
        "кликни по центру",
    ]):
        return mouse_click_center()

    if any(phrase in lower for phrase in [
        "двойной клик",
        "два клика",
        "кликни два раза",
        "нажми два раза",
    ]):
        return mouse_double_click()

    if any(phrase in lower for phrase in [
        "правый клик",
        "клик правой кнопкой",
        "нажми правой кнопкой",
        "контекстное меню",
    ]):
        return mouse_right_click()

    if lower in [
        "клик",
        "кликни",
        "нажми мышкой",
        "нажми левой кнопкой",
        "левый клик",
    ]:
        return mouse_click()

    if any(phrase in lower for phrase in [
        "прокрути вниз",
        "листай вниз",
        "скролл вниз",
        "скрол вниз",
    ]):
        amount = extract_number(lower, DEFAULT_SCROLL_AMOUNT)
        return mouse_scroll_down(amount)

    if any(phrase in lower for phrase in [
        "прокрути вверх",
        "листай вверх",
        "скролл вверх",
        "скрол вверх",
    ]):
        amount = extract_number(lower, DEFAULT_SCROLL_AMOUNT)
        return mouse_scroll_up(amount)

    pixels = extract_number(lower, DEFAULT_MOVE_PIXELS)

    if any(phrase in lower for phrase in [
        "перемести мышь вправо",
        "курсор вправо",
        "мышь вправо",
    ]):
        return mouse_move(dx=pixels)

    if any(phrase in lower for phrase in [
        "перемести мышь влево",
        "курсор влево",
        "мышь влево",
    ]):
        return mouse_move(dx=-pixels)

    if any(phrase in lower for phrase in [
        "перемести мышь вверх",
        "курсор вверх",
        "мышь вверх",
    ]):
        return mouse_move(dy=-pixels)

    if any(phrase in lower for phrase in [
        "перемести мышь вниз",
        "курсор вниз",
        "мышь вниз",
    ]):
        return mouse_move(dy=pixels)

    return None

SCREENSHOTS_DIR = Path("screenshots")
GRID_IMAGE_PATH = SCREENSHOTS_DIR / "screen_grid.png"


def extract_coordinates(text: str) -> tuple[int, int] | None:
    """
    Поддерживает фразы:
    - клик по икс 500 игрек 300
    - клик x 500 y 300
    - перемести мышь на 500 300
    """
    lower = normalize_mouse_text(text)

    lower = lower.replace("икс", "x")
    lower = lower.replace("игрек", "y")
    lower = lower.replace("и грек", "y")

    patterns = [
        r"x\s*(\d+)\s*y\s*(\d+)",
        r"по\s+(\d+)\s+(\d+)",
        r"на\s+(\d+)\s+(\d+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, lower)

        if match:
            x = int(match.group(1))
            y = int(match.group(2))

            width, height = pyautogui.size()

            x = max(0, min(x, width - 1))
            y = max(0, min(y, height - 1))

            return x, y

    return None


def mouse_move_to(x: int, y: int) -> str:
    try:
        pyautogui.moveTo(x, y, duration=0.15)
        return f"Переместил мышь на икс {x}, игрек {y}."
    except Exception as e:
        print("Ошибка перемещения мыши по координатам:", e)
        return "Не получилось переместить мышь по координатам."


def mouse_click_at(x: int, y: int) -> str:
    try:
        pyautogui.click(x, y)
        return f"Кликнул по икс {x}, игрек {y}."
    except Exception as e:
        print("Ошибка клика по координатам:", e)
        return "Не получилось кликнуть по координатам."


def get_screen_point(position_name: str) -> tuple[int, int]:
    width, height = pyautogui.size()

    points = {
        "центр": (width // 2, height // 2),
        "середина": (width // 2, height // 2),

        "левый верхний угол": (50, 50),
        "правый верхний угол": (width - 50, 50),
        "левый нижний угол": (50, height - 50),
        "правый нижний угол": (width - 50, height - 50),

        "верх": (width // 2, 50),
        "низ": (width // 2, height - 50),
        "лево": (50, height // 2),
        "право": (width - 50, height // 2),
    }

    return points[position_name]


def click_screen_position(position_name: str) -> str:
    try:
        x, y = get_screen_point(position_name)
        pyautogui.click(x, y)
        return f"Кликнул: {position_name}."
    except Exception as e:
        print("Ошибка клика по позиции экрана:", e)
        return "Не получилось кликнуть по этой позиции."


def show_screen_grid() -> str:
    """
    Делает скриншот, рисует сетку координат и открывает картинку.
    Потом можно сказать: клик по икс 500 игрек 300.
    """
    try:
        SCREENSHOTS_DIR.mkdir(exist_ok=True)

        screenshot = pyautogui.screenshot()
        draw = ImageDraw.Draw(screenshot)

        width, height = screenshot.size

        step_x = 200
        step_y = 150

        # Вертикальные линии
        for x in range(0, width, step_x):
            draw.line((x, 0, x, height), width=2)
            draw.text((x + 5, 5), f"x{x}", fill=(255, 0, 0))

        # Горизонтальные линии
        for y in range(0, height, step_y):
            draw.line((0, y, width, y), width=2)
            draw.text((5, y + 5), f"y{y}", fill=(255, 0, 0))

        # Центральная точка
        center_x = width // 2
        center_y = height // 2

        draw.ellipse(
            (center_x - 8, center_y - 8, center_x + 8, center_y + 8),
            outline=(255, 0, 0),
            width=3,
        )
        draw.text(
            (center_x + 10, center_y + 10),
            f"center {center_x}, {center_y}",
            fill=(255, 0, 0),
        )

        screenshot.save(GRID_IMAGE_PATH)

        os.startfile(str(GRID_IMAGE_PATH))

        return "Показал сетку экрана. Назови координаты для клика."

    except Exception as e:
        print("Ошибка показа сетки экрана:", e)
        return "Не получилось показать сетку экрана."