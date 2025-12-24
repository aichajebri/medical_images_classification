import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.report_generator import MedicalReportGenerator

def main():
    output_dir = Path("c:/Users/asus/Downloads/Medical/outputs/step6_reports")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    generator = MedicalReportGenerator()
    
    # Test cases representing each class
    test_cases = [
        ("glioma", 0.985, "Heatmap shows significant localization in the temporal lobe region."),
        ("meningioma", 0.821, "Attention focused on the periphery of the dura mater."),
        ("pituitary", 0.941, "Hotspot localized in the pituitary fossa/sella turcica."),
        ("notumor", 0.992, "Diffuse attention with no sharp hotspots detected.")
    ]
    
    print("Generating sample reports...")
    
    for cls, conf, observation in test_cases:
        report = generator.generate_report(cls, conf, observation)
        
        # Print to console
        print(f"\n--- Report for {cls} ---")
        print(report)
        
        # Save to file
        file_path = output_dir / f"report_{cls}.txt"
        with open(file_path, "w") as f:
            f.write(report)
            
    print(f"\nAll reports generated and saved to {output_dir}")

if __name__ == "__main__":
    main()
