from src.pdf_export import PDFExporter
from src.report_generator import MedicalReportGenerator
from pathlib import Path

def test_pdf_generation():
    print("Testing PDF Generation...")
    
    # 1. Generate Report Text
    generator = MedicalReportGenerator()
    report_text = generator.generate_report("meningioma", 0.88, "Observation of dural tail sign.")
    print("\nGenerated Report Text:")
    print(report_text)
    
    # 2. Export PDF
    exporter = PDFExporter()
    output_path = Path("test_report.pdf")
    
    # Use a dummy image if exists, else it will use fallback
    image_path = "dummy_image.jpg"
    
    try:
        exporter.export(report_text, image_path, output_path)
        print(f"\nSuccessfully generated {output_path.absolute()}")
    except Exception as e:
        print(f"\nFAILED to generate PDF: {e}")

if __name__ == "__main__":
    test_pdf_generation()
