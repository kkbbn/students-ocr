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

OCR_CORRECTIONS = str.maketrans(
    '八毛三工力口し（）*',
    'ハモミエカロレ()＊',
)

# Small kana at the start of a name are OCR errors (e.g. ョシミ→ヨシミ)
SMALL_TO_LARGE_KANA = str.maketrans('ァィゥェォヵヶッャュョヮ', 'アイウエオカケツヤユヨワ')

NAME_FIXES = {
    'チェリン': 'チェリノ',
}

SKILL_NAMES = ["EX", "Normal", "Passive", "Sub"]

def filter_white_text(image):
    """Black out ghost images from semi-transparent backgrounds, keeping original text pixels intact."""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    white_mask = (hsv[:, :, 1] < 50) & (hsv[:, :, 2] > 160)
    cols_with_text = np.any(white_mask, axis=0)
    result = image.copy()
    if cols_with_text.any():
        last_col = np.max(np.where(cols_with_text))
        result[:, last_col + 5:] = 0
    return result

def ocr_area(image_mat, fromxy, toxy, ocr_lang=OCR_LANG.EN, white_text=False):
    fromx, fromy = fromxy
    tox, toy = toxy
    cropped = image_mat[fromy:toy, fromx:tox]
    if white_text:
        cropped = filter_white_text(cropped)
    result = OCR_SYSTEMS[ocr_lang].ocr_single_line(cropped)
    text = result[0].strip()
    score = result[1] if not isnan(result[1]) else 0
    return text, score

def parse_skill_lv(text):
    text = text.strip()
    if text == "MAX":
        return "MAX"
    return int(text.replace("Lv.", ""))

def is_yellow_star(pixel):
    b, g, r = pixel
    return int(r) > 180 and int(g) > 150 and int(b) < 120

def is_blue_star(pixel):
    b, g, r = pixel
    return int(b) > 200 and int(g) > 200 and int(r) < 180

def count_stars(image):
    yellow_star_xs = [271, 284, 297, 310, 324]
    blue_star_xs = [1012, 1028, 1044, 1061, 1077]
    yellow = sum(1 for x in yellow_star_xs if is_yellow_star(image[575, x]))
    blue = sum(1 for x in blue_star_xs if is_blue_star(image[512, x]))
    return yellow, blue

def process_image(image):
    name, _ = ocr_area(image, [70, 560], [265, 590], OCR_LANG.JA, white_text=True)
    name = name.translate(OCR_CORRECTIONS).replace(" ", "").replace("((", "(").replace("))", ")")
    if name:
        fixed_first = name[0].translate(SMALL_TO_LARGE_KANA)
        if fixed_first != name[0]:
            name = fixed_first + name[1:]
    # Extract base name (before parenthesized suffix) for name-specific fixes
    base = name.split('(')[0]
    if base in NAME_FIXES:
        name = NAME_FIXES[base] + name[len(base):]
    lv_text, _ = ocr_area(image, [5, 590], [80, 620])
    lv = int(re.sub(r'\D', '', lv_text))
    bond_text, _ = ocr_area(image, [45, 560], [75, 580])
    bond = int(re.sub(r'\D', '', bond_text))
    yellow_stars, blue_stars = count_stars(image)

    ue_text, _ = ocr_area(image, [778, 451], [838, 474])
    m = re.search(r'[Ll][Vv]\.?(\d+)', ue_text)
    ue_lv = int(m.group(1)) if m else None

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

    max_skill_lvs = [5, 10, 10, 10]
    skill_lvs = []
    for i in range(4):
        x_start = 700 + i * 100
        skill_text, _ = ocr_area(image, [x_start, 400], [x_start + 80, 425])
        skill_lv = parse_skill_lv(skill_text)
        skill_lvs.append(max_skill_lvs[i] if skill_lv == "MAX" else skill_lv)

    equip_tiers = []
    for i in range(4):
        x_start = 690 + i * 90
        equip_text, _ = ocr_area(image, [x_start, 616], [x_start + 30, 632])
        m = re.search(r'T(\d+)', equip_text)
        equip_tiers.append(int(m.group(1)) if m else None)

    return {
        'name': name,
        'lv': lv,
        'bond': bond,
        'stars': '★' * yellow_stars + '☆' * blue_stars,
        'skills': skill_lvs,
        'equip': equip_tiers,
        'ue_lv': ue_lv,
        'wb': wb_lvs,
    }

def fmt(value):
    return "" if value is None else str(value)

def print_result(result):
    r = result
    fields = [r['name'], r['stars'], r['ue_lv'], r['lv']] + r['skills'] + r['equip'] + [r['bond']] + r['wb']
    print(",".join(fmt(f) for f in fields))

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
        print_result(result)

if __name__ == "__main__":
    main()
