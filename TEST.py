from dictation_mode import handle_dictation_mode

tests = [
    "начни диктовку",
    "первая строка",
    "новая строка",
    "вторая строка",
    "абзац",
    "третья строка",
    "стоп диктовка",
]

for command in tests:
    print("\nUSER:", command)
    result = handle_dictation_mode(command)
    print("RESULT:", result)

