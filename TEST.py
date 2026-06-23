from mouse_actions import handle_mouse_command

tests = [
    "покажи сетку экрана"
]

for command in tests:
    print("\nUSER:", command)
    result = handle_mouse_command(command)
    print("RESULT:", result)