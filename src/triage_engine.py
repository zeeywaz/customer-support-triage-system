import os
import joblib
import numpy as np
from sentence_transformers import SentenceTransformer
from src.preprocessing import clean_text

MODEL_PATH = "models/lr_classifier.pkl"
TRANSFORMER_MODEL_NAME = "all-MiniLM-L6-v2"

class TriageEngine:
    def __init__(self, model_path=MODEL_PATH):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}. Please train the model first.")
        
        print("Initializing Triage Engine...")
        self.classifier = joblib.load(model_path)
        self.embedder = SentenceTransformer(TRANSFORMER_MODEL_NAME, device='cpu')
        print("Triage Engine ready!")

    def predict(self, subject: str, body: str) -> dict:
        """
        Takes raw subject and body, preprocesses, embeds, and predicts category + confidence.
        """
        raw_combined = f"{subject or ''} {body or ''}".strip()
        cleaned = clean_text(raw_combined)

        if not cleaned:
            return {
                "category": "unknown",
                "confidence": 0.0,
                "cleaned_text": ""
            }

        # Generate embedding
        embedding = self.embedder.encode([cleaned])

        # Predict class & confidence probabilities
        probabilities = self.classifier.predict_proba(embedding)[0]
        max_idx = np.argmax(probabilities)
        predicted_class = self.classifier.classes_[max_idx]
        confidence = float(probabilities[max_idx])

        return {
            "category": predicted_class,
            "confidence": round(confidence, 4),
            "cleaned_text": cleaned
        }

if __name__ == "__main__":
    engine = TriageEngine()
    test_subject = "Where is my order?"
    test_body = "I placed an order last week and tracking hasn't updated. Please help."
    result = engine.predict(test_subject, test_body)
    print("\n--- Test Prediction ---")
    print(f"Subject: {test_subject}")
    print(f"Predicted Category: {result['category']}")
    print(f"Confidence: {result['confidence'] * 100:.2f}%")