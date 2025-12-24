import sys
import torch
import cv2
import random
from pathlib import Path
import matplotlib.pyplot as plt

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.data_loader import BrainTumorDataset
from src.model import BrainTumorModel
from src.gradcam import GradCAM

def run_gradcam():
    # 1. Setup
    device = torch.device("cpu") # Grad-CAM is fast enough on CPU for single images
    output_dir = Path("c:/Users/asus/Downloads/Medical/outputs/step5_gradcam")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Loading Model...")
    model = BrainTumorModel(num_classes=4)
    checkpoint_path = "c:/Users/asus/Downloads/Medical/outputs/step4_training/model_checkpoint.pth"
    model.load_state_dict(torch.load(checkpoint_path, map_location=device))
    model.to(device)
    model.eval()
    
    # 2. Initialize Grad-CAM
    # Target Layer: Last residual block of ResNet50
    # model.backbone.layer4 is a Sequential block, we take the last one [-1]
    target_layer = model.backbone.layer4[-1]
    grad_cam = GradCAM(model, target_layer)
    
    # 3. Load Data to pick samples
    print("Loading Dataset...")
    dataset_path = "c:/Users/asus/Downloads/Medical"
    dm = BrainTumorDataset(dataset_path)
    
    # Pick 2 samples per class from Test set
    samples_to_process = []
    
    for cls in dm.classes:
        class_dir = dm.test_dir / cls
        files = list(class_dir.glob('*'))
        if files:
            selected = random.sample(files, min(2, len(files)))
            for f in selected:
                samples_to_process.append((f, cls))
                
    print(f"Processing {len(samples_to_process)} samples...")
    
    # 4. Generate Heatmaps
    transforms = dm.get_transforms('test')
    
    for img_path, true_label in samples_to_process:
        # Preprocess
        # Use simple PIL load to match what dataset class does internally or just use cv2 and convert
        # Here lets use the transform pipeline manually
        from PIL import Image
        pil_img = Image.open(img_path).convert('RGB')
        input_tensor = transforms(pil_img).unsqueeze(0).to(device)
        
        # Get Prediction
        output = model(input_tensor)
        prob = torch.nn.functional.softmax(output, dim=1)
        pred_idx = torch.argmax(prob, dim=1).item()
        pred_label = dm.classes[pred_idx]
        conf = prob[0, pred_idx].item()
        
        print(f"Image: {img_path.name} | True: {true_label} | Pred: {pred_label} ({conf:.2f})")
        
        # Generate Grad-CAM
        heatmap = grad_cam.generate_heatmap(input_tensor, class_idx=pred_idx)
        
        # Save visualization
        original, heat_img, overlay = grad_cam.overlay_heatmap(img_path, heatmap)
        
        # Stack images horizontally for nice view: Original | Heatmap | Overlay
        combined = cv2.hconcat([original, heat_img, overlay])
        
        fname = f"{true_label}_pred_{pred_label}_{img_path.stem}.jpg"
        cv2.imwrite(str(output_dir / fname), combined)
        
    print(f"Saved {len(samples_to_process)} visualizations to {output_dir}")

if __name__ == "__main__":
    run_gradcam()
