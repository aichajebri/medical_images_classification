import torch
import torch.nn as nn
from torchvision import models
from torchvision.models import ResNet50_Weights

class BrainTumorModel(nn.Module):
    """
    ResNet50-based model for Brain Tumor Classification.
    """
    def __init__(self, num_classes=4, freeze_backbone=True):
        """
        Args:
            num_classes (int): Number of output classes.
            freeze_backbone (bool): If True, freezes the pretrained layers.
        """
        super(BrainTumorModel, self).__init__()
        
        # Load pre-trained ResNet50
        # We use the 'DEFAULT' weights which correspond to the best available ImageNet weights
        self.backbone = models.resnet50(weights=ResNet50_Weights.DEFAULT)
        
        if freeze_backbone:
            self._freeze_params()
            
        # Replace the final fully connected layer
        # ResNet50's fc layer has 2048 input features
        num_ftrs = self.backbone.fc.in_features
        self.backbone.fc = nn.Linear(num_ftrs, num_classes)

    def _freeze_params(self):
        """Freezes all parameters in the backbone."""
        for param in self.backbone.parameters():
            param.requires_grad = False
            
    def unfreeze_backbone(self):
        """Unfreezes all parameters for fine-tuning."""
        for param in self.backbone.parameters():
            param.requires_grad = True

    def forward(self, x):
        return self.backbone(x)
