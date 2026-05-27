import numpy as np
import argparse

import torch
from torchvision.transforms import functional as F
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from pathlib import Path

from PIL import Image
"""
model = fasterrcnn_resnet50_fpn(pretrained=True)
model.eval()

PERSON_CLASS_ID = 1  # COCO "person"

def detect_people_orientations(image_path: Path) -> list[str]:
    img = Image.open(image_path).convert("RGB")
    w, h = img.size

    tensor = F.to_tensor(img).unsqueeze(0)

    with torch.no_grad():
        output = model(tensor)[0]

    orientations = []

    for box, label, score in zip(
        output["boxes"],
        output["labels"],
        output["scores"]
    ):
        if label != PERSON_CLASS_ID:
            continue

        if score < 0.85:
            continue

        x1, y1, x2, y2 = box.tolist()
        bw = x2 - x1
        bh = y2 - y1

        # Ignore tiny detections
        if bw * bh < 0.01 * w * h:
            continue

        orientation = "vertical" if bh >= bw else "horizontal"
        orientations.append(orientation)

    return orientations
"""
model = fasterrcnn_resnet50_fpn(pretrained=True)
model.eval()

PERSON_CLASS_ID = 1

def get_object_orientations(image_path):
    """
    Returns list of orientations per detected object: ['vertical', 'horizontal', ...]
    """
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    tensor = F.to_tensor(img).unsqueeze(0)

    with torch.no_grad():
        output = model(tensor)[0]

    orientations = []

    for box, label, score in zip(output["boxes"], output["labels"], output["scores"]):
        if label != PERSON_CLASS_ID:
            continue
        if score < 0.8:  # filter weak detections
            continue
        x1, y1, x2, y2 = box.tolist()
        bw = x2 - x1
        bh = y2 - y1

        if bw * bh < 0.01 * w * h:
            continue

        orientation = "vertical" if bh >= bw else "horizontal"
        orientations.append(orientation)

    return orientations

def dominant_orientation(orientations):
    """
    Majority vote for overall orientation
    """
    if not orientations:
        return "vertical"  # fallback
    return max(set(orientations), key=orientations.count)

def main():
    parser = argparse.ArgumentParser(
        description="Detect orientation of people in an image"
    )

    parser.add_argument(
        "image",
        type=Path,
        help="Path to the image file"
    )

    args = parser.parse_args()

    orientations = get_object_orientations(args.image)

    print(orientations)

# ================= ENTRY =================

if __name__ == "__main__":
    main()