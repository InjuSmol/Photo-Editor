
from PIL import Image
import config
from pathlib import Path
from core.ori_det import get_object_orientations, dominant_orientation

def apply_logo_to_image(
    photo_path: Path,
    logo_path: Path,
    output_dir: Path,
    position: str = "right",
    scale_ratio: float = 0.10,
    padding: int = 10, 
    auto_rotate_logo=False
):
    if not photo_path.exists():
        raise FileNotFoundError(photo_path)

    if not logo_path.exists():
        raise FileNotFoundError(logo_path)

    valid_positions = {
        "top-left", "top-right",
        "bottom-left", "bottom-right"
    }

    if position not in valid_positions:
        raise ValueError("Invalid logo position")

    # -------------------------------
    # Detect people orientation
    # -------------------------------
    orientations = get_object_orientations(photo_path)
    dom_orient = dominant_orientation(orientations)
    # If auto rotate is chosen and if the rotate is needed: 
    rotate_logo = auto_rotate_logo and dom_orient == "horizontal" 

    # -------------------------------
    # Load images
    # -------------------------------
    img = Image.open(photo_path).convert("RGBA")
    logo_original = Image.open(logo_path).convert("RGBA")

    if rotate_logo:
        logo_original = logo_original.rotate(90, expand=True)

    img_w, img_h = img.size

    # Resize logo relative to photo width
    target_logo_width = int(img_w * scale_ratio)
    ratio = target_logo_width / logo_original.width
    new_height = int(logo_original.height * ratio)

    logo = logo_original.resize(
        (target_logo_width, new_height),
        Image.LANCZOS
    )

    # -------------------------------
    # Position calculation
    # -------------------------------
    if "right" in position:
        x = img_w - logo.size[0] - padding
    else:
        x = padding

    if "bottom" in position:
        y = img_h - logo.size[1] - padding
    else:
        y = padding

    # Paste logo
    img.paste(logo, (x, y), logo)

    # -------------------------------
    # Output
    # -------------------------------
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"logo_{photo_path.name}"

    img.convert("RGB").save(out_path, quality=95)

    return out_path

def apply_logo_batch(
    photos: list[Path],
    logo_path: Path,
    output_dir: Path,
    position="right", 
    auto_rotate_logo=False
):
    """
    Applies logo to many photos, using settings from config.
    Returns list of output paths.
    """
    results = []

    for photo in photos:
        try:
            # Load image to compute padding in pixels
            img = Image.open(photo)
            padding_px = int(img.size[0] * config.LOGO_MARGIN_PERCENT / 100)
            scale_ratio = config.LOGO_SIZE_PERCENT / 100

            out = apply_logo_to_image(
                photo_path=photo,
                logo_path=logo_path,
                output_dir=output_dir,
                position=position,
                scale_ratio=scale_ratio,
                padding=padding_px,
                auto_rotate_logo=auto_rotate_logo
            )
            results.append(out)

        except Exception as e:
            print(f"[LOGO ERROR] {photo.name}: {e}")

    return results

