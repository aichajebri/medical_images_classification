import json
import re

class ClinicalNER:
    """
    Simulates Named Entity Recognition (NER) for medical findings extraction.
    
    To ensure robustness and interpretability in a clinical context, the NER stage 
    relies on a deterministic, dictionary-enhanced approach optimized for medical 
    terminology extraction. This design choice enables reliable identification of 
    core clinical entities (tumor type, anatomical site, and radiological findings) 
    while remaining computationally efficient under CPU constraints and avoiding 
    the overhead of large transformer-based NER models.
    """
    def __init__(self):
        # Entity patterns
        self.entities = {
            "TUMOR_TYPE": ["glioma", "meningioma", "pituitary", "tumor", "mass", "lesion"],
            "ANATOMICAL_SITE": ["sellar", "pituitary fossa", "temporal lobe", "frontal", "meninges", "dura mater", "brain"],
            "CLINICAL_TERM": ["edema", "mass effect", "circumscribed", "dural tail", "endocrine", "glial"]
        }

    def extract_entities(self, text):
        """
        Parses the clinical findings text and extracts key entities.
        
        Args:
            text (str): The clinical findings text.
            
        Returns:
            dict: JSON-like dictionary of extracted entities.
        """
        findings = {
            "TUMOR_TYPE": "Not detected",
            "ANATOMICAL_SITE": "Not specified",
            "FINDINGS": []
        }
        
        text_lower = text.lower()
        
        # 1. Extract Tumor Type
        for tumor in self.entities["TUMOR_TYPE"]:
            if tumor in text_lower:
                findings["TUMOR_TYPE"] = tumor
                break
                
        # 2. Extract Anatomical Site
        for site in self.entities["ANATOMICAL_SITE"]:
            if site in text_lower:
                findings["ANATOMICAL_SITE"] = site
                break
                
        # 3. Extract General Clinical Terms (Findings)
        for term in self.entities["CLINICAL_TERM"]:
            if term in text_lower:
                findings["FINDINGS"].append(term)
                
        return findings

    def to_json(self, findings):
        return json.dumps(findings, indent=2)

if __name__ == "__main__":
    # Test
    ner = ClinicalNER()
    sample_text = "The findings are suggestive of a glioma in the frontal region with significant peritumoral edema."
    results = ner.extract_entities(sample_text)
    print(ner.to_json(results))
