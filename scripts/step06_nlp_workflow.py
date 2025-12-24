import sys
from pathlib import Path
import json

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.report_generator import MedicalReportGenerator
from src.ner_extraction import ClinicalNER
from src.chatbot_qa import MedicalChatbot
from src.pdf_export import PDFExporter

def main():
    print("--- NLP Workflow Demonstration ---\n")
    
    # 1. Prediction Inputs (Simulated from previous steps)
    pred_class = "pituitary"
    confidence = 0.942
    gradcam_obs = "Sellar region shows marked hyper-intensity focal points."
    
    # Initialize Modules
    generator = MedicalReportGenerator()
    ner = ClinicalNER()
    chatbot = MedicalChatbot()
    exporter = PDFExporter()
    
    output_dir = Path("c:/Users/asus/Downloads/Medical/outputs/step6_nlp")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # --- STEP 6.1: Clinical Findings Generation ---
    findings_text = generator.get_clinical_findings(pred_class)
    print(f"[6.1] Clinical Findings: {findings_text}")
    
    # --- STEP 6.2: NER Extraction ---
    entities = ner.extract_entities(findings_text)
    print(f"[6.2] Extracted Entities (JSON):\n{json.dumps(entities, indent=2)}")
    
    # --- STEP 6.3: Multi-section Report Generation ---
    report = generator.generate_report(pred_class, confidence, gradcam_obs)
    print(f"\n[6.3] Generated Medical Report:\n{report}")
    
    # --- STEP 6.4: Chatbot QA Interaction ---
    print("\n[6.4] Chatbot Demonstration:")
    q1 = "What did the AI find in this brain?"
    a1 = chatbot.get_response(q1, report)
    print(f"User: {q1}\nBot: {a1}")
    
    q2 = "What should I do next?"
    a2 = chatbot.get_response(q2, report)
    print(f"User: {q2}\nBot: {a2}")
    
    # --- STEP 6.5: PDF Export ---
    # We use a placeholder image for this test (or an existing one from step 5)
    img_path = Path("c:/Users/asus/Downloads/Medical/outputs/step5_gradcam/").glob("*.jpg")
    img_path = next(img_path, "placeholder.jpg") # Pick first available
    
    pdf_path = output_dir / "Final_Medical_Report.pdf"
    print(f"\n[6.5] Exporting to PDF...")
    try:
        exporter.export(report, img_path, pdf_path)
    except Exception as e:
        print(f"PDF Export failed: {e} (Ensure 'fpdf2' is installed)")

    print(f"\nWorkflow complete. See results in {output_dir}")

if __name__ == "__main__":
    main()
