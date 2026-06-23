import pyperclip


MAX_READ_CHARS = 700
MAX_AI_CHARS = 5000


def get_clipboard_text() -> str:
    try:
        text = pyperclip.paste()
    except Exception as e:
        print("Ошибка чтения буфера обмена:", e)
        return ""

    return str(text).strip()


def read_clipboard() -> str:
    text = get_clipboard_text()

    if not text:
        return "Буфер обмена пуст."

    if len(text) > MAX_READ_CHARS:
        preview = text[:MAX_READ_CHARS].strip()
        return (
            f"В буфере обмена текст длиной примерно {len(text)} символов. "
            f"Начало такое: {preview}"
        )

    return f"В буфере обмена: {text}"


def summarize_clipboard() -> str:
    text = get_clipboard_text()

    if not text:
        return "Буфер обмена пуст."

    text_for_ai = text[:MAX_AI_CHARS]

    from ai import ask_ai

    return ask_ai(
        "Кратко перескажи содержимое буфера обмена на русском языке. "
        "Не используй markdown, если это не нужно. "
        "Вот текст:\n\n"
        f"{text_for_ai}"
    )


def explain_clipboard() -> str:
    text = get_clipboard_text()

    if not text:
        return "Буфер обмена пуст."

    text_for_ai = text[:MAX_AI_CHARS]

    from ai import ask_ai

    return ask_ai(
        "Объясни простыми словами, что означает этот текст или код. "
        "Если это код, объясни его назначение и основные части. "
        "Ответь на русском языке:\n\n"
        f"{text_for_ai}"
    )


def fix_clipboard_code() -> str:
    text = get_clipboard_text()

    if not text:
        return "Буфер обмена пуст."

    text_for_ai = text[:MAX_AI_CHARS]

    from ai import ask_ai

    return ask_ai(
        "Проверь этот код на ошибки. "
        "Объясни, что не так, и предложи исправленный вариант. "
        "Ответь на русском языке:\n\n"
        f"{text_for_ai}"
    )


def clear_clipboard() -> str:
    try:
        pyperclip.copy("")
        return "Очистил буфер обмена."
    except Exception as e:
        print("Ошибка очистки буфера обмена:", e)
        return "Не получилось очистить буфер обмена."