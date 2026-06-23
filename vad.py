import torch

from silero_vad import (
    load_silero_vad,
    get_speech_timestamps
)

model = load_silero_vad()


def contains_speech(audio):

    audio_tensor = torch.from_numpy(
        audio.flatten()
    )

    timestamps = get_speech_timestamps(
        audio_tensor,
        model,
        sampling_rate=16000
    )

    return len(timestamps) > 0