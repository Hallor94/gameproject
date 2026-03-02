import os
import json
import numpy as np
import torch
from PIL import Image
from torchvision import transforms, models
from torchvision.models import ResNet18_Weights
import re

def generate_reference_embeddings(output_dir="output"):
    REFERENCE_DIR = "processed_cards"
    ENCODER_PATH = os.path.join(output_dir, "siamese_encoder.pth")
    OUTPUT_EMBEDDINGS = os.path.join(output_dir, "reference_embeddings.npy")
    OUTPUT_LABELS = os.path.join(output_dir, "reference_labels.json")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ])

    # Load encoder
    model = models.resnet18(weights=ResNet18_Weights.DEFAULT)
    model.fc = torch.nn.Identity()
    model.load_state_dict(torch.load(ENCODER_PATH, map_location=device))
    model = model.to(device)
    model.eval()

    embeddings_dict = {}

    print("📂 Embedding reference cards:")
    for root, _, files in os.walk(REFERENCE_DIR):
        for fname in files:
            if not fname.lower().endswith((".jpg", ".png")):
                continue

            path = os.path.join(root, fname)
            rel_path = os.path.relpath(path, REFERENCE_DIR)
            label = re.sub(r"_[^_]+$", "", os.path.splitext(fname)[0])
            print(f"✅ Processed {rel_path} → label: {label}")

            img = Image.open(path).convert("RGB")
            tensor = transform(img).unsqueeze(0).to(device)

            with torch.no_grad():
                vec = model(tensor).cpu().numpy()[0]
                vec /= np.linalg.norm(vec)

            embeddings_dict.setdefault(label, []).append(vec)

    if not embeddings_dict:
        print("⚠️ No valid reference images found. Nothing to embed.")
        return

    print("\n📄 Labels embedded:")
    for label in embeddings_dict:
        print(f"  ✅ {label}")

    # Average multiple embeddings per label
    final_embeddings = []
    final_labels = []
    for label, vecs in embeddings_dict.items():
        final_embeddings.append(np.mean(vecs, axis=0))
        final_labels.append(label)

    np.save(OUTPUT_EMBEDDINGS, np.vstack(final_embeddings))
    with open(OUTPUT_LABELS, "w") as f:
        json.dump(final_labels, f)

    print(f"\n✅ Saved embeddings to {OUTPUT_EMBEDDINGS}")
    print(f"✅ Saved labels to {OUTPUT_LABELS}")
