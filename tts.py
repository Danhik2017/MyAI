# tts.py
import re
import torch
import sounddevice as sd
from text_prepare import replace_numbers

# --------- SILERO --------------

device = torch.device("cpu")

model, _ = torch.hub.load(
    repo_or_dir="snakers4/silero-models",
    model="silero_tts",
    language="ru",
    speaker="v4_ru",
)

model.to(device)


LATIN_REPLACEMENTS = {
    "ollama": "оллама",
    "chrome": "хром",
    "google chrome": "гугл хром",
    "edge": "эдж",
    "vscode": "ви эс код",
    "vs code": "ви эс код",
    "visual studio code": "вижуал студио код",
    "windows": "виндовс",
    "python": "пайтон",
    "github": "гитхаб",
    "api": "эй пи ай",
    "url": "ссылка",
    "http": "",
    "https": "",
}


def replace_latin_words(text: str) -> str:
    lowered = text

    for latin, russian in LATIN_REPLACEMENTS.items():
        pattern = re.compile(re.escape(latin), re.IGNORECASE)
        lowered = pattern.sub(russian, lowered)

    return lowered


def clean_tts_text(text: str) -> str:
    text = str(text)

    # убираем ссылки
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"www\.\S+", "", text)

    # заменяем частые английские слова на русское звучание
    text = replace_latin_words(text)

    # убираем markdown и технические символы
    text = text.replace("`", " ")
    text = text.replace("*", " ")
    text = text.replace("#", " ")
    text = text.replace("_", " ")
    text = text.replace("|", " ")
    text = text.replace("\\", " ")
    text = text.replace("/", " ")

    # тире разных типов приводим к обычному
    text = text.replace("—", "-")
    text = text.replace("–", "-")

    # для русской Silero лучше убрать оставшуюся латиницу
    text = re.sub(r"[a-zA-Z]+", "", text)

    # оставляем только безопасные символы для русской TTS
    text = re.sub(
        r"[^а-яА-ЯёЁ0-9.,!?:;()\- ]",
        " ",
        text,
    )

    # схлопываем пробелы
    text = re.sub(r"\s+", " ", text).strip()

    return text


def split_text(text: str, max_len: int = 250) -> list[str]:
    """
    Silero иногда падает на длинных кусках текста.
    Поэтому режем ответ на короткие фразы.
    """
    parts = re.split(r"(?<=[.!?])\s+", text)
    result = []

    current = ""

    for part in parts:
        if len(current) + len(part) <= max_len:
            current = f"{current} {part}".strip()
        else:
            if current:
                result.append(current)
            current = part

    if current:
        result.append(current)

    return result


def speak(text: str):
    try:
        text = clean_tts_text(text)

        if not text:
            return

        text = replace_numbers(text)
        text = clean_tts_text(text)

        if not text:
            return

        chunks = split_text(text)

        for chunk in chunks:
            if not chunk.strip():
                continue

            audio = model.apply_tts(
                text=chunk,
                speaker="eugene",
                sample_rate=48000,
            )

            sd.play(audio, 48000)
            sd.wait()

    except ValueError as e:
        print("Ошибка TTS ValueError. Текст не удалось озвучить:", repr(text))
        print("Подробности:", e)

    except Exception as e:
        print("Ошибка TTS:", e)
        print("Текст:", repr(text))