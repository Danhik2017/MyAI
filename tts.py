import re

import torch
import sounddevice as sd
import soundfile as sf
import asyncio
import tempfile
import edge_tts
from edge_tts import communicate

from text_prepare import replace_numbers

#--------- SILERO --------------
device = torch.device("cpu")

model, _ = torch.hub.load(
    repo_or_dir='snakers4/silero-models',
    model='silero_tts',
    language='ru',
    speaker='v4_ru'
)

model.to(device)


def clean_tts_text(text):

    # убираем ссылки
    text = re.sub(r'http\S+', '', text)

    # оставляем только буквы, цифры и основные знаки
    text = re.sub(
        r'[^а-яА-ЯёЁa-zA-Z0-9.,!?:;()\-\s]',
        '',
        text
    )

    return text

def speak(text):

    text = replace_numbers(text)

    text = clean_tts_text(text)

    if not text.strip():
        return

    audio = model.apply_tts(
        text=text,
        speaker='eugene',
        sample_rate=48000
    )

    sd.play(audio, 48000)
    sd.wait()
