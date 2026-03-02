import os
import random
import itertools
import re
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms

class SiameseCardDataset(Dataset):
    """
    Dataset for training a Siamese network using card augmentations.
    Now supports recursive folders (e.g., cards/, dice/) under image_folder.
    """

    def __init__(self, image_folder, transform=None):
        self.image_folder = image_folder
        self.transform = transform

        self.card_to_images = {}
        for root, _, files in os.walk(image_folder):
            for fname in files:
                if not fname.lower().endswith((".jpg", ".png")):
                    continue
                full_path = os.path.join(root, fname)
                rel_path = os.path.relpath(full_path, image_folder)
                card_id = re.sub(r"(_\d+)?_aug\d+\.(jpg|png)$", "", os.path.basename(fname))
                self.card_to_images.setdefault(card_id, []).append(rel_path)

        self.card_ids = list(self.card_to_images.keys())
        print("📂 Detected card/dice groups:")
        for card_id, imgs in self.card_to_images.items():
            print(f"  - {card_id}: {len(imgs)} images")

        self.pairs = self._generate_pairs()
        print(f"\n✅ Dataset successfully built with {len(self.pairs)} pairs.\n")

    def _generate_pairs(self):
        pairs = []
        pos_count = 0
        neg_count = 0

        print("\n🔁 Building positive pairs...")
        for card_id, images in self.card_to_images.items():
            if len(images) < 2:
                print(f"  ⚠️ Skipping {card_id}, only {len(images)} image(s).")
                continue
            combos = list(itertools.combinations(images, 2))
            for img1, img2 in combos:
                pairs.append((img1, img2, 1))
                pos_count += 1

        print("\n🔁 Building negative pairs...")
        while neg_count < pos_count:
            card1, card2 = random.sample(self.card_ids, 2)
            img1 = random.choice(self.card_to_images[card1])
            img2 = random.choice(self.card_to_images[card2])
            pairs.append((img1, img2, 0))
            neg_count += 1

        print(f"\n📊 Pair summary: {pos_count} positive, {neg_count} negative")
        random.shuffle(pairs)
        return pairs

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        fname1, fname2, label = self.pairs[idx]
        path1 = os.path.join(self.image_folder, fname1)
        path2 = os.path.join(self.image_folder, fname2)

        img1 = Image.open(path1).convert("RGB")
        img2 = Image.open(path2).convert("RGB")

        if self.transform:
            img1 = self.transform(img1)
            img2 = self.transform(img2)

        return img1, img2, label
