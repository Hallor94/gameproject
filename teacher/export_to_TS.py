import torch
from torchvision import models
from torchvision.models import ResNet18_Weights
import os

def export_encoder_to_torchscript(output_dir="output"):
    ENCODER_PATH = os.path.join(output_dir, "siamese_encoder.pth")
    TORCHSCRIPT_OUT = os.path.join(output_dir, "siamese_encoder.pt")

    # Load encoder
    model = models.resnet18(weights=ResNet18_Weights.DEFAULT)
    model.fc = torch.nn.Identity()
    model.load_state_dict(torch.load(ENCODER_PATH, map_location="cpu"))
    model.eval()

    # Export to TorchScript
    dummy_input = torch.randn(1, 3, 224, 224)
    traced = torch.jit.trace(model, dummy_input)
    traced.save(TORCHSCRIPT_OUT)

    print(f"✅ TorchScript model saved to: {TORCHSCRIPT_OUT}")
