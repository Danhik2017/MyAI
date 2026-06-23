import sounddevice as sd
import soundfile as sf
from faster_whisper import WhisperModel
import torch
import os
import numpy as np

from vad import contains_speech

os.environ["PATH"] += r";C:\ffmpeg\bin"

device = "cuda" if torch.cuda.is_available() else "cpu"

print(torch.__version__)
print(torch.version.cuda)
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))

wake_model = WhisperModel("tiny", device = device, compute_type="float16")

model = WhisperModel("medium", device=device, compute_type="float16")

def record_audio():

    sample_rate = 16000

    print("Слушаю...")

    chunks = []

    speach_started = False

    silence_after_speach = 0

    while True:

        audio = sd.rec(
            int(1.5 * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype="float32"
        )

        sd.wait()

        has_speech = contains_speech(audio)

        print("речь: ", has_speech)

        if not speach_started:

            if has_speech:

                print("Речь обнаружена")

                speach_started = True

                chunks.append(audio)

            continue

        chunks.append(audio)

        print(
            "Речь:",
            has_speech,
            "Размер записи:",
            len(chunks)
        )

        if has_speech:

            silence_after_speach = 0

        else:

            silence_after_speach += 1

        if silence_after_speach >= 2:
            break

    if len(chunks) == 0:

        print("Голос не обнаружен")

        return False

    recording = np.concatenate(chunks)

    sf.write(
        "input.wav",
        recording,
        sample_rate
    )

    return True

def speach_to_text():

    segments, info = model.transcribe(
        "input.wav",
         language="ru"
    )

    text = ""

    for segment in segments:
        text += segment.text

    return text.strip()

def record_wake_audio():

    samplerate = 16000

    recording = sd.rec(
        int(1.5 * samplerate),
        samplerate=samplerate,
        channels=1,
        dtype="float32"
    )

    sd.wait()

    sf.write(
        "wake.wav",
        recording,
        samplerate
    )

def wake_to_text():

    segments, info = wake_model.transcribe(
        "wake.wav",
        language="ru"
    )

    text = ""

    for segment in segments:
        text += segment.text

    return text.strip()