# trainer.py
import os
import shutil
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
import random
import traceback
import re

from train_siamese import train_model
from generate_reference_embeddings import generate_reference_embeddings
from export_to_TS import export_encoder_to_torchscript
from crop_reference_cards import process_card_image


# Make sure crop_reference_cards.py writes to processed_cards instead of cropped_cards

# === CONFIG ===
REFERENCE_DIR = "reference_cards"
CROPPED_DIR = "processed_cards"
AUGMENTED_DIR = "augmented_cards"
OUTPUT_DIR = "output"
BACKGROUND_DIR = "backgrounds"

# Augmentation
AUGS_PER_IMAGE = 10

# Training hyperparameters
TARGET_LOSS = 0.05
EPOCHS = 20
BATCH_SIZE = 16
LR = 1e-4
MARGIN = 1.0
PATIENCE = 3
THRESHOLD = 0.001


def pad_with_border(img, padding=32):
    w, h = img.size
    # Use an alpha channel for masking
    new_img = Image.new("RGBA", (w + 2*padding, h + 2*padding), (0, 0, 0, 0))
    img = img.convert("RGBA")
    new_img.paste(img, (padding, padding))
    return new_img

def paste_on_random_background(fg_img):
    if not os.path.exists(BACKGROUND_DIR):
        return fg_img.convert("RGB")

    bg_files = [f for f in os.listdir(BACKGROUND_DIR) if f.lower().endswith((".jpg", ".png"))]
    if not bg_files:
        return fg_img.convert("RGB")

    bg_path = os.path.join(BACKGROUND_DIR, random.choice(bg_files))
    bg = Image.open(bg_path).convert("RGB").resize(fg_img.size[:2])

    if fg_img.mode != "RGBA":
        fg_img = fg_img.convert("RGBA")

    composite = Image.new("RGB", fg_img.size)
    composite.paste(bg, (0, 0))
    composite.paste(fg_img, (0, 0), mask=fg_img.split()[3])  # use alpha channel
    return composite

# === Augmentation function ===
def augment_card(img):
    # Random rotation in 0, 90, 180, 270 degrees (applied to most augmentations)

    img = pad_with_border(img)
    if random.random() < 0.9:
        angle = random.choice([0, 90, 180, 270])
        img = img.rotate(angle, expand=True)

    # Safe transforms
    img = ImageEnhance.Contrast(img).enhance(random.uniform(0.8, 1.2))
    img = ImageEnhance.Brightness(img).enhance(random.uniform(0.8, 1.2))

    # Occasionally apply stronger augmentations
    if random.random() < 0.5:
        img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 1.5)))

    if random.random() < 0.3:
        # Add synthetic Gaussian noise
        import numpy as np
        arr = np.array(img).astype(np.float32)
        noise = np.random.normal(0, 10, arr.shape)
        noisy = np.clip(arr + noise, 0, 255).astype(np.uint8)
        img = Image.fromarray(noisy)

    if random.random() < 0.5:
        img = center_blur(img)

    if random.random() < 0.3:
        # Apply affine warp (perspective simulation)
        from torchvision.transforms import functional as TF
        angle = random.uniform(-10, 10)
        translate = (random.uniform(-0.05, 0.05) * img.size[0], random.uniform(-0.05, 0.05) * img.size[1])
        scale = random.uniform(0.95, 1.05)
        shear = random.uniform(-5, 5)
        img = TF.affine(img, angle=angle, translate=translate, scale=scale, shear=shear)

    if random.random() < 0.7:
        img = paste_on_random_background(img)

    return img

def augment_dice(img):
    # For now, use the same augmentation pipeline as cards
    return augment_card(img)

# === Folder setup ===
def prepare_folders():
    print("\U0001F4C1 Preparing folders...")

    if not os.path.exists(REFERENCE_DIR):
        raise FileNotFoundError(f"❌ Folder not found: {REFERENCE_DIR}")

    for folder in [CROPPED_DIR, AUGMENTED_DIR, OUTPUT_DIR]:
        if os.path.exists(folder):
            print(f"🧹 Clearing existing folder: {folder}")
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)
        print(f"✅ Created: {folder}")


