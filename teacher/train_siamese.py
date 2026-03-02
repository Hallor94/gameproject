# train_siamese.py
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models, transforms
from torch.utils.data import DataLoader
from siamese_dataset import SiameseCardDataset
import torch.nn.functional as F
import os
import matplotlib.pyplot as plt
from torch import amp
from torchvision.models import ResNet18_Weights

# === Contrastive Loss ===
class ContrastiveLoss(nn.Module):
    def __init__(self, margin):
        super().__init__()
        self.margin = margin

    def forward(self, dist, label):
        loss = 0.5 * (label * dist.pow(2) + (1 - label) * F.relu(self.margin - dist).pow(2))
        return loss.mean()

# === Siamese Network Definition ===
class SiameseNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        
        base = models.resnet18(weights=ResNet18_Weights.DEFAULT)
        base.fc = nn.Identity()
        self.encoder = base

    def forward_once(self, x):
        return self.encoder(x)

    def forward(self, x1, x2):
        f1 = self.forward_once(x1)
        f2 = self.forward_once(x2)
        return f1, f2

# === Training Function ===
def train_model(output_dir="output", use_early_stopping=False, full_pair_generation=True,
                epochs=20, batch_size=16, lr=1e-4, margin=1.0, patience=3, threshold=0.001, target_loss=0.1):
    print("🧠 Preparing training dataset...")
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ])

    dataset = SiameseCardDataset("augmented_cards", transform=transform)
    if len(dataset) < 100:
        print("⚠️ Warning: Very few training pairs available! Add more images or augmentations.")
    print(f"📊 Total pairs available: {len(dataset)}")

    if len(dataset) == 0:
        raise ValueError("❌ No valid training pairs found. Check your augmented_cards directory and ensure multiple images per label.")


    use_cuda = torch.cuda.is_available()
    device = torch.device("cuda" if use_cuda else "cpu")
    device_type = "cuda" if use_cuda else "cpu"

    num_workers = min(8, 6) if use_cuda else 0
    prefetch = 2 if use_cuda else 0
    dataloader = DataLoader(
        dataset,
        batch_size=max(batch_size, 32),
        shuffle=True,
        num_workers=4 if use_cuda else 0,
        pin_memory=use_cuda,
        prefetch_factor=prefetch
    )

    model = SiameseNetwork().to(device)
    criterion = ContrastiveLoss(margin=margin)
    optimizer = optim.Adam(model.parameters(), lr=lr)

    best_loss = float('inf')
    epochs_no_improve = 0
    loss_history = []
    import time
    total_start_time = time.time()

    print(f"🔁 Starting training (max {epochs} epochs)...")
    scaler = amp.GradScaler()

    import time

    for epoch in range(epochs):
        start_time = time.time()
        model.train()
        running_loss = 0.0
        for batch_idx, (img1, img2, labels) in enumerate(dataloader, 1):
            img1, img2, labels = img1.to(device), img2.to(device), labels.float().to(device)
            optimizer.zero_grad()
            with amp.autocast(device_type=device_type):
                f1, f2 = model(img1, img2)
                dist = F.pairwise_distance(f1, f2)
                loss = criterion(dist, labels)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            running_loss += loss.item()
            if batch_idx % 10 == 0 or batch_idx == len(dataloader):
                print(f"    Batch {batch_idx}/{len(dataloader)} - Loss: {loss.item():.4f}")

        avg_loss = running_loss / len(dataloader)
        loss_history.append(avg_loss)
        elapsed = time.time() - start_time
        eta = elapsed * (epochs - (epoch + 1))
        device_status = "GPU" if use_cuda else "CPU"
        print(f"📈 Epoch [{epoch+1}/{epochs}] Loss: {avg_loss:.4f} — Time: {elapsed:.2f}s — ETA: {eta:.2f}s — Device: {device_status}")

        if use_early_stopping:
            if avg_loss < target_loss:
                print(f"🛑 Early stopping: target loss reached (avg_loss={avg_loss:.4f})")
                break
            if avg_loss < best_loss - threshold:
                best_loss = avg_loss
                epochs_no_improve = 0
            else:
                epochs_no_improve += 1
                if epochs_no_improve >= patience:
                    print(f"⏹️ Early stopping triggered at epoch {epoch+1}.")
                    break

    os.makedirs(output_dir, exist_ok=True)
    model_path = os.path.join(output_dir, "siamese_encoder.pth")
    torch.save(model.encoder.state_dict(), model_path)
    print(f"✅ Trained encoder saved to: {model_path}")

    # Plot training loss
    plt.figure()
    plt.plot(range(1, len(loss_history) + 1), loss_history, marker='o')
    plt.title("Training Loss per Epoch")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.grid(True)
    loss_plot_path = os.path.join(output_dir, "loss_plot.png")
    plt.savefig(loss_plot_path)
    plt.close()
    print(f"📉 Loss plot saved to: {loss_plot_path}")
    total_time = time.time() - total_start_time
    print(f"⏱️ Total training time: {total_time:.2f}s")
