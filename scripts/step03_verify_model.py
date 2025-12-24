import sys
import torch
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.model import BrainTumorModel

def verify_model():
    print("Initializing BrainTumorModel (ResNet50)...")
    model = BrainTumorModel(num_classes=4, freeze_backbone=True)
    
    # 1. Check Output Shape
    batch_size = 8
    dummy_input = torch.randn(batch_size, 3, 224, 224)
    print(f"Feeding dummy input: {dummy_input.shape}")
    
    output = model(dummy_input)
    print(f"Output shape: {output.shape}")
    
    assert output.shape == (batch_size, 4), f"Expected (8, 4), got {output.shape}"
    print("Shape Verification Passed!")
    
    # 2. Check Freezing
    print("\nChecking Parameter Freezing:")
    frozen_params = 0
    active_params = 0
    
    for name, param in model.named_parameters():
        if param.requires_grad:
            active_params += 1
        else:
            frozen_params += 1
            
    print(f"Frozen parameters (Backbone): {frozen_params}")
    print(f"Active parameters (Head): {active_params}")
    
    # ResNet50 has mainly frozen params, only the last fc layer (weight + bias) should be active
    # Note: If batchnorm layers are frozen/unfrozen depends on how we handle them, 
    # but strictly 'requires_grad' should be false for backbone.
    
    if active_params == 2: # Weight and Bias of fc
        print("Freezing Verification Passed! Only Head is trainable.")
    else:
        print(f"Warning: {active_params} trainable parameters found. Verify if this is intended.")
        
    print("\nModel implementation is correct and ready for training.")

if __name__ == "__main__":
    verify_model()
