from pathlib import Path
from datetime import datetime

import mss
import mss.tools
from PIL import Image
from ollama import Client, ResponseError


SCREENSHOT_DIR = Path("screenshots")
VISION_MODEL = "llava:7b"

client = Client(
    host="http://127.0.0.1:11434",
    trust_env=False,
    timeout=120,
)


def take_screenshot(monitor_index: int = 1) -> Path:
    SCREENSHOT_DIR.mkdir(exist_ok=True)

    raw_path = SCREENSHOT_DIR / datetime.now().strftime(
        "screen_raw_%Y-%m-%d_%H-%M-%S.png"
    )

    with mss.mss() as sct:
        monitor = sct.monitors[monitor_index]
        image = sct.grab(monitor)
        mss.tools.to_png(image.rgb, image.size, output=str(raw_path))

    return raw_path


def compress_image_for_vision(image_path: Path, max_width: int = 1280) -> Path:
    compressed_path = image_path.with_name(
        image_path.stem.replace("raw", "vision") + ".jpg"
    )

    with Image.open(image_path) as img:
        img = img.convert("RGB")

        width, height = img.size

        if width > max_width:
            new_height = int(height * max_width / width)
            img = img.resize((max_width, new_height))

        img.save(compressed_path, "JPEG", quality=90, optimize=True)

    return compressed_path


def build_screen_prompt(user_question: str | None = None, detailed: bool = False) -> str:
    if detailed:
        return f"""
Ты — голосовой помощник Джарвис. Пользователь попросил подробно посмотреть на экран.

Задача:
- Опиши, что сейчас видно на экране.
- Скажи, какие приложения или окна открыты.
- Если виден текст, перескажи самое важное.
- Если видна ошибка, объясни, в чём может быть проблема.
- Если экран связан с кодом, проектом или настройками, дай полезный вывод.
- Отвечай естественно, как голосовой ассистент.
- Не используй markdown, списки и нумерацию.
- Не говори "на изображении видно", говори "на экране видно".
- Ответ должен быть на русском языке, примерно пять-семь предложений.

Вопрос пользователя:
{user_question or "Что происходит на экране?"}
""".strip()

    return f"""
Ты — голосовой помощник Джарвис. Пользователь попросил посмотреть на экран.

Задача:
- Опиши экран живо и понятно.
- Не отвечай одним словом.
- Скажи, какое окно или приложение видно.
- Если есть важный текст, кратко перескажи его.
- Если видна ошибка, скажи, что именно не так.
- Отвечай как ассистент голосом: естественно, без markdown, без списков.
- Ответ должен быть на русском языке, примерно два-четыре предложения.

Вопрос пользователя:
{user_question or "Что сейчас видно на экране?"}
""".strip()


def analyze_screen(question: str | None = None, detailed: bool = False) -> str:
    raw_screenshot = take_screenshot()
    image_path = compress_image_for_vision(raw_screenshot)

    prompt = build_screen_prompt(question, detailed=detailed)

    try:
        response = client.chat(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [str(image_path.resolve())],
                }
            ],
            options={
                "temperature": 0.3,
                "num_ctx": 4096,
                "num_predict": 220 if detailed else 120,
                "repeat_penalty": 1.05,
            },
        )

        answer = response["message"]["content"].strip()

        if not answer:
            return "Я посмотрел на экран, но не смог уверенно разобрать содержимое."

        return answer

    except ResponseError as e:
        print("Ошибка Ollama vision ResponseError:", e)
        return (
            "Модель анализа экрана вернула ошибку. "
            "Проверь, что установлена модель с поддержкой изображений."
        )

    except ConnectionResetError as e:
        print("Модель анализа экрана разорвала соединение:", e)
        return (
            "Модель анализа экрана разорвала соединение. "
            "Скорее всего, не хватает памяти или скриншот слишком большой."
        )

    except Exception as e:
        print("Ошибка анализа экрана:", e)
        return "Произошла ошибка при анализе экрана."