class MedicalChatbot:
    """
    A minimal NLP chatbot backend for answering questions about medical reports.
    Uses a rule-based QA approach with medical knowledge fallback.
    """
    def __init__(self):
        # Sample medical knowledge base for the chatbot
        self.knowledge_base = {
            "glioma": "A glioma is a type of tumor that starts in the glial cells of the brain or spine.",
            "meningioma": "A meningioma is a tumor that forms on the membranes that cover the brain and spinal cord.",
            "pituitary": "Pituitary tumors are abnormal growths that develop in your pituitary gland.",
            "notumor": "This means no significant abnormal masses were detected by the current analysis.",
            "grad-cam": "Grad-CAM is a technique used to visualize which parts of an image the AI model focused on.",
            "next steps": "You should consult with a neurologist or radiologist to discuss these findings professionally.",
            "disclaimer": "I am an AI assistant and cannot provide a medical diagnosis. Please see a doctor."
        }

    def get_response(self, user_query, report_text):
        """
        Processes a user query based on the report context and knowledge base.
        """
        query = user_query.lower()
        
        # 1. Check for specific terms in knowledge base
        for key, value in self.knowledge_base.items():
            if key in query:
                return value
                
        # 2. Context-aware fallback
        if "what" in query and "found" in query:
            if "GLIOMA" in report_text: return "The report identified features suggestive of a Glioma."
            if "MENINGIOMA" in report_text: return "The report identified features suggestive of a Meningioma."
            if "PITUITARY" in report_text: return "The report identified features suggestive of a Pituitary tumor."
            return "The report did not identify any tumor."

        if "recommendation" in query or "do next" in query:
            return "The primary recommendation is to have this report reviewed by a qualified medical professional."

        return "I'm sorry, I can only answer specific questions about the tumor types, Grad-CAM, or next steps found in this report."

if __name__ == "__main__":
    bot = MedicalChatbot()
    print(bot.get_response("What is a glioma?", "PRIMARY FINDING: GLIOMA"))
