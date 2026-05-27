import argparse
import shutil
import time
from datetime import datetime
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image, ImageEnhance
import numpy as np

import config



# ================= CONFIG =================

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

raw_counter = 1

LOGO_PATH = WORKSPACE / "logo.png"



# ================= UTIL =================

def log(msg):
    print(f"[INFO] {msg}")


def ensure_dirs():
    dirs = [
        INCOMING,
        PHOTO_DIR,
        PRINT_DIR,
        OLD_PH,
        OLD_PR,
        FILTERED_DIR,
        #CROPPED_DIR,
        #EDITED_DIR,
        OLD_PH / "raw",
        OLD_PH / "cropped",
        OLD_PH / "logo",
        OLD_PH / "edited"
    ]

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        log(f"Ready: {d}")


def get_next_raw_number():
    existing = list(PHOTO_DIR.glob("raw_*"))
    nums = []

    for f in existing:
        try:
            nums.append(int(f.stem.split("_")[1]))
        except:
            pass

    return max(nums) + 1 if nums else 1


# ================= FILE MANAGEMENT =================

def archive_old_versions(raw_name):
    for stage in ["raw", "cropped", "logo"]:
        for f in PHOTO_DIR.glob(f"{stage}_{raw_name}*"):
            dest = OLD_PH / stage / f.name
            shutil.move(str(f), dest)
            log(f"Archived: {dest}")


def finalize_to_print(raw_name):
    log(f"FINALIZED {raw_name}")
    archive_old_versions(raw_name)
    log("Workspace cleaned")


# ================= INTERACTIVE MENU =================

def show_menu():
    print("\n========= ACTION MENU =========")
    print("1) crop")
    print("2) insert_logo")
    print("3) finalize_print")
    print("4) list")
    print("5) skip")
    print("===============================")

    return input("Select option: ").strip()


def list_status():
    print("\n--- ACTIVE PHOTOS ---")

    for f in PHOTO_DIR.glob("*"):
        if f.is_file():
            print(" ", f.name)

    print("----------------------")


# ================= WATCHER =================

class IncomingHandler(FileSystemEventHandler):

    def on_created(self, event):
        global raw_counter

        if event.is_directory:
            return

        path = Path(event.src_path)

        if path.suffix.lower() not in IMAGE_EXTS:
            return

        log("NEW PICTURE DETECTED")

        raw_counter = get_next_raw_number()

        new_name = f"raw_{raw_counter}{path.suffix}"
        dest = PHOTO_DIR / new_name

        shutil.move(str(path), dest)

        log(f"Renamed -> {new_name}")
        log("Moved to photo folder")

        while True:
            action = show_menu()

            if action == "1":
                log("Crop selected (coming soon)")
            elif action == "2":
                log("Insert logo selected (coming soon)")
            elif action == "3":
                finalize_to_print(new_name)
                break
            elif action == "4":
                list_status()
            elif action == "5":
                log("Skipped")
                break
            else:
                print("Invalid choice")


# ================= CLI COMMANDS =================

