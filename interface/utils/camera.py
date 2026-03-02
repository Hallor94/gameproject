import subprocess
import tempfile
import time
from PIL import Image
import numpy as np
import os

def capture_image(width=2304, height=1296, timeout=1000, retries=3):
    for attempt in range(retries):
        try:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmpfile:
                temp_path = tmpfile.name
            result = subprocess.run([
                "libcamera-still", "-o", temp_path,
                "--width", str(width), "--height", str(height),
                "--nopreview", "--awb", "auto", "--exposure", "normal",
                "-t", str(timeout)
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode != 0 or not os.path.exists(temp_path):
                raise RuntimeError("Image capture failed")
            img = Image.open(temp_path).convert("RGB")
            os.remove(temp_path)
            return img
        except Exception as e:
            print(f"[WARN] Image capture attempt {attempt+1} failed: {e}")
            time.sleep(0.3)
    raise RuntimeError("Failed to capture image after retries")

def capture_preview(width=320, height=240, timeout=100, retries=3):
    for attempt in range(retries):
        try:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmpfile:
                temp_path = tmpfile.name
            result = subprocess.run([
                "libcamera-still", "-o", temp_path,
                "--width", str(width), "--height", str(height),
                "--nopreview", "--awb", "auto", "--exposure", "normal",
                "--timeout", str(timeout)
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode != 0:
                raise RuntimeError("Preview capture failed")
            img = Image.open(temp_path).convert("L")
            os.remove(temp_path)
            return np.array(img)
        except Exception as e:
            print(f"[WARN] Preview attempt {attempt+1} failed: {e}")
            time.sleep(0.2)
    return None
