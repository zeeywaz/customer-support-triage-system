import pandas as pd
import torch
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
from preprocessing import load_and_preprocess

def train_advanced_model(data_path):
    print("Loading and preprocessing dataset...")
    df = load_and_preprocess(data_path)
    df = df[df['cleaned_text'].str.strip() != '']
    
    # Transformers need a raw list of strings
    X = df['cleaned_text'].tolist() 
    y = df['Category']
    
    # Automatically detect if your RTX 2050 is available!
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"\n🚀 Loading Deep Learning Model on: {device.upper()}")
    
    # Load the pre-trained NLP model
    embedder = SentenceTransformer('all-MiniLM-L6-v2', device=device)
    
    print("Generating Semantic Embeddings (This is where the GPU shines)...")
    X_embeddings = embedder.encode(X, show_progress_bar=True)
    
    print("\nSplitting data into training and testing sets...")
    X_train, X_test, y_train, y_test = train_test_split(X_embeddings, y, test_size=0.2, random_state=42)
    
    print("Training Logistic Regression Classifier...")
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train, y_train)
    
    print("\n--- Advanced Model Evaluation ---")
    predictions = model.predict(X_test)
    print(classification_report(y_test, predictions))
    
    print("\nSaving AI brain to models/ folder...")
    joblib.dump(model, 'models/lr_classifier.pkl')
    # We don't need to save a vectorizer anymore, the Transformer handles it natively!
    print("Deep Learning Training complete!")

if __name__ == '__main__':
    train_advanced_model('data/customer_support_tickets.csv')