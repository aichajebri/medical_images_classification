import os
import sys
import torch
import cv2
import argparse
from pathlib import Path
from PIL import Image
import json

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.data_loader import BrainTumorDataset
from src.model import BrainTumorModel
from src.gradcam import GradCAM
from src.report_generator import MedicalReportGenerator
from src.ner_extraction import ClinicalNER
from src.pdf_export import PDFExporter

class InferencePipeline:
    """
    Orchestrates the entire Brain Tumor MRI analysis workflow.
    """
    def __init__(self, model_path, dataset_root):
        self.device = torch.device("cpu")
        self.output_dir = Path("c:/Users/asus/Downloads/Medical/outputs/inference_results")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Load Data/Preprocessing
        self.dm = BrainTumorDataset(dataset_root)
        self.transforms = self.dm.get_transforms('test')
        self.classes = self.dm.classes
        
        # 2. Initialize Model
        print("Initializing Model...")
        self.model = BrainTumorModel(num_classes=len(self.classes))
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()
        
        # 3. Initialize Grad-CAM
        target_layer = self.model.backbone.layer4[-1]
        self.grad_cam = GradCAM(self.model, target_layer)
        
        # 4. Initialize NLP Modules
        self.generator = MedicalReportGenerator()
        self.ner = ClinicalNER()
        self.exporter = PDFExporter()

    def run(self, image_path):
        """
        Runs the full inference pipeline on a single image.
        """
        img_path = Path(image_path)
        if not img_path.exists():
            print(f"Error: Image {image_path} not found.")
            return

        print(f"\n--- Processing Image: {img_path.name} ---")
        
        # A. Preprocessing
        pil_img = Image.open(img_path).convert('RGB')
        input_tensor = self.transforms(pil_img).unsqueeze(0).to(self.device)
        
        # B. Classification
        with torch.no_grad():
            output = self.model(input_tensor)
            probs = torch.nn.functional.softmax(output, dim=1)
            conf, pred_idx = torch.max(probs, dim=1)
            pred_class = self.classes[pred_idx.item()]
            conf_val = conf.item()
            
        print(f"Prediction: {pred_class.upper()} ({conf_val:.2%})")
        
        # C. Explainability (Grad-CAM)
        heatmap = self.grad_cam.generate_heatmap(input_tensor, class_idx=pred_idx.item())
        original, heat_img, overlay = self.grad_cam.overlay_heatmap(img_path, heatmap)
        
        # Save visualization to a temporary location for the PDF
        overlay_path = self.output_dir / f"overlay_{img_path.stem}.jpg"
        cv2.imwrite(str(overlay_path), overlay)
        
        # D. NLP Report Generation
        gradcam_obs = f"Model attention focused on region suggestive of {pred_class} morphology."
        report_text = self.generator.generate_report(pred_class, conf_val, gradcam_obs)
        findings_text = self.generator.get_clinical_findings(pred_class)
        
        # E. NER extraction (for log/verification)
        entities = self.ner.extract_entities(findings_text)
        print(f"Extracted Entities: {json.dumps(entities)}")
        
        # F. PDF Export
        pdf_path = self.output_dir / f"Report_{img_path.stem}.pdf"
        self.exporter.export(report_text, overlay_path, pdf_path)
        
        print(f"Pipeline complete. Report saved: {pdf_path}")
        return pdf_path

    # Helper added to GradCAM in thought: Wait, I should add overlay_heatmap to GradCAM 
    # but I'll use the one I implemented or just call the static method.

def main():
    parser = argparse.ArgumentParser(description="Run full MRI inference pipeline.")
    parser.add_argument("--image", type=str, help="Path to the MRI image file.")
    args = parser.parse_args()
    
    model_path = "c:/Users/asus/Downloads/Medical/outputs/step4_training/model_checkpoint.pth"
    dataset_root = "c:/Users/asus/Downloads/Medical"
    
    pipeline = InferencePipeline(model_path, dataset_root)
    
    if args.image:
        pipeline.run(args.image)
    else:
        # Demo mode: Pick a random image from the test set
        test_images = list(Path(dataset_root).glob("Testing/*/*.jpg"))
        if test_images:
            import random
            sample = random.choice(test_images)
            print(f"No image provided. Running demo on random test sample: {sample}")
            pipeline.run(sample)
        else:
            print("No test images found. Please provide an image path with --image.")

if __name__ == "__main__":
    main()
