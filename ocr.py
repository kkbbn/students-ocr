import re
import sys
import cv2
import numpy as np
from enum import Enum
from math import isnan
from pponnxcr import TextSystem

class OCR_LANG(Enum):
    EN = 1
    JA = 4

OCR_SYSTEMS = {
    OCR_LANG.EN: TextSystem('en'),
    OCR_LANG.JA: TextSystem('ja'),
}

def filter_white_text(image):
    """Keep only white (low-saturation, high-value) pixels to remove ghost images from semi-transparent backgrounds."""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = (hsv[:, :, 1] < 50) & (hsv[:, :, 2] > 160)
    result = np.zeros_like(image)
    result[mask] = [255, 255, 255]
    return result

def ocr_area(image_mat, fromxy, toxy, ocr_lang=OCR_LANG.EN, white_text=False):
    fromx, fromy = fromxy
    tox, toy = toxy
    cropped = image_mat[fromy:toy, fromx:tox]
    if white_text:
        cropped = filter_white_text(cropped)
    result = OCR_SYSTEMS[ocr_lang].ocr_single_line(cropped)
    text = result[0].strip().replace("９", "9")
    score = result[1] if not isnan(result[1]) else 0
    return text, score

SKILL_NAMES = ["EX", "Normal", "Passive", "Sub"]

def parse_skill_lv(text):
    text = text.strip()
    if text == "MAX":
        return "MAX"
    return int(text.replace("Lv.", ""))

def process_image(image):
    name, name_score = ocr_area(image, [70, 560], [265, 590], OCR_LANG.JA, white_text=True)
    lv_text, lv_score = ocr_area(image, [5, 590], [80, 620])
    lv = int(lv_text.replace("Lv.", ""))
    bond_text, _ = ocr_area(image, [45, 560], [75, 580])
    bond = int(re.sub(r'\D', '', bond_text))

    wb_coords = [
        [774, 231, 819, 254],   # HP
        [996, 233, 1038, 251],  # ATK
        [1000, 271, 1045, 291], # Heal
    ]
    wb_lvs = []
    for x1, y1, x2, y2 in wb_coords:
        text, _ = ocr_area(image, [x1, y1], [x2, y2])
        m = re.search(r'[Ll][Vv]\.?(\d+)', text)
        wb_lvs.append(int(m.group(1)) if m else None)

    skill_lvs = []
    for i in range(4):
        x_start = 700 + i * 100
        skill_text, _ = ocr_area(image, [x_start, 400], [x_start + 80, 425])
        skill_lvs.append(parse_skill_lv(skill_text))

    equip_tiers = []
    for i in range(4):
        x_start = 690 + i * 90
        equip_text, _ = ocr_area(image, [x_start, 616], [x_start + 30, 632])
        m = re.search(r'T(\d+)', equip_text)
        equip_tiers.append(int(m.group(1)) if m else None)

    skills_str = "/".join(str(s) for s in skill_lvs)
    equip_str = "/".join(f"T{t}" if t is not None else "None" for t in equip_tiers)
    wb_str = "/".join(str(w) if w is not None else "None" for w in wb_lvs)
    print(f"{name} Lv.{lv} Bond:{bond} Skills:{skills_str} Equip:{equip_str} WB:{wb_str}")

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <image1> [image2 ...]", file=sys.stderr)
        sys.exit(1)

    for filepath in sorted(sys.argv[1:]):
        image = cv2.imread(filepath)
        if image is None:
            print(f"Error: Could not read {filepath}", file=sys.stderr)
            continue
        result = process_image(image)

if __name__ == "__main__":
    main()
