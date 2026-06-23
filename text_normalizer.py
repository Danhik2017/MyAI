from openai import OpenAI
from config import GROQ_API_KEY, MODEL


client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)


def normalize_vision_answer(raw_text: str, user_question: str | None = None) -> str:
    """
    Исправляет ответ vision-модели:
    - убирает смесь русских и английских букв;
    - переводит английские слова на русский;
    - делает речь естественной для голосового помощника;
    - не добавляет новых фактов.
    """
    raw_text = str(raw_text).strip()

    if not raw_text:
        return "Я посмотрел на экран, но не смог уверенно разобрать содержимое."

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """
Ты исправляешь текст, который пришёл от vision-модели.

Правила:
- Перепиши текст нормальным русским языком.
- Не добавляй новых фактов.
- Не выдумывай детали, которых нет в исходном тексте.
- Убери смесь латиницы и кириллицы внутри слов.
- Английские слова переведи на русский или запиши русской транскрипцией.
- Не используй markdown, списки, кавычки и технические пометки.
- Ответ должен звучать естественно для голосового помощника.
- Сохрани смысл исходного текста.
""".strip(),
                },
                {
                    "role": "user",
                    "content": f"""
Вопрос пользователя:
{user_question or "Что видно на экране?"}

Сырой ответ vision-модели:
{raw_text}

Исправленный русский ответ:
""".strip(),
                },
            ],
            temperature=0.1,
            max_tokens=250,
        )

        fixed_text = response.choices[0].message.content.strip()

        if not fixed_text:
            return raw_text

        return fixed_text

    except Exception as e:
        print("Ошибка нормализации vision-ответа:", e)
        return raw_text