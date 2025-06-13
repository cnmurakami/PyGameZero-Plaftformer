import time
import subprocess
import os
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pygetwindow as gw

WINDOW_POS_FILE = "window_position.txt"
WATCHED_FILES = ["main.py", "classes.py", "global_variables.py"]  # Files to watch
SCRIPT_FILE = "main.py"  # The main file to run with pgzrun

# --- Load window position ---
def load_window_position():
    try:
        with open(WINDOW_POS_FILE, "r") as f:
            x, y = f.read().strip().split(",")
            os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x},{y}"
            print(f"Loaded window position: {x}, {y}")
    except FileNotFoundError:
        os.environ['SDL_VIDEO_WINDOW_POS'] = "100,100"

# --- Save window position ---
def save_window_position():
    BORDER_X = 8
    TITLE_BAR_Y = 30
    try:
        for win in gw.getWindowsWithTitle("My Game Window"):
            if win.left != -32000:
                corrected_x = win.left + BORDER_X
                corrected_y = win.top + TITLE_BAR_Y
                with open(WINDOW_POS_FILE, "w") as f:
                    f.write(f"{corrected_x},{corrected_y}")
                print(f"Saved window position: {corrected_x},{corrected_y}")
                return
        print("Game window not found.")
    except Exception as e:
        print("Error saving window position:", e)

# --- Handler class ---
class ReloadHandler(FileSystemEventHandler):
    def __init__(self, watched_files, script_file):
        self.watched_files = [Path(f).resolve() for f in watched_files]
        self.script_file = Path(script_file).resolve()
        self.process = None
        self.start_game()

    def start_game(self):
        load_window_position()
        print(f"Launching: pgzrun {self.script_file.name}")
        self.process = subprocess.Popen(["pgzrun", str(self.script_file)])

    def restart_game(self):
        if self.process:
            save_window_position()
            print("Stopping game...")
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
        print("Restarting game...")
        self.start_game()

    def on_modified(self, event):
        changed_path = Path(event.src_path).resolve()
        if changed_path in self.watched_files:
            print(f"Detected change in {changed_path.name}")
            self.restart_game()

    def stop(self):
        if self.process:
            save_window_position()
            self.process.terminate()
            self.process.wait()

# --- Main loop ---
if __name__ == "__main__":
    handler = ReloadHandler(WATCHED_FILES, SCRIPT_FILE)
    observer = Observer()
    observer.schedule(handler, ".", recursive=True)  # Set to True to catch subfolders
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down watcher...")
        observer.stop()
        handler.stop()
    observer.join()