import shutil
from pathlib import Path
from core.logo import apply_logo_batch
import config 
from datetime import datetime

class FileActionManager:
    def __init__(self, photo_dir, print_dir, old_dir, printer_dir, session_dir=None):
        self.photo_dir = Path(photo_dir)
        self.print_dir = Path(print_dir)
        self.old_dir = Path(old_dir)
        self.printer_dir = Path(printer_dir)
        self.session_dir = Path(session_dir) if session_dir else None

    
    def set_session_dir(self, session_dir):
        self.session_dir = Path(session_dir)

    def _resolve_targets(self, selected_files, base_dir):
        if selected_files:
            return [Path(f) for f in selected_files]
        return list(base_dir.glob("*"))


    def add_logo(self, selected_files, position="top-right", auto_rotate_logo=False):
        targets = self._resolve_targets(selected_files, self.photo_dir)

        # move originals to old_ph
        originals = []
        for file in targets:
            if not file.is_file():
                continue

            old_path = self.old_dir / file.name
            shutil.move(file, old_path)
            originals.append(old_path)

        # apply logo to originals, save back to photo_dir
        apply_logo_batch(
            photos=originals,
            logo_path=config.LOGO_PATH,
            output_dir=self.photo_dir,
            position=position, 
            auto_rotate_logo=auto_rotate_logo
        )
        
    def move_to_print(self, selected_files, auto_print=True):
        targets = self._resolve_targets(selected_files, self.photo_dir)

        for file in targets:
            if not file.is_file():
                continue

            old_path = self.old_dir / file.name
            shutil.move(file, old_path)

            existing = list(self.print_dir.glob(f"print_*{file.suffix}"))
            next_num = len(existing) + 1

            new_name = f"print_{next_num}{file.suffix}"
            new_path = self.print_dir / new_name

            shutil.copy(old_path, new_path)

            # auto-send
            if auto_print:
                self.send_to_printer([new_path])

                
    def send_to_printer(self, selected_files=None):
        """Send files to printer hotfolder. Moves files to session folder afterward."""
        if self.session_dir is None:
            # Session hasn't started yet
            raise RuntimeError("Session folder not set. Call set_session_dir() first.")

        targets = self._resolve_targets(selected_files, self.print_dir)

        for file in targets:
            if not file.is_file():
                continue

            # 1. Copy to printer hotfolder
            shutil.copy(file, self.printer_dir / file.name)

            # 2. Move/organize in session folder
            self.session_dir.mkdir(parents=True, exist_ok=True)  # create if missing
            shutil.move(file, self.session_dir / file.name)