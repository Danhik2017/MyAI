import re
import webbrowser
from urllib.parse import quote_plus


SITES = {
    "youtube": "https://youtube.com",
    "ютуб": "https://youtube.com",
    "ютюб": "https://youtube.com",

    "google": "https://google.com",
    "гугл": "https://google.com",

    "github": "https://github.com",
    "гитхаб": "https://github.com",

    "мой гитхаб": "https://github.com/Danhik2017",
    "мой github": "https://github.com/Danhik2017",

    "мой репозиторий": "https://github.com/Danhik2017/MyAI",
    "репозиторий": "https://github.com/Danhik2017/MyAI",
    "проект на гитхабе": "https://github.com/Danhik2017/MyAI",

    "chatgpt": "https://chatgpt.com",
    "чат gpt": "https://chatgpt.com",
    "чат джипити": "https://chatgpt.com",

    "gmail": "https://mail.google.com",
    "почта": "https://mail.google.com",

    "telegram": "https://web.telegram.org",
    "телеграм": "https://web.telegram.org",

    "vk": "https://vk.com",
    "вк": "https://vk.com",

    "stackoverflow": "https://stackoverflow.com",
    "stack overflow": "https://stackoverflow.com",
    "стак оверфлоу": "https://stackoverflow.com",

    "pypi": "https://pypi.org",
    "пайпи": "https://pypi.org",
}


SEARCH_PREFIXES = [
    "найди в гугле",
    "найди в google",
    "поищи в гугле",
    "поищи в google",
    "загугли",
    "найди в интернете",
    "поищи в интернете",
    "поиск в интернете",
]


OPEN_SITE_PREFIXES = [
    "открой сайт",
    "открой страницу",
    "открой",
    "перейди на",
    "зайди на",
]


def normalize_web_text(text: str) -> str:
    text = str(text).lower().strip()

    wake_words = [
        "джарвис",
        "jarvis",
        "джервис",
        "жарвис",
    ]

    for word in wake_words:
        text = re.sub(rf"\b{re.escape(word)}\b", " ", text)

    text = text.replace("точка", ".")
    text = text.replace("слэш", "/")
    text = text.replace("двоеточие", ":")
    text = text.replace("дефис", "-")

    text = re.sub(r"[^\w\sа-яА-ЯёЁ./:-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def looks_like_url(text: str) -> bool:
    text = text.strip().lower()

    if not text:
        return False

    # Убираем финальную пунктуацию от STT
    text = text.strip(".,!?;: ")

    if text.startswith("http://") or text.startswith("https://"):
        return True

    if text.startswith("www."):
        return True

    # Если есть кириллица, не считаем это URL.
    # Иначе "блокнот." превращается в сайт.
    if re.search(r"[а-яА-ЯёЁ]", text):
        return False

    # Нормальный домен: google.com, github.com, example.ru
    domain_pattern = r"^[a-z0-9-]+(\.[a-z0-9-]+)+(/[^\s]*)?$"

    return re.match(domain_pattern, text) is not None


def normalize_url(text: str) -> str:
    url = text.strip().strip(".,!?;: ")

    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    return url


def open_url(url: str) -> str:
    try:
        webbrowser.open(url)
        return "Открываю сайт."
    except Exception as e:
        print("Ошибка открытия сайта:", e)
        return "Не получилось открыть сайт."


def open_known_site(site_name: str) -> str | None:
    name = normalize_web_text(site_name)

    if name in SITES:
        webbrowser.open(SITES[name])
        return f"Открываю {name}."

    for key, url in SITES.items():
        if key in name:
            webbrowser.open(url)
            return f"Открываю {key}."

    return None


def google_search(query: str) -> str:
    query = query.strip()

    if not query:
        return "Я не понял, что нужно найти."

    url = "https://www.google.com/search?q=" + quote_plus(query)

    try:
        webbrowser.open(url)
        return f"Ищу в интернете: {query}."
    except Exception as e:
        print("Ошибка поиска в браузере:", e)
        return "Не получилось открыть поиск."


def extract_search_query(text: str) -> str | None:
    lower = normalize_web_text(text)

    for prefix in SEARCH_PREFIXES:
        if lower.startswith(prefix + " "):
            return lower.replace(prefix, "", 1).strip()

    return None


def extract_site_to_open(text: str) -> str | None:
    lower = normalize_web_text(text)

    for prefix in OPEN_SITE_PREFIXES:
        if lower.startswith(prefix + " "):
            return lower.replace(prefix, "", 1).strip()

    return None


def handle_web_command(text: str) -> str | None:
    lower = normalize_web_text(text)

    print("WEB COMMAND:", repr(lower))

    search_query = extract_search_query(lower)

    if search_query:
        return google_search(search_query)

    site_to_open = extract_site_to_open(lower)

    if site_to_open:
        known_result = open_known_site(site_to_open)

        if known_result:
            return known_result

        # Открываем как URL только если это реально похоже на URL
        if looks_like_url(site_to_open):
            return open_url(normalize_url(site_to_open))

        # Важно: если это не известный сайт и не URL,
        # ничего не делаем, чтобы "открой блокнот" не стало сайтом.
        return None

    return None