import json
import os

MEMORY_FILE = "memory.json"


def load_memory():

    if not os.path.exists(MEMORY_FILE):

        with open(
            MEMORY_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                {"facts": []},
                f,
                ensure_ascii=False,
                indent=4
            )

    with open(
        MEMORY_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def save_fact(fact):

    memory = load_memory()

    memory["facts"].append(fact)

    with open(
        MEMORY_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            memory,
            f,
            ensure_ascii=False,
            indent=4
        )


def get_memory_text():

    memory = load_memory()

    return "\n".join(
        memory["facts"]
    )