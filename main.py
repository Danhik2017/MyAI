from wakeword import wait_for_jarvis

from speach import (
    record_audio,
    speach_to_text,
)

from ai import (
    ask_ai,
    clear_memory
)

from tts import speak

from memory import save_fact

import time

from commands import handle_local_command

from action_logger import (
    log_user_input,
    log_local_command,
    log_ai_answer,
    log_error,
)

SESSION_TIMEOUT = 12

state = {
    "active": False,
    "last activity": time.time()
}

def is_session_expired():
    return time.time() - state["last activity"] > SESSION_TIMEOUT


def main():

    print("Джарвис запущен")

    while True:

        # режим ожидания
        if not state["active"]:

            wait_for_jarvis()

            state["active"] = True
            state["last activity"] = time.time()

        if not record_audio():
            continue

        text = speach_to_text()

        if not text:

            if is_session_expired():
                speak("Перехожу в режим ожидания")

                state["active"] = False

            continue

        print("Вы:", text)

        log_user_input(text)

        state["last activity"] = time.time()


        # -------------------КОМАНДЫ-----------------
        # очистка памяти
        if "очисти память" in text.lower():

            clear_memory()

            speak("Память очищена")

            continue

        # завершение диалога
        if any(
            phrase in text.lower()
            for phrase in [
                "отбой",
                "режим ожидания",
                "до свидания",
                "пока"
            ]
        ):

            speak("Перехожу в режим ожидания")

            state["active"] = False

            continue

        if text.lower().startswith("запомни"):
            fact = text[7:].strip()

            save_fact(fact)

            speak("Запомнил")

            continue
        #--------------------------------------------------

        try:
            local_answer = handle_local_command(text)

            if local_answer:
                if local_answer == "__SILENT__":
                    log_local_command(text, "silent dictation input")
                    state["last activity"] = time.time()
                    continue

                log_local_command(text, local_answer)

                print("Джарвис:", local_answer)
                speak(local_answer)

                state["last activity"] = time.time()
                continue

        except Exception as e:
            log_error("handle_local_command", e, user_text=text)
            print("Ошибка локальной команды:", e)

            error_answer = "Произошла ошибка при выполнении локальной команды."
            print("Джарвис:", error_answer)
            speak(error_answer)

            state["last activity"] = time.time()
            continue

        try:
            answer = ask_ai(text)

            log_ai_answer(text, answer)

            print("Джарвис:", answer)
            speak(answer)

        except Exception as e:
            log_error("ask_ai", e, user_text=text)

            answer = "Произошла ошибка при обращении к ИИ."
            print("Джарвис:", answer)
            speak(answer)

        state["last activity"] = time.time()

if __name__ == "__main__":
    main()