def cmd_start(args):
    restaurant = args.RN
    name = args.N

    log("Starting VISTA system")

    ensure_dirs()

    today = datetime.now().strftime("%m.%d.%Y")
    session_name = f"{today} {name} {restaurant}"

    session_dir = OLD_PR / session_name
    session_dir.mkdir(exist_ok=True)

    log(f"Print archive created:")
    log(session_dir)

    log("Watching for new photos...")
    log("DROP FILES INTO: incoming folder")

    handler = IncomingHandler()
    observer = Observer()
    observer.schedule(handler, str(INCOMING), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log("Stopping watcher")
        observer.stop()

    observer.join()


def cmd_filter(args):
    files = args.files
    log("Filtering photos")

    if not files:
        log("Filtering ALL photos")
    else:
        log(f"Filtering selected: {files}")

    log("Filter logic coming soon")


def cmd_crop(args):
    files = args.files
    log("Cropping photos")

    if not files:
        log("Cropping ALL photos")
    else:
        log(f"Cropping selected: {files}")

    log("Crop logic coming soon")

###################################################################################
def cmd_insert_logo(args): # ARGS: files=, pos=

    position = args.pos.lower()
    # 1. CHECK IF THE LOGO EXISTS: 
    if not config.LOGO_PATH.exists():
        log("ERROR: logo.png not found in workspace")
        return
    # EXTRACT THE POSITION TO APPLY
    # TODO: if no position make the right the default
    if position not in ["left", "right"]: # TODO: add the bottom position too + for the vertical/horizontal
        log("ERROR: position must be left or right")
        return
    # 2. EXTRACT FILES NAMES FROM THE ARGS (IF ANY)
    files = args.files

    # 3. SELECT FILES: 
    if files:
        targets = [config.PHOTO_DIR / f for f in files]
    else:
        targets = list(config.PHOTO_DIR.glob("raw_*")) # TODO: change this: it can be any, not only raw photo
    # IF NOT FILES: 
    if not targets:
        log("No photos found to apply logo")
        return
    # 4. LOGS TO TERMINAL: 
    log(f"Applying logo to {len(targets)} photo(s)")
    log(f"Position: top-{position}")
    # 5. CONVERT THE LOGO IMAGE TO RGBA
    logo_original = Image.open(config.LOGO_PATH).convert("RGBA")

    # 6. PROCESS EACH PHOTO: 
    for photo_path in targets:
        # if photo doesn't exist: 
        if not photo_path.exists():
            log(f"Skipping missing file: {photo_path.name}")
            continue
        # CONVERT IMAGE INTO RGBA: TODO: Does this RGBA conversion lower the quality? can I avoid it? 
        img = Image.open(photo_path).convert("RGBA")
        # Extract the image sizes: 
        img_w, img_h = img.size

        # 7. RESIZE LOGO TO logo_size OF IMAGE WIDTH
        logo_size = 0.10 # default 10%
        target_logo_width = int(img_w * logo_size) # TODO: make the size an optional argument
        # 8. CALCULATE THE LOGO HEIGHT: 
        ratio = target_logo_width / logo_original.width
        new_height = int(logo_original.height * ratio)
        # 9. NEW LOGO OF THE RIGHT SIZE: 
        logo = logo_original.resize(
            (target_logo_width, new_height),
            Image.LANCZOS
        )

        padding = 10 # TODO: make this optional? or what? 
        # 10. CALCULATE THE POSITION OF THE LOGO: 
        if position == "right":
            x = img_w - target_logo_width - padding
        else:
            x = padding

        y = padding
        # TODO: What arguments are these: 
        img.paste(logo, (x, y), logo)

        # SAVE (as new stage file):
        new_name = f"logo_{photo_path.name}"
        out_path = config.PHOTO_DIR / new_name

        img.convert("RGB").save(out_path)

        log(f"Logo added -> {new_name}")

        # Archive old raw
        #dest = OLD_PH / "logo" / photo_path.name
        #shutil.move(photo_path, dest)
        #log(f"Archived old version -> {dest.name}")

#############################################################################
        

def apply_gamma(image, gamma):
    inv_gamma = 1.0 / gamma

    table = [
        int(((i / 255.0) ** inv_gamma) * 255)
        for i in range(256)
    ]

    return image.point(table * 3)



def cmd_auto_edit(args):
    log("Auto edit pipeline coming soon")


def cmd_edit(args):

    files = args.files

    # Select active photos
    if files:
        targets = [PHOTO_DIR / f for f in files]
    else:
        targets = list(PHOTO_DIR.glob("*"))

    if not targets:
        log("No photos found to edit")
        return

    log(f"Editing {len(targets)} photo(s)")

    for photo_path in targets:

        if not photo_path.exists():
            log(f"Skipping missing file: {photo_path.name}")
            continue

        img = Image.open(photo_path).convert("RGB")

        log(f"Processing: {photo_path.name}")

        # ---------- APPLY ADJUSTMENTS ----------

        if args.brightness:
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(args.brightness)
            log(f"  Brightness -> {args.brightness}")

        if args.contrast:
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(args.contrast)
            log(f"  Contrast -> {args.contrast}")

        if args.sharpness:
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(args.sharpness)
            log(f"  Sharpness -> {args.sharpness}")

        if args.gamma:
            img = apply_gamma(img, args.gamma)
            log(f"  Gamma -> {args.gamma}")

        # ---------- SAVE NEW VERSION ----------

        new_name = f"edit_{photo_path.name}"
        out_path = PHOTO_DIR / new_name

        img.save(out_path, quality=95)

        log(f"Saved edited version -> {new_name}")

        # ---------- ARCHIVE OLD VERSION ----------

        dest = OLD_PH / "edited" / photo_path.name
        dest.parent.mkdir(exist_ok=True)

        shutil.move(photo_path, dest)

        log(f"Archived previous version -> {dest.name}")



# ================= CLI SETUP =================

def main():

    parser = argparse.ArgumentParser(description="VISTA Photo Automation System")

    subparsers = parser.add_subparsers(dest="command")

    # START
    start_parser = subparsers.add_parser("start", help="Start photo booth system")
    start_parser.add_argument("RN", help="Restaurant name")
    start_parser.add_argument("N", help="Your name")
    start_parser.set_defaults(func=cmd_start)

    # FILTER
    filter_parser = subparsers.add_parser("filter")
    filter_parser.add_argument("files", nargs="*")
    filter_parser.set_defaults(func=cmd_filter)

    # CROP
    crop_parser = subparsers.add_parser("crop")
    crop_parser.add_argument("files", nargs="*")
    crop_parser.set_defaults(func=cmd_crop)

    # INSERT LOGO
    logo_parser = subparsers.add_parser("insert_logo")
    logo_parser.add_argument("files", nargs="*")
    logo_parser.add_argument(
        "--pos",
        default="right",
        help="Logo position: left or right (default: right)"
    )
    logo_parser.set_defaults(func=cmd_insert_logo)


    # AUTO EDIT
    auto_edit_parser = subparsers.add_parser("auto_edit")
    auto_edit_parser.set_defaults(func=cmd_auto_edit)

    # MANUAL EDIT
    edit_parser = subparsers.add_parser("edit")

    edit_parser.add_argument(
        "files",
        nargs="*",
        help="Optional list of image filenames"
    )

    edit_parser.add_argument("-B", "--brightness", type=float)
    edit_parser.add_argument("-S", "--sharpness", type=float)
    edit_parser.add_argument("-C", "--contrast", type=float)
    edit_parser.add_argument("-G", "--gamma", type=float)

    edit_parser.set_defaults(func=cmd_edit)


    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    args.func(args)


# ================= ENTRY =================

if __name__ == "__main__":
    main()