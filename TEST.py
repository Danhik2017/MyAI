from commands import handle_local_command

tests = [
    "напиши привет и нажми enter",
    "напиши hello world и нажми enter",
    "открой блокнот и напиши привет",
    "скопируй и открой новую вкладку и вставь",
]

for command in tests:
    print("\nTEST:", command)
    result = handle_local_command(command)
    print("RESULT:", result)