def crop_all_reference_images():
    print("✂️ Cropping reference images...")

    from collections import defaultdict
    label_stats = defaultdict(lambda: {"total": 0, "saved": 0})

    for root, _, files in os.walk(REFERENCE_DIR):
        for fname in files:
            if not fname.lower().endswith((".jpg", ".png", ".jpeg")):
                continue

            full_path = os.path.join(root, fname)
            rel_path = os.path.relpath(full_path, REFERENCE_DIR)
            label = re.sub(r"_[^_]+$", "", os.path.splitext(fname)[0])

            label_stats[label]["total"] += 1

            try:
                img = Image.open(full_path).convert("RGB")
                from crop_reference_cards import process_card_image  # make sure it's re-imported fresh
                processed = process_card_image(img, full_path)
                if processed is None:
                    print(f"❌ Skipped (could not process): {rel_path}")
                    continue

                save_path = os.path.join(CROPPED_DIR, rel_path)
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                processed.save(save_path)
                label_stats[label]["saved"] += 1
                print(f"✅ Cropped: {rel_path}")
            except Exception as e:
                print(f"❌ Failed cropping {rel_path}: {e}")

    print("\n📊 Cropping Summary:")
    for label, stats in label_stats.items():
        if stats["saved"] == 0:
            print(f"⚠️ All variants of {label} failed to crop ({stats['total']} skipped)")
        else:
            print(f"✅ {label}: {stats['saved']}/{stats['total']} saved")



def generate_augmented_images():
    print(f"\n🔁 Generating {AUGS_PER_IMAGE} augmentations per object...")

    total = 0
    for root, _, files in os.walk(CROPPED_DIR):
        for fname in files:
            if not fname.lower().endswith((".jpg", ".png")):
                continue

            full_path = os.path.join(root, fname)
            rel_path = os.path.relpath(full_path, CROPPED_DIR)
            base = os.path.splitext(fname)[0]
            label = re.sub(r"_[^_]+$", "", base)
            variant = base.replace(label, "").strip("_")

            img = Image.open(full_path).convert("RGB")

            # Folder-specific logic
            if "dice" in rel_path.lower():
                aug_func = augment_dice
            else:
                aug_func = augment_card

            for i in range(AUGS_PER_IMAGE):
                outname = f"{label}_{variant}_aug{i}.png"
                outpath = os.path.join(AUGMENTED_DIR, os.path.dirname(rel_path), outname)
                os.makedirs(os.path.dirname(outpath), exist_ok=True)
                aug_img = aug_func(img)
                aug_img.save(outpath)

            total += 1
            print(f"✅ Augmented: {rel_path}")

    print(f"\n📊 Done: {total} objects × {AUGS_PER_IMAGE} = {total * AUGS_PER_IMAGE} images.")


def center_blur(img):
    """Apply blur to the edges, keeping the center sharp to emphasize features."""
    blurred = img.filter(ImageFilter.GaussianBlur(radius=3))
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    w, h = img.size
    draw.ellipse((w * 0.1, h * 0.1, w * 0.9, h * 0.9), fill=255)
    return Image.composite(img, blurred, mask)




# === Master training sequence ===
def main():
    print("🔧 Starting full training pipeline...\n")

    try:
        prepare_folders()

        print("\n✂️ Step 0: Cropping reference images...")
        crop_all_reference_images()

        print("\n📸 Step 1: Augmenting reference images...")
        generate_augmented_images()

        print("\n🏋️‍♂️ Step 2: Training Siamese model...")
        train_model(
            output_dir=OUTPUT_DIR,
            use_early_stopping=True,
            full_pair_generation=True,
            epochs=EPOCHS,
            batch_size=BATCH_SIZE,
            lr=LR,
            margin=MARGIN,
            patience=PATIENCE,
            threshold=THRESHOLD,
            target_loss=TARGET_LOSS
        )

        print("\n🧠 Step 3: Generating reference embeddings...")
        generate_reference_embeddings(OUTPUT_DIR)

        print("\n📦 Step 4: Exporting TorchScript encoder...")
        export_encoder_to_torchscript(OUTPUT_DIR)

        print("\n✅ All steps completed successfully.")
        print(f"📂 Outputs available in: {OUTPUT_DIR}/")

    except Exception as e:
        print("❌ An error occurred:")
        traceback.print_exc()

if __name__ == "__main__":
    main()
