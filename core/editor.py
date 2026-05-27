# Methods for editing: image processing engine

from PIL import Image, ImageEnhance
from pathlib import Path


# ---------- SINGLE IMAGE OPERATIONS ----------

def apply_brightness_to_image(image: Image.Image, value: float):
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(value)


def apply_contrast_to_image(image: Image.Image, value: float):
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(value)


def apply_sharpness_to_image(image: Image.Image, value: float):
    enhancer = ImageEnhance.Sharpness(image)
    return enhancer.enhance(value)


def apply_gamma_to_image(image: Image.Image, gamma: float):
    inv_gamma = 1.0 / gamma

    table = [
        int(((i / 255.0) ** inv_gamma) * 255)
        for i in range(256)
    ]

    return image.point(table * 3)

# ~~~~~~~~~~~~~ BATCH FUNCTIONS (File-based) ~~~~~~~~~~~~~~~~~~~~~~~


def _load_image(path: Path):
    return Image.open(path).convert("RGB")


def _save_image(image: Image.Image, out_dir: Path, prefix: str, original_name: str):
    out_dir.mkdir(parents=True, exist_ok=True)

    new_name = f"{prefix}_{original_name}"
    out_path = out_dir / new_name

    image.save(out_path, quality=95)

    return out_path

# ~~~~~~~~~~~~~ BRIGHTNESS BATCH  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def apply_brightness(files: list[Path], value: float, output_dir: Path):
    results = []

    for file in files:
        if not file.exists():
            continue

        img = _load_image(file)
        edited = apply_brightness_to_image(img, value)

        out = _save_image(
            edited,
            output_dir,
            "brightness",
            file.name
        )

        results.append(out)

    return results


# ~~~~~~~~~~~~~ CONTRAST BATCH  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def apply_contrast(files: list[Path], value: float, output_dir: Path):
    results = []

    for file in files:
        if not file.exists():
            continue

        img = _load_image(file)
        edited = apply_contrast_to_image(img, value)

        out = _save_image(
            edited,
            output_dir,
            "contrast",
            file.name
        )

        results.append(out)

    return results


# ~~~~~~~~~~~~~ SHARPNESS BATCH  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def apply_sharpness(files: list[Path], value: float, output_dir: Path):
    results = []

    for file in files:
        if not file.exists():
            continue

        img = _load_image(file)
        edited = apply_sharpness_to_image(img, value)

        out = _save_image(
            edited,
            output_dir,
            "sharpness",
            file.name
        )

        results.append(out)

    return results


# ~~~~~~~~~~~~~ GAMMA BATCH  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def apply_gamma(files: list[Path], gamma: float, output_dir: Path):
    results = []

    for file in files:
        if not file.exists():
            continue

        img = _load_image(file)
        edited = apply_gamma_to_image(img, gamma)

        out = _save_image(
            edited,
            output_dir,
            "gamma",
            file.name
        )

        results.append(out)

    return results

# USAGE EXAMPLE: 

# Btirhgtness slider: 
'''
apply_brightness(
    files=selected_files,
    value=1.2,
    output_dir=PHOTO_DIR
)
'''

# Gamma slider: 
'''
apply_gamma(
    files=selected_files,
    gamma=0.85,
    output_dir=PHOTO_DIR
)

'''