from tts import speak

TRIGGERS = [
    "джарвис",
    "джервис",
    "jarvis",
    "проснись",
    "нужна помощь",
    "простнись"
]

def is_wakeword(text):

    text = text.lower()

    return any(
        trigger in text
        for trigger in TRIGGERS
    )

from speach import (
    record_wake_audio,
    wake_to_text
)

def wait_for_jarvis():

    while True:

        record_wake_audio()

        text = wake_to_text()

        print("Wake:", text)

        if is_wakeword(text):

            speak("Слушаю")

            return