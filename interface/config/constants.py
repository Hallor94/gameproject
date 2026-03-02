# config/constants.py

import os

# Model and data paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TORCHSCRIPT_MODEL = os.path.join(BASE_DIR, "siamese_encoder.pt")
EMBEDDINGS_FILE = os.path.join(BASE_DIR, "reference_embeddings.npy")
LABELS_FILE = os.path.join(BASE_DIR, "reference_labels.json")
MODEL_PATH = "camera_interface/model/siamese_encoder.pt"
EMBEDDINGS_PATH = "camera_interface/model/reference_embeddings.npy"
LABELS_PATH = "camera_interface/model/reference_labels.json"

# Recognition thresholds
THRESHOLD = 0.80

# Auto mode
DIFF_THRESHOLD = 10  # sensitivity of scene change
AUTO_INTERVAL = 2.0  # seconds between checks

ROTATION_ANGLES = [0, 90, 180, 270]
CONFIDENCE_VOTE_THRESHOLD = 3

# Sensitivity for local change detection
LOCAL_CHANGE_REGION = 10
LOCAL_CHANGE_PIXEL_THRESHOLD = 15
LOCAL_CHANGE_COUNT_THRESHOLD = 5