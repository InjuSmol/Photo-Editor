# IncomingHandler Class 
# Observer Logic
# But not input(), show_menu()
# Just auto-move + emit event

# TODO: What is emit? 

# Runs forever
# Does not block UI
# Same logic as CLI, just isolated

from PySide6.QtCore import QThread
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import time
import config
from core.file_manager import log, get_next_raw_number
import shutil

class IncomingHandler(FileSystemEventHandler):

    def on_created(self, event):
        if event.is_directory:
            return

        path = Path(event.src_path)

        if path.suffix.lower() not in [".jpg", ".jpeg", ".png"]:
            return
        
        config.raw_counter +=1
        raw_number = get_next_raw_number()
        
        new_name = f"raw_{raw_number}{path.suffix}"
        dest = config.PHOTO_DIR / new_name
        config.CROPPED_IMAGES[raw_number] = False

        shutil.move(str(path), dest)
        log(f"New photo detected → {new_name}")

class WatcherThread(QThread):
    def __init__(self):
        super().__init__()
        self._running = True
        self.observer = None

    def run(self):
        log("Watcher thread started")

        self.observer = Observer()
        handler = IncomingHandler()
        self.observer.schedule(handler, str(config.INCOMING), recursive=False)
        self.observer.start()

        try:
            while self._running:
                time.sleep(0.5)
        finally:
            log("Stopping watchdog observer")
            self.observer.stop()
            self.observer.join()

        log("Watcher thread stopped")

    def stop(self):
        print("[INFO] Stopping watcher thread")
        self._running = False

    def on_new_file_in_print(self, file_path):
        if self.app.auto_print_enabled:
            self.file_actions.send_to_printer([file_path])