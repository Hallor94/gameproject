import time

class MemoryManager:
    def __init__(self):
        self.locked_objects = []  # List of dicts with object data
        self.next_id = 1

    def clear(self):
        self.locked_objects = []
        self.next_id = 1

    def register_objects(self, new_objects):
        for obj in new_objects:
            x1, y1, x2, y2 = obj["bbox"]
            self.locked_objects.append({
                "id": self.next_id,
                "bbox": obj["bbox"],
                "type": obj["type"],
                "label": obj["best_label"],
                "timestamp": time.time(),
                "center": ((x1 + x2) // 2, (y1 + y2) // 2),
                "corners": [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
            })
            self.next_id += 1

    def get_locked_objects(self):
        return self.locked_objects

    def get_locked_cards(self):
        return [obj for obj in self.locked_objects if obj["type"] == "card"]

    def find_overlapping_object(self, bbox, iou_threshold=0.5, type_filter=None):
        for obj in self.locked_objects:
            if type_filter and obj["type"] != type_filter:
                continue
            if self.compute_iou(bbox, obj["bbox"]) > iou_threshold:
                return obj
        return None

    def compute_iou(self, boxA, boxB):
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])

        interArea = max(0, xB - xA) * max(0, yB - yA)
        if interArea == 0:
            return 0.0

        boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
        return interArea / float(boxAArea + boxBArea - interArea)
