import pyperclip

from clipboard_actions import (
    read_clipboard,
    summarize_clipboard,
    explain_clipboard,
)

pyperclip.copy("print('Hello world')")

print(read_clipboard())
print(explain_clipboard())
print(summarize_clipboard())