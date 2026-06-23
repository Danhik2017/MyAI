import json
import re
from datetime import datetime
from pathlib import Path


LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "actions.jsonl"

MAX_TEXT_LENGTH = 700


SECRET_PATTERNS = [
    # Groq / OpenAI-like keys
    r"gsk_[A-Za-z0-9_\-]+",
    r"sk-[A-Za-z0-9_\-]+",

    # generic API key fragments
    r"api[_-]?key\s*[:=]\s*[A-Za-z0-9_\-]+",
    r"token\s*[:=]\s*[A-Za-z0-9_\-]+",
    r"password\s*[:=]\s*\S+",
    r"пароль\s*[:=]\s*\S+",
]


def redact_secrets(text: str | None) -> str:
    if text is None:
        return ""

    result = str(text)

    for pattern in SECRET_PATTERNS:
        result = re.sub(
            pattern,
            "[REDACTED]",
            result,
            flags=re.IGNORECASE,
        )

    return result


def shorten_text(text: str | None, max_length: int = MAX_TEXT_LENGTH) -> str:
    text = redact_secrets(text)

    if len(text) <= max_length:
        return text

    return text[:max_length].rstrip() + "...[TRUNCATED]"


def log_event(
    event_type: str,
    user_text: str | None = None,
    action: str | None = None,
    result: str | None = None,
    error: str | None = None,
    meta: dict | None = None,
):
    """
    Пишет одну строку JSONL.
    JSONL удобен тем, что каждая строка — отдельное событие.
    """
    try:
        LOG_DIR.mkdir(exist_ok=True)

        event = {
            "time": datetime.now().isoformat(timespec="seconds"),
            "event_type": event_type,
            "user_text": shorten_text(user_text),
            "action": shorten_text(action),
            "result": shorten_text(result),
            "error": shorten_text(error),
            "meta": meta or {},
        }

        with open(LOG_FILE, "a", encoding="utf-8") as file:
            file.write(json.dumps(event, ensure_ascii=False) + "\n")

    except Exception as e:
        # Логгер не должен ломать ассистента
        print("Ошибка записи лога:", e)


def log_user_input(text: str):
    log_event(
        event_type="user_input",
        user_text=text,
    )


def log_local_command(user_text: str, result: str):
    log_event(
        event_type="local_command",
        user_text=user_text,
        result=result,
    )


def log_ai_answer(user_text: str, answer: str):
    log_event(
        event_type="ai_answer",
        user_text=user_text,
        result=answer,
    )


def log_error(place: str, error: Exception | str, user_text: str | None = None):
    log_event(
        event_type="error",
        user_text=user_text,
        action=place,
        error=str(error),
    )
    
def get_last_logs_text(count: int = 5) -> str:
    if not LOG_FILE.exists():
        return "Логов пока нет."

    try:
        lines = LOG_FILE.read_text(encoding="utf-8").splitlines()
        last_lines = lines[-count:]

        if not last_lines:
            return "Логов пока нет."

        summaries = []

        for line in last_lines:
            event = json.loads(line)

            event_type = event.get("event_type", "")
            user_text = event.get("user_text", "")
            result = event.get("result", "")
            error = event.get("error", "")

            if error:
                summaries.append(f"Ошибка в {event_type}: {error}")
            elif result:
                summaries.append(f"Команда: {user_text}. Результат: {result}")
            else:
                summaries.append(f"Событие: {event_type}. Текст: {user_text}")

        return "Последние события: " + " ".join(summaries)

    except Exception as e:
        print("Ошибка чтения логов:", e)
        return "Не получилось прочитать логи."