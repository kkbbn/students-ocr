import re
import sys
import cv2
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

def ocr_area(image_mat, fromxy, toxy, ocr_lang=OCR_LANG.EN):
    fromx, fromy = fromxy
    tox, toy = toxy
    cropped = image_mat[fromy:toy, fromx:tox]
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
    name, name_score = ocr_area(image, [70, 560], [265, 590], OCR_LANG.JA)
    lv_text, lv_score = ocr_area(image, [5, 590], [80, 620])
    lv = int(lv_text.replace("Lv.", ""))

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
    print(f"{name} Lv.{lv} Skills:{skills_str} Equip:{equip_str}")

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <image1> [image2 ...]", file=sys.stderr)
        sys.exit(1)

    for filepath in sys.argv[1:]:
        image = cv2.imread(filepath)
        if image is None:
            print(f"Error: Could not read {filepath}", file=sys.stderr)
            continue
        result = process_image(image)

if __name__ == "__main__":
    main()
