import sys
from pathlib import Path
import matplotlib.pyplot as plt
import torch
import numpy as np

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.data_loader import BrainTumorDataset

def denormalize(tensor):
    """Reverts ImageNet normalization for visualization."""
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    
    img = tensor.numpy().transpose((1, 2, 0)) # C,H,W -> H,W,C
    img = std * img + mean
    img = np.clip(img, 0, 1)
    return img

def verify_transforms():
    dataset_path = "c:/Users/asus/Downloads/Medical"
    output_dir = Path("c:/Users/asus/Downloads/Medical/outputs/step2_augmentation")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Initializing Data Module...")
    dm = BrainTumorDataset(dataset_path)
    
    print("Creating DataLoaders...")
    train_loader, _ = dm.get_loaders(batch_size=8, num_workers=0) # num_workers=0 for simple debugging
    
    print("Fetching a batch of training data...")
    images, labels = next(iter(train_loader))
    
    print(f"Batch Shape: {images.shape}")
    print(f"Labels: {labels}")
    
    # Visualization
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    classes = dm.classes
    
    for i, ax in enumerate(axes.flat):
        img = denormalize(images[i])
        label = classes[labels[i]]
        
        ax.imshow(img)
        ax.set_title(f"{label}\n(Augmented)")
        ax.axis('off')
        
    plt.suptitle("Augmented Training Batch (224x224, Normalized)")
    plt.savefig(output_dir / 'augmented_samples.png')
    print(f"Saved augmented samples to {output_dir / 'augmented_samples.png'}")

if __name__ == "__main__":
    verify_transforms()
