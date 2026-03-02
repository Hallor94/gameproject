import os
import time
import tkinter as tk
from tkinter import messagebox, END
from PIL import ImageTk
import numpy as np
import threading
from utils.camera import capture_image, capture_preview
from core.recognition_pipeline import recognize_cards, get_locked_objects, clear_memory
from utils.image_utils import scale_to_fit
from config.constants import (
    AUTO_INTERVAL,
    LOCAL_CHANGE_REGION,
    LOCAL_CHANGE_PIXEL_THRESHOLD,
    LOCAL_CHANGE_COUNT_THRESHOLD
)

# === GUI Setup ===
root = tk.Tk()
root.title("TorchScript Card Recognizer")
try:
    root.state("zoomed")
except:
    root.attributes("-zoomed", True)

monitoring = False
last_preview = None
captured_image = None
tk_image = None
debug_mode = False

image_frame = tk.Frame(root)
image_frame.pack(pady=10)
original_label = tk.Label(image_frame)
original_label.pack()

status_label = tk.Label(root, text="Status: Waiting to capture")
status_label.pack(pady=5)
result_frame = tk.Frame(root)
result_frame.pack(pady=10)

def update_status():
    modes = []
    if debug_mode:
        modes.append(" Debug ON")
    if monitoring:
        modes.append("🎯 Auto Mode ON (publishing)")
    status_label.config(text=" | ".join(modes) if modes else "Status: Idle")

def toggle_debug_mode():
    global debug_mode
    debug_mode = not debug_mode
    update_status()

def significant_local_change(prev, curr, region_size=LOCAL_CHANGE_REGION, pixel_thresh=LOCAL_CHANGE_PIXEL_THRESHOLD, count_thresh=LOCAL_CHANGE_COUNT_THRESHOLD):
    diff = np.abs(curr.astype(int) - prev.astype(int))
    h, w = diff.shape
    for y in range(0, h, region_size):
        for x in range(0, w, region_size):
            region = diff[y:y+region_size, x:x+region_size]
            changed = np.sum(region > pixel_thresh)
            if changed > count_thresh:
                return True
    return False

def start_monitoring():
    global monitoring
    if monitoring:
        return
    monitoring = True
    threading.Thread(target=monitor_loop, daemon=True).start()
    update_status()

def stop_monitoring():
    global monitoring
    monitoring = False
    update_status()

def auto_capture_and_recognize():
    global captured_image, tk_image
    try:
        img = capture_image()
        captured_image = img
        scaled = scale_to_fit(img, 640, 360)
        tk_image = ImageTk.PhotoImage(scaled)
        original_label.config(image=tk_image)
        original_label.image = tk_image
        run_recognition(publish=True)
    except Exception as e:
        print(f"[ERROR] Auto capture failed: {e}")

def monitor_loop():
    global last_preview
    while monitoring:
        preview = capture_preview()
        if preview is None:
            time.sleep(1.0)
            continue
        if last_preview is not None and significant_local_change(last_preview, preview):
            print("🎲 Local change detected — capturing!")
            root.after(0, auto_capture_and_recognize)
            last_preview = None
            time.sleep(3)
            continue
        last_preview = preview
        time.sleep(AUTO_INTERVAL)

def run_recognition(publish=False):
    global captured_image, tk_image
    if captured_image is None:
        messagebox.showwarning("No Image", "Please capture an image first.")
        return
    results, debug_img = recognize_cards(captured_image, debug=debug_mode)
    scaled_debug = scale_to_fit(debug_img, 800, 600)
    tk_debug = ImageTk.PhotoImage(scaled_debug)
    original_label.config(image=tk_debug)
    original_label.image = tk_debug

    for widget in result_frame.winfo_children():
        widget.destroy()
    for result in results:
        frame = tk.Frame(result_frame)
        frame.pack(side="left", padx=10)
        tk.Label(frame, text=f"Object {result['object_id']} ({result['type']})").pack()
        lst = tk.Listbox(frame, width=40)
        lst.pack()
        if result["is_confident"]:
            lst.insert(END, f"✅ {result['best_label']} ({result['vote_count']}/12)")
        else:
            lst.insert(END, "❓ No confident match")
            lst.insert(END, f"Top guess: {result['best_label']}")
        for label, dist in result["matches"][:10]:
            lst.insert(END, f"{label}: {dist:.4f}")

    status_label.config(text=f"✅ {len(results)} object(s) detected." if results else "🚼 Board cleared.")

    if publish:
        try:
            from broadcaster.mqtt_broadcaster import publish_recognition
            publish_recognition(get_locked_objects())
        except Exception as e:
            print(f"[MQTT ERROR] Could not publish results: {e}")

button_frame = tk.Frame(root)
button_frame.place(x=10, y=10)

buttons = [
    ("Capture Image", lambda: auto_capture_and_recognize()),
    ("Run Recognition", lambda: run_recognition(publish=True)),
    ("Start Auto Mode", start_monitoring),
    ("Stop Auto Mode", stop_monitoring),
    ("Toggle Debug Mode", toggle_debug_mode),
    ("Reset Memory", lambda: (clear_memory(), messagebox.showinfo("Memory Reset", "Recognition memory has been cleared."))),
    ("Exit", root.destroy)
]

for label, cmd in buttons:
    tk.Button(button_frame, text=label, command=cmd).pack(anchor="w", pady=2)

root.mainloop()
