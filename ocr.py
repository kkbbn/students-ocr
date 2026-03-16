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

def process_image(image):
    name, name_score = ocr_area(image, [70, 560], [265, 590], OCR_LANG.JA)
    lv_text, lv_score = ocr_area(image, [5, 590], [80, 620])
    lv = int(lv_text.replace("Lv.", ""))
    print(f"{name} Lv.{lv} (confidence: {name_score:.4f}, {lv_score:.4f})")

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
