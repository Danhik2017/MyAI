from text_input_actions import handle_text_input_command

tests = [
    "напиши привет как дела",
    "введи import requests",
    "набери print('hello world')",
    "джарвис напиши это тестовый текст",
]

for command in tests:
    print("\nTEST:", command)
    result = handle_text_input_command(command)
    print("RESULT:", result)