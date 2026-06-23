from window_action import get_open_windows

for window in get_open_windows():
    print(window.process_name, "|", window.title, "|", window.exe_path)