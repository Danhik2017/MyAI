from ddgs import DDGS


def clean_query(query: str) -> str:
    query = query.strip()

    trash_phrases = [
        "найди в интернете",
        "поищи в интернете",
        "загугли",
        "посмотри в интернете",
        "что там по",
        "расскажи про",
    ]

    lowered = query.lower()

    for phrase in trash_phrases:
        lowered = lowered.replace(phrase, "")

    return lowered.strip() or query


def search_web(query: str, max_results: int = 5) -> list[dict]:
    query = clean_query(query)

    try:
        with DDGS(timeout=10) as ddgs:
            raw_results = ddgs.text(
                query=query,
                region="ru-ru",
                safesearch="moderate",
                max_results=max_results,
                backend="auto",
            )

        results = []

        for item in raw_results:
            title = item.get("title", "").strip()
            href = item.get("href", "").strip()
            body = item.get("body", "").strip()

            if not title or not href:
                continue

            results.append({
                "title": title,
                "url": href,
                "body": body,
            })

        return results

    except Exception as e:
        print("Ошибка поиска:", e)
        return []