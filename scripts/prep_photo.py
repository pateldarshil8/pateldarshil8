"""
prep_photo.py
Run once per photo. Prepares a headshot for ASCII conversion:
1. Remove the background (rembg) so the subject is isolated.
2. Boost local contrast with OpenCV CLAHE (contrast-limited adaptive
   histogram equalization) -- gives a flat face real highlights/shadows.
3. Composite onto pure white so background maps to the blank end of the
   ASCII ramp (white -> spaces).
Output: source-prepped.png (grayscale), written next to the input photo.

Usage: python scripts/prep_photo.py source-photo.jpg
"""
import sys
import os

import numpy as np
import cv2
from PIL import Image
from rembg import remove


def main():
    if len(sys.argv) < 2:
        print("Usage: python prep_photo.py <photo.jpg>")
        sys.exit(1)

    in_path = sys.argv[1]
    out_path = os.path.join(os.path.dirname(in_path) or ".", "source-prepped.png")

    with open(in_path, "rb") as f:
        input_bytes = f.read()

    # 1. remove background -> RGBA
    result_bytes = remove(input_bytes)
    with open("_tmp_nobg.png", "wb") as f:
        f.write(result_bytes)

    rgba = Image.open("_tmp_nobg.png").convert("RGBA")
    os.remove("_tmp_nobg.png")

    # 2. composite onto white using alpha channel
    white_bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, rgba).convert("L")

    # 3. CLAHE contrast boost
    arr = np.array(composited)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    boosted = clahe.apply(arr)

    Image.fromarray(boosted).save(out_path)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
