import sys
import torch
import torch.nn as nn
import torch.optim as optim
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.data_loader import BrainTumorDataset
from src.model import BrainTumorModel
from src.trainer import Trainer

def main():
    # 1. Setup Device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # 2. Prepare Data
    print("Loading data...")
    dataset_path = "c:/Users/asus/Downloads/Medical"
    dm = BrainTumorDataset(dataset_path)
    train_loader, val_loader = dm.get_loaders(batch_size=32, num_workers=0)

    # 3. Initialize Model (Stage 1)
    print("Initializing model...")
    model = BrainTumorModel(num_classes=4, freeze_backbone=True)
    model = model.to(device)

    # 4. Define Loss
    criterion = nn.CrossEntropyLoss()
    
    # 5. Stage 1: Train Head Only
    print("\n=== Stage 1: Training Helper (Frozen Backbone) ===")
    # Optimize only the head
    optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-3)
    
    output_dir = "c:/Users/asus/Downloads/Medical/outputs/step4_training"
    trainer = Trainer(model, train_loader, val_loader, criterion, optimizer, device, output_dir)
    
    # Train for 5 epochs
    trainer.train(num_epochs=5)
    
    # 6. Stage 2: Fine-tuning
    print("\n=== Stage 2: Fine-tuning (Full Model) ===")
    model.unfreeze_backbone()
    
    # Lower learning rate for fine-tuning
    optimizer = optim.Adam(model.parameters(), lr=1e-4)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.1, patience=3, verbose=True)
    
    # Update trainer with new optimizer and scheduler
    trainer.optimizer = optimizer
    trainer.scheduler = scheduler
    
    # Train for more epochs
    trainer.train(num_epochs=20)
    
    print(f"\nTraining Complete. Best model saved to {output_dir}/best_model.pth")

if __name__ == "__main__":
    main()
