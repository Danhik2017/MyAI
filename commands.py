from vision import analyze_screen
from actions import open_app


def handle_local_command(text: str) -> str | None:
    lower = text.lower().strip()

    screen_phrases = [
        "что на экране",
        "что сейчас на экране",
        "посмотри на экран",
        "что ты видишь",
        "опиши экран",
        "прочитай экран",
    ]

    if any(phrase in lower for phrase in screen_phrases):
        return analyze_screen(
            "Посмотри на скриншот экрана. "
            "Кратко опиши, что видно. "
            "Если есть важный текст, перескажи его."
        )

    open_phrases = [
        "открой ",
        "запусти ",
        "включи ",
    ]

    for phrase in open_phrases:
        if lower.startswith(phrase):
            app_name = lower.replace(phrase, "", 1).strip()
            return open_app(app_name)

    return None