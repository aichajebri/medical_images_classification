import os
import torch
import time
import cv2
import sys
from pathlib import Path
from PIL import Image
from typing import Tuple

# Add root to sys.path to access src modules
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(ROOT_DIR))

class InferenceService:
    """
    Singleton service to handle deep learning inference and NLP reporting 
    within the backend environment. Loads models lazily on first use.
    """
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InferenceService, cls).__new__(cls)
        return cls._instance

    def _ensure_initialized(self):
        """Lazy initialization - only loads models when first needed."""
        if self._initialized:
            return
            
        try:
            from src.model import BrainTumorModel
            from src.gradcam import GradCAM
            from src.report_generator import MedicalReportGenerator
            from src.ner_extraction import ClinicalNER
            from src.pdf_export import PDFExporter
            
            self.device = torch.device("cpu")
            
            # Get model path from environment or use default
            model_path_env = os.getenv("MODEL_PATH")
            if model_path_env:
                self.model_path = Path(model_path_env)
            else:
                # Priority: best_model.pth (new training) > model_checkpoint.pth (old default)
                best_model = ROOT_DIR / "outputs/step4_training/best_model.pth"
                if best_model.exists():
                    self.model_path = best_model
                else:
                    self.model_path = ROOT_DIR / "outputs/step4_training/model_checkpoint.pth"
            
            # Load Model
            print(f"Loading model from {self.model_path}...")
            self.model = BrainTumorModel(num_classes=4)
            self.model.load_state_dict(torch.load(self.model_path, map_location=self.device))
            self.model.to(self.device)
            self.model.eval()
            print("Model loaded successfully!")
            
            # Load Grad-CAM
            target_layer = self.model.backbone.layer4[-1]
            self.grad_cam = GradCAM(self.model, target_layer)
            
            # Load NLP Modules
            self.generator = MedicalReportGenerator()
            self.ner = ClinicalNER()
            self.exporter = PDFExporter()
            
            # Get storage path from environment or use default
            storage_path_env = os.getenv("STORAGE_PATH")
            if storage_path_env:
                self.storage_root = Path(storage_path_env)
            else:
                self.storage_root = ROOT_DIR / "backend/storage"
            
            # Ensure storage directories exist
            (self.storage_root / "images").mkdir(parents=True, exist_ok=True)
            (self.storage_root / "heatmaps").mkdir(parents=True, exist_ok=True)
            (self.storage_root / "reports").mkdir(parents=True, exist_ok=True)
            
            # Store classes for prediction
            self.classes = ['glioma', 'meningioma', 'notumor', 'pituitary']
            
            self._initialized = True
            print("Inference service fully initialized!")
            
        except Exception as e:
            print(f"Error initializing inference service: {e}")
            import traceback
            traceback.print_exc()
            raise

    def run_full_inference(self, image_path: Path) -> dict:
        """
        Runs the 7-step pipeline on an uploaded image.
        """
        # Ensure models are loaded
        self._ensure_initialized()
        
        start_time = time.time()
        
        # 1. Preprocessing
        pil_img = Image.open(image_path).convert('RGB')
        
        # Create transforms directly instead of using BrainTumorDataset
        from torchvision import transforms
        normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                         std=[0.229, 0.224, 0.225])
        test_transforms = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            normalize
        ])
        
        input_tensor = test_transforms(pil_img).unsqueeze(0).to(self.device)
        
        # 2. Prediction
        with torch.no_grad():
            output = self.model(input_tensor)
            probs = torch.nn.functional.softmax(output, dim=1)
            conf, pred_idx = torch.max(probs, dim=1)
            pred_class = self.classes[pred_idx.item()]
            confidence = conf.item()

        # 3. Grad-CAM
        heatmap = self.grad_cam.generate_heatmap(input_tensor, class_idx=pred_idx.item())
        original, heat_img, overlay = self.grad_cam.overlay_heatmap(image_path, heatmap)
        
        heatmap_filename = f"heatmap_{image_path.stem}.jpg"
        heatmap_path = self.storage_root / "heatmaps" / heatmap_filename
        cv2.imwrite(str(heatmap_path), overlay)
        
        # 4. NLP Report
        gradcam_obs = f"Model attention localized in area characteristic of {pred_class} morphology."
        report_text = self.generator.generate_report(pred_class, confidence, gradcam_obs)
        
        # 5. PDF Export
        pdf_filename = f"Report_{image_path.stem}.pdf"
        pdf_path = self.storage_root / "reports" / pdf_filename
        self.exporter.export(report_text, heatmap_path, pdf_path)
        
        processing_time = time.time() - start_time
        
        return {
            "class_label": pred_class,
            "confidence": confidence,
            "heatmap_path": f"storage/heatmaps/{heatmap_filename}",
            "pdf_path": f"storage/reports/{pdf_filename}",
            "processing_time": processing_time
        }

# Singleton instance - does NOT initialize on import anymore
inference_service = InferenceService()
