from help_commands import handle_help_command

tests = [
    "что ты умеешь",
    "покажи команды",
    "подробная помощь",
    "полный список команд",
]

for command in tests:
    print("\nUSER:", command)
    print("ASSISTANT:", handle_help_command(command))