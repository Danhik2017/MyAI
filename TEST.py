from keyboard_actions import handle_keyboard_command

tests = [
    "нажми энтер",
    "нажми escape",
    "скопируй",
    "вставь",
    "сохрани",
    "отмени",
    "выдели всё",
    "открой новую вкладку",
    "закрой вкладку",
    "обнови страницу",
]

for command in tests:
    print("\nTEST:", command)
    result = handle_keyboard_command(command)
    print("RESULT:", result)
    