import mss

from ollama import chat

def screenshot():

    with mss.mss() as sct:
        path = sct.shot()

    return path

# def analyse_screen():
#
#     image_path = screenshot()
#
#     response = chat(
#         model = "qwen2.5v1:7b",
#         messages =[
#             {
#                 "role": "user",
#                 "content": "Опиши что изображено на экране компьютера",
#                 "images": [image_path]
#             }
#         ]
#     )
#
#     return response["messages"]["content"]