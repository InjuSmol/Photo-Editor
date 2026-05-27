import config
import shutil
from datetime import datetime

# CONTENT OVERVIEW: 

# log(msg) --> prints message in the terminal 
# finalize_to_print() --> moves a raw photo to print_folder and removes it from the photo folder
# ensure_dirs() --> makes sure we have all needed directories and creates them if needed
# get_next_raw_number() --> gets the next raw number
# archive_old_versions() --> archives different versions of the same picture (raw, cropped, logo) # TODO: need to be able to choose which versions we would want to keep 


# ================= FILE MANAGEMENT =================

def log(msg):
    print(f"[INFO] {msg}")


def finalize_to_print(raw_name):
    log(f"FINALIZED {raw_name}")
    archive_old_versions(raw_name)
    log("Workspace cleaned")


def ensure_dirs(name, restaurant):
    #date_str = datetime.now().strftime("%m.%d.%Y")
    #session_name = f"{date_str} {name} {restaurant}"

    dirs = [
        config.INCOMING,
        config.PHOTO_DIR,
        config.PRINT_DIR,
        config.OLD_PH,
        #config.PRINT_DIR / session_name, 
        config.FILTERED_DIR,
        config.OLD_PH / "raw",
        config.OLD_PH / "cropped",
        config.OLD_PH / "logo",
        config.OLD_PH / "edited", 
        config.PRINTER_DIR
    ]

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        log(f"Ready: {d}")


def get_next_raw_number():
    existing = list(config.PHOTO_DIR.glob("raw_*"))
    nums = []

    for f in existing:
        try:
            nums.append(int(f.stem.split("_")[1]))
        except:
            pass

    #return max(nums) + 1 if nums else 1
    return config.raw_counter


def archive_old_versions(raw_name):
    for stage in ["raw", "cropped", "logo"]:
        for f in config.PHOTO_DIR.glob(f"{stage}_{raw_name}*"):
            dest = config.OLD_PH / stage / f.name
            shutil.move(str(f), dest)
            log(f"Archived: {dest}")



