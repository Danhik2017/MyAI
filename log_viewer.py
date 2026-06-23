import json
from pathlib import Path


LOG_FILE = Path("logs/actions.jsonl")


def show_last_logs(count: int = 20):
    if not LOG_FILE.exists():
        print("Логов пока нет.")
        return

    lines = LOG_FILE.read_text(encoding="utf-8").splitlines()
    last_lines = lines[-count:]

    for line in last_lines:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            print(line)
            continue

        print("-" * 60)
        print("TIME:", event.get("time"))
        print("TYPE:", event.get("event_type"))
        print("USER:", event.get("user_text"))
        print("ACTION:", event.get("action"))
        print("RESULT:", event.get("result"))
        print("ERROR:", event.get("error"))


if __name__ == "__main__":
    show_last_logs()