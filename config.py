from pathlib import Path
from datetime import datetime

raw_counter = 0

WORKSPACE = Path.home() / "Desktop" / "V" / "workspace"

INCOMING = WORKSPACE / "incoming"

PHOTO_DIR = WORKSPACE / "photo"
PRINT_DIR = WORKSPACE / "print"

OLD_PH = PHOTO_DIR / "old_ph"
OLD_PR = PRINT_DIR / "old_pr"

FILTERED_DIR = OLD_PH / "filtered"
#CROPPED_DIR = WORKSPACE / "cropped"
#EDITED_DIR = WORKSPACE / "edited"

IMAGE_EXTS = [".jpg", ".jpeg", ".png"]

LOGO_PATH = WORKSPACE / "logo.png"

LOGO_MARGIN_PERCENT = 7
LOGO_SIZE_PERCENT = 10

PRINTER_DIR = WORKSPACE / "printer"

SESSION_BASE_DIR = PRINT_DIR

CURRENT_SESSION_DIR = None

SAFE_PADDING = 0.1 # 10% default safe area
SHOW_CENTER_LINES = True  # show center guides by default

# persistentm edit (global state)
CURRENT_EDITS = {
    "brightness": 0,
    "contrast": 0,
    "gamma": 0,
    "sharpness": 0,
}

CROPPED_IMAGES = {}  # key: extract_raw_number(Path (string)), value: True/False

def make_session_folder(base_dir: Path, name: str, restaurant: str) -> Path:
    date_str = datetime.now().strftime("%m.%d.%Y")
    folder_name = f"{date_str} {name} {restaurant}"
    folder_path = base_dir / folder_name
    folder_path.mkdir(parents=True, exist_ok=True)
    return folder_path

