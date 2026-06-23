from num2words import num2words
import re

def replace_numbers(text):

    def repl(match):

        number = int(match.group())

        try:
            return num2words(
                number,
                lang="ru"
            )
        except:
            return str(number)

    return re.sub(
        r"\d+",
        repl,
        text
    )
