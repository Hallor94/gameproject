import numpy as np
import cv2
from PIL import Image

def extract_card_candidates(pil_image, min_card_area=5000, min_dice_area=200):
    image = np.array(pil_image)
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 150, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    results = []
    card_boxes = []

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_dice_area:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / h
        is_rect_like = 0.6 < aspect_ratio < 1.8
        x1, y1 = max(x - 10, 0), max(y - 10, 0)
        x2, y2 = min(x + w + 10, image.shape[1]), min(y + h + 10, image.shape[0])
        cropped = image[y1:y2, x1:x2]
        cropped_pil = Image.fromarray(cropped)

        if area >= min_card_area and is_rect_like:
            obj_type = 'card'
            card_boxes.append((x1, y1, x2, y2))
        elif min_dice_area < area < min_card_area:
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue
            circularity = 4 * np.pi * (area / (perimeter ** 2))
            if circularity < 0.6:
                continue
            obj_type = 'dice'
            dice_center = (x + w // 2, y + h // 2)
            inside_card = any(cb[0] <= dice_center[0] <= cb[2] and cb[1] <= dice_center[1] <= cb[3] for cb in card_boxes)
            if inside_card:
                continue
        else:
            continue

        results.append({
            'bbox': (x1, y1, x2, y2),
            'cropped': cropped_pil,
            'type': obj_type
        })

    # Filter nested cards
    filtered_results = []
    for i, result in enumerate(results):
        if result['type'] != 'card':
            filtered_results.append(result)
            continue
        x1, y1, x2, y2 = result['bbox']
        area = (x2 - x1) * (y2 - y1)
        is_nested = False
        for j, other in enumerate(results):
            if i == j or other['type'] != 'card':
                continue
            ox1, oy1, ox2, oy2 = other['bbox']
            inter_x1 = max(x1, ox1)
            inter_y1 = max(y1, oy1)
            inter_x2 = min(x2, ox2)
            inter_y2 = min(y2, oy2)
            inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)
            if inter_area / area > 0.85:
                is_nested = True
                break
        if not is_nested:
            filtered_results.append(result)

    return filtered_results
