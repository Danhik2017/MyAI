from openai import OpenAI

from memory import get_memory_text

from config import (
    GROQ_API_KEY,
    MODEL,
    SYSTEM_PROMPT
)

from intertent import search_web

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)


MAX_HISTORY = 20

def build_system_prompt():
    memory_text = get_memory_text()

    return (
        SYSTEM_PROMPT + "\n\nПамять позьзователя:\n" +
        memory_text
    )

conversation = [
    {
        "role": "system",
        "content": build_system_prompt()
    }]

def needs_internet(user_input):

    try:

        response = client.chat.completions.create(
            model=MODEL,
            messages= [
                {
                    "role": "system",
                    "content":
                    """
                    Ответь строго одним словом.
                    
                    INTERNET - если нужен поиск в интернете.
                    
                    CHAT - если можешь ответить из общих знаний.
                    
                    Никаких объяснений.
                    Только INTERNET или CHAT.
                    """
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            temperature=0,
            max_tokens=3
        )

        result = (
            response
            .choices[0]
            .message.content
            .strip()
            .upper()
        )

        print("Тип запроса:", result)

        return "INTERNET" in result

    except Exception as e:

        print("Ошибка классификации:", e)

        return False

def ask_ai(user_input):

    global conversation

    try:

        system_prompt = build_system_prompt()

        if not conversation:

            conversation.append(
                {
                    "role": "system",
                    "content": system_prompt
                }
            )

        if needs_internet(user_input):

            print("Поиск в интернете...")

            results = search_web(user_input)

            print("\n===== SEARCH RESULTS =====")

            for i, item in enumerate(results):
                print(f"\nРезультат {i + 1}")

                print("TITLE:", item.get("title"))

                print("BODY:", item.get("body"))

                print("URL:", item.get("url"))

            print("==========================\n")

            web_context = ""

            if results:
                for item in results:

                    title = item.get("title", "")
                    body = item.get("body", "")

                    web_context += (
                        f"Заголовки: {title}\n"
                        f"Описание: {body}\n"
                    )

            else:
                web_context = "Результаты поиска отсутствуют."

            internet_prompt = f"""
            Ты используешь интернет-данные для ответа.

            ДАННЫЕ ИЗ ПОИСКА:
            {web_context}

            ВОПРОС:
            {user_input}

            Ответь на основе данных выше.
            """

            conversation.append({
                "role": "user",
                "content": internet_prompt
            })

        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages = conversation,
                temperature=0.7,
                max_tokens=300
            )

            answer = response.choices[0].message.content

            conversation.append(
                {
                    "role": "assistant",
                    "content": answer
                }
            )

            if len(conversation) > MAX_HISTORY + 1:
                conversation = [
                    conversation[0]
                    ] + conversation[-MAX_HISTORY:]

            return answer

        except Exception as e:

            print(e)

            return "Извините, произошла ошибка"

    except Exception as e:

        print("Ошибка Groq:", e)

        return "Произошла ошибка"


def clear_memory():

    global conversation

    conversation = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]