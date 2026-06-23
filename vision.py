from pathlib import Path
from datetime import datetime

import mss
import mss.tools
from PIL import Image
from ollama import Client, ResponseError

from text_normalizer import normalize_vision_answer

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


def analyze_screen(question: str | None = None) -> str:
    raw_screenshot = None
    image_path = None

    try:
        raw_screenshot = take_screenshot()
        image_path = compress_image_for_vision(raw_screenshot)

        prompt = question or (
            "Опиши, что сейчас видно на экране компьютера. "
            "Если виден текст, кратко перескажи его. "
            "Ответь на русском языке."
        )

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
                "temperature": 0.1,
                "num_ctx": 2048,
            },
        )

        return response["message"]["content"].strip()

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

    finally:
        safe_delete_file(image_path)
        safe_delete_file(raw_screenshot)

def safe_delete_file(path: Path | None):
    if not path:
        return

    try:
        if path.exists():
            path.unlink()
    except Exception as e:
        print(f"Не удалось удалить временный файл {path}: {e}")