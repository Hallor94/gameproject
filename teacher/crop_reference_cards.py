
import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance

# === CONFIG ===
INPUT_DIR = "reference_cards"
OUTPUT_DIR = "processed_cards"
PADDING = 10

# === CROPPING PROFILES ===
DEFAULT_CONFIG = {
    "MIN_AREA": 400000,
    "MAX_ASPECT_RATIO": 5
}

DICE_CONFIG = {
    "MIN_AREA": 5000,
    "MAX_ASPECT_RATIO": 5
}

def crop_card_by_contour(image, contour, padding):
    x, y, w, h = cv2.boundingRect(contour)
    x = max(x - padding, 0)
    y = max(y - padding, 0)
    w = min(w + 2 * padding, image.shape[1] - x)
    h = min(h + 2 * padding, image.shape[0] - y)
    cropped = image[y:y + h, x:x + w]
    return Image.fromarray(cropped), (x, y, x + w, y + h)

def crop_dice_by_contour(image, contour, padding):
    x, y, w, h = cv2.boundingRect(contour)
    size = max(w, h)
    cx = x + w // 2
    cy = y + h // 2
    half = size // 2 + padding
    x1 = max(cx - half, 0)
    y1 = max(cy - half, 0)
    x2 = min(cx + half, image.shape[1])
    y2 = min(cy + half, image.shape[0])
    cropped = image[y1:y2, x1:x2]
    return Image.fromarray(cropped), (x1, y1, x2, y2)

def straighten_card(pil_image: Image.Image) -> Image.Image:
    image = np.array(pil_image)
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 150, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        print("❌ No contours found for deskewing.")
        return None

    contour = max(contours, key=cv2.contourArea)
    rect = cv2.minAreaRect(contour)
    angle = rect[-1]

    if angle < -45:
        angle += 90

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return Image.fromarray(rotated)

def crop_card_from_image(pil_image, padding=PADDING, config=DEFAULT_CONFIG):
    image = np.array(pil_image)
    image_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    image_blur = cv2.GaussianBlur(image_gray, (5, 5), 0)
    _, thresh = cv2.threshold(image_blur, 150, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print("❌ No contours found.")
        return None, None

    contour = max(contours, key=cv2.contourArea)
    contour_area = cv2.contourArea(contour)
    x, y, w, h = cv2.boundingRect(contour)
    aspect_ratio = max(w / h, h / w)

    if contour_area < config["MIN_AREA"] or aspect_ratio > config["MAX_ASPECT_RATIO"]:
        print(f"❌ Failed: area={int(contour_area)}px, ratio={aspect_ratio:.2f}")
        return None, None

    if config == DICE_CONFIG:
        return crop_dice_by_contour(image, contour, padding)
    else:
        return crop_card_by_contour(image, contour, padding)

def process_card_image(pil_image, source_path=""):
    config = DICE_CONFIG if "/dice/" in source_path.replace("\\", "/").lower() else DEFAULT_CONFIG
    upright = straighten_card(pil_image)
    if upright is None:
        return None
    cropped, _ = crop_card_from_image(upright, config=config)
    return cropped

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
