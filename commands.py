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
        "проанализируй экран",
        "посмотри что происходит",
    ]

    if any(phrase in lower for phrase in screen_phrases):
        detailed = any(
            word in lower
            for word in [
                "подробно",
                "детально",
                "проанализируй",
                "объясни",
                "что происходит",
                "разбери",
            ]
        )

        return analyze_screen(
            question=text,
            detailed=detailed,
        )

    open_phrases = [
        "открой ",
        "запусти ",
        "включи ",
    ]

    for phrase in open_phrases:
        if lower.startswith(phrase):
            app_name = lower.replace(phrase, "", 1).strip()
            print("LOCAL COMMAND RAW:", repr(text))
            print("LOCAL COMMAND LOWER:", repr(lower))
            return open_app(app_name)


    return None
