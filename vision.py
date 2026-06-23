from pathlib import Path
from datetime import datetime
import mss
import mss.tools
from PIL import Image
from ollama import Client, ResponseError


SCREENSHOT_DIR = Path("screenshots")
VISION_MODEL = "llava:7b"

client = Client(host="http://127.0.0.1:11434")


def take_screenshot(monitor_index: int = 1) -> Path:
    SCREENSHOT_DIR.mkdir(exist_ok=True)

    raw_path = SCREENSHOT_DIR / datetime.now().strftime("screen_raw_%Y-%m-%d_%H-%M-%S.png")

    with mss.mss() as sct:
        monitor = sct.monitors[monitor_index]
        image = sct.grab(monitor)
        mss.tools.to_png(image.rgb, image.size, output=str(raw_path))

    return raw_path


def compress_image_for_vision(image_path: Path, max_width: int = 1280) -> Path:
    compressed_path = image_path.with_name(image_path.stem.replace("raw", "vision") + ".jpg")

    with Image.open(image_path) as img:
        img = img.convert("RGB")

        width, height = img.size

        if width > max_width:
            new_height = int(height * max_width / width)
            img = img.resize((max_width, new_height))

        img.save(compressed_path, "JPEG", quality=85, optimize=True)

    return compressed_path


def analyze_screen(question: str | None = None) -> str:
    raw_screenshot = take_screenshot()
    image_path = compress_image_for_vision(raw_screenshot)

    prompt = question or (
        "Опиши, что сейчас видно на экране компьютера. "
        "Если виден текст, кратко перескажи его. "
        "Ответь на русском языке."
    )

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
                "temperature": 0.1,
                "num_ctx": 2048,
            },
        )

        return response["message"]["content"].strip()

    except ResponseError as e:
        print("Ошибка Ollama vision ResponseError:", e)
        return (
            "Ollama вернул ошибку при анализе экрана. "
            "Проверь, что установлена именно vision-модель, например llava:7b."
        )

    except ConnectionResetError as e:
        print("Ollama разорвал соединение:", e)
        return (
            "Ollama разорвал соединение во время анализа экрана. "
            "Скорее всего, модели не хватает памяти или скриншот слишком большой."
        )

    except Exception as e:
        print("Ошибка анализа экрана:", e)
        return "Произошла ошибка при анализе экрана."