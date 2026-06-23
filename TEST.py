from tts import speak

tests = [
    "Произошла ошибка при анализе экрана.",
    "Ollama разорвал соединение во время анализа экрана.",
    "На экране открыт VS Code и Chrome.",
    "Ошибка API: http://localhost:11434/api/tags",
]

for text in tests:
    print("TEST:", text)
    speak(text)