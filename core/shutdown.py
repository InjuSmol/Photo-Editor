import shutil
from pathlib import Path
import config
from PySide6.QtCore import QObject, Signal

# TODO: Make all the print final pictures 
# from PRINT folder to be inside the PRINT/name_restuarant_name_date folder


class ShutdownManager(QObject):
    shutdown_requested = Signal()

    def __init__(self):
        super().__init__()
        self._is_shutting_down = False

    def request_shutdown(self):
        if self._is_shutting_down:
            return
        #self._is_shutting_down = True
        print("[INFO] Shutdown requested")
        self.shutdown_requested.emit()

    def cleanup_session(self):
        print("[INFO] Cleaning up session folders")

        workspace = config.WORKSPACE
        old_ph = config.OLD_PH
        raw_dir = old_ph

        # 1️ Ensure raw destination exists
        raw_dir.mkdir(parents=True, exist_ok=True)

        # 2️ Collect ALL raw* files from workspace
        for path in workspace.rglob("raw*"):
            if path.is_file() and path.parent != raw_dir:
                try:
                    shutil.move(str(path), raw_dir / path.name)
                    print(f"[INFO] Moved {path.name} → raw/")
                except Exception as e:
                    print(f"[WARN] Failed to move {path}: {e}")

        # 3️ Delete everything except:
        # - print/
        # - photo/old_ph/raw
        for item in workspace.iterdir():

            # Preserve print
            if item == config.PRINT_DIR:
                continue

            # Preserve photo/old_ph (but clean inside)
            if item == config.PHOTO_DIR:
                for sub in item.iterdir():
                    if sub == old_ph:
                        # clean old_ph except raw
                        for x in old_ph.iterdir():
                            if x != raw_dir:
                                shutil.rmtree(x, ignore_errors=True)
                        continue
                    shutil.rmtree(sub, ignore_errors=True)
                continue

            # Remove everything else
            shutil.rmtree(item, ignore_errors=True)

        print("[INFO] Cleanup completed successfully")     
'''
    def cleanup_session(self):
        print("[INFO] Cleaning up session folders")

        # 1️ Ensure raw folder exists
        raw_dest = config.OLD_PH / "raw"
        raw_dest.mkdir(parents=True, exist_ok=True)

        # 2️ Collect RAW files from everywhere
        for folder in [
            config.PHOTO_DIR,
            config.FILTERED_DIR,
            config.OLD_PH,
        ]:
            if not folder.exists():
                continue

            for f in folder.rglob("raw_*"):
                if f.is_file():
                    shutil.move(str(f), raw_dest / f.name)

        # 3️ Delete everything except raw + print
        for folder in config.WORKSPACE.iterdir():
            if folder.name in ["print", "old_ph"]:
                continue
            shutil.rmtree(folder, ignore_errors=True)

        # 4️ Clean old_ph except raw
        if config.OLD_PH.exists():
            for sub in config.OLD_PH.iterdir():
                if sub.name != "raw":
                    shutil.rmtree(sub, ignore_errors=True)
        print("[INFO] Cleanup complete")
'''
