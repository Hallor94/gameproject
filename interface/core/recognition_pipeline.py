import json
import numpy as np
import torch
from torchvision import transforms
from utils.detector import extract_card_candidates
from utils.image_utils import straighten_card, crop_card_from_image, draw_debug_boxes
from core.memory_manager import MemoryManager
from config.constants import MODEL_PATH, EMBEDDINGS_PATH, LABELS_PATH, ROTATION_ANGLES, CONFIDENCE_VOTE_THRESHOLD

# Load model and reference data
model = torch.jit.load(MODEL_PATH, map_location="cpu")
model.eval()
reference_vectors = np.load(EMBEDDINGS_PATH)
with open(LABELS_PATH, "r") as f:
    reference_labels = json.load(f)

memory = MemoryManager()

preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

def recognize_card(pil_image):
    aligned = straighten_card(pil_image)
    cropped, _ = crop_card_from_image(aligned)
    label_votes = {}
    all_matches = []

    for angle in ROTATION_ANGLES:
        rotated = cropped.rotate(angle, expand=True)
        image_tensor = preprocess(rotated).unsqueeze(0)
        with torch.no_grad():
            vec = model(image_tensor).cpu().numpy()[0]
        vec /= np.linalg.norm(vec)
        distances = [np.linalg.norm(vec - ref_vec) for ref_vec in reference_vectors]
        label_dist_pairs = list(zip(reference_labels, distances))
        label_dist_pairs.sort(key=lambda x: x[1])
        top_matches = label_dist_pairs[:3]
        for label, dist in top_matches:
            label_votes[label] = label_votes.get(label, 0) + 1
            all_matches.append((label, dist))

    sorted_votes = sorted(label_votes.items(), key=lambda x: (-x[1], min(d for l, d in all_matches if l == x[0])))
    best_label, vote_count = sorted_votes[0]
    is_confident = vote_count >= CONFIDENCE_VOTE_THRESHOLD

    return {
        "aligned_image": aligned,
        "cropped_image": cropped,
        "best_label": best_label,
        "vote_count": vote_count,
        "is_confident": is_confident,
        "matches": sorted(all_matches, key=lambda x: x[1])
    }

def recognize_cards(pil_image, debug=False):
    candidates = extract_card_candidates(pil_image)
    if not candidates:
        print("[Memory] No objects detected — clearing memory.")
        memory.clear()
        return [], pil_image

    results = []
    new_objects = []
    for idx, obj in enumerate(candidates):
        bbox = obj["bbox"]
        obj_type = obj.get("type", "unknown")

        if obj_type == "card":
            if memory.find_overlapping_object(bbox, iou_threshold=0.9, type_filter="card"):
                continue

        recog = recognize_card(obj["cropped"])
        recog.update({
            "object_id": idx + 1,
            "bbox": bbox,
            "type": obj_type
        })
        results.append(recog)
        new_objects.append(recog)

    if new_objects:
        memory.register_objects(new_objects)

    debug_image = pil_image.copy()
    if debug:
        debug_labels = [f"Object {r['object_id']} ({r['type']}): {r['best_label']}" for r in results]
        debug_types = [r["type"] for r in results]
        debug_image = draw_debug_boxes(debug_image, [r["bbox"] for r in results], debug_labels, debug_types)

    return results, debug_image

def get_locked_objects():
    return memory.get_locked_objects()

def clear_memory():
    memory.clear()
