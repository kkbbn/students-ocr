import sys
import cv2
from enum import Enum
from math import isnan
from pponnxcr import TextSystem

OCR_SYS_JA = TextSystem('ja')

class OCR_LANG(Enum):
    EN = 1
    JA = 4

def ocr_area(image_mat, fromxy, toxy):
    fromx, fromy = fromxy
    tox, toy = toxy
    ocr_sys = OCR_SYS_JA
    cropped = image_mat[fromy:toy, fromx:tox]
    result = ocr_sys.ocr_single_line(cropped)
    text = result[0].strip().replace("９", "9")
    score = result[1] if not isnan(result[1]) else 0
    return text, score

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <image1> [image2 ...]", file=sys.stderr)
        sys.exit(1)

    for filepath in sys.argv[1:]:
        image = cv2.imread(filepath)
        if image is None:
            print(f"Error: Could not read {filepath}", file=sys.stderr)
            continue
        text, score = ocr_area(image, [70, 560], [265, 590])
        print(f"{text} (confidence: {score:.4f})")

if __name__ == "__main__":
    main()
