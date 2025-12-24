import torch
import torch.nn.functional as F
import numpy as np
import cv2

class GradCAM:
    """
    Implements Grad-CAM (Gradient-weighted Class Activation Mapping).
    """
    def __init__(self, model, target_layer):
        """
        Args:
            model: The PyTorch model.
            target_layer: The layer to hook into (e.g. model.backbone.layer4[-1]).
        """
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        # Register hooks
        self._register_hooks()

    def _register_hooks(self):
        def forward_hook(module, input, output):
            self.activations = output

        def backward_hook(module, grad_in, grad_out):
            self.gradients = grad_out[0]

        self.target_layer.register_forward_hook(forward_hook)
        self.target_layer.register_full_backward_hook(backward_hook)

    def generate_heatmap(self, input_tensor, class_idx=None):
        """
        Generates the Grad-CAM heatmap for a specific input and class.
        """
        # 0. Temporarily enable gradients for the whole model
        # We need this because if the backbone is frozen, gradients won't flow
        # to the target conv layer even if input_tensor.requires_grad = True
        param_grad_states = []
        for param in self.model.parameters():
            param_grad_states.append(param.requires_grad)
            param.requires_grad = True
            
        try:
            # 1. Forward Pass
            self.model.zero_grad()
            output = self.model(input_tensor)
            
            if class_idx is None:
                class_idx = torch.argmax(output, dim=1).item()
                
            # 2. Backward Pass
            score = output[0, class_idx]
            score.backward()
            
            # 3. Compute Grad-CAM
            gradients = self.gradients
            activations = self.activations
            
            if gradients is None or activations is None:
                raise RuntimeError("Gradients or activations not captured. Ensure the target layer is correct.")
                
            weights = torch.mean(gradients, dim=[2, 3], keepdim=True)
            cam = torch.sum(weights * activations, dim=1, keepdim=True)
            cam = F.relu(cam)
            
            cam = cam - cam.min()
            cam = cam / (cam.max() + 1e-7)
            
            return cam.squeeze().detach().cpu().numpy()
            
        finally:
            # 4. Restore original gradient states
            for param, state in zip(self.model.parameters(), param_grad_states):
                param.requires_grad = state

    @staticmethod
    def overlay_heatmap(image_path, heatmap, alpha=0.5):
        """
        Overlays the heatmap onto the original image.
        
        Args:
            image_path (str/Path): Path to original image.
            heatmap (np.ndarray): 2D heatmap array (0-1).
            alpha (float): Opacity of the heatmap.
            
        Returns:
            overlay (np.ndarray): The combined image.
        """
        img = cv2.imread(str(image_path))
        img = cv2.resize(img, (224, 224))
        
        # Resize heatmap to match image
        heatmap = cv2.resize(heatmap, (224, 224))
        
        # Colorize heatmap
        heatmap_uint8 = np.uint8(255 * heatmap)
        heatmap_colored = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
        
        # Overlay
        overlay = cv2.addWeighted(heatmap_colored, alpha, img, 1 - alpha, 0)
        
        return img, heatmap_colored, overlay
