from media_actions import handle_media_command

tests = [
    "сделай громче",
    "сделай тише",
    "сделай громче на 5",
    "выключи звук",
    "пауза",
    "следующий трек",
    "предыдущий трек",
]

for command in tests:
    print("\nTEST:", command)
    result = handle_media_command(command)
    print("RESULT:", result)