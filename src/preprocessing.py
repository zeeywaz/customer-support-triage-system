import pandas as pd
import re
import spacy

nlp = spacy.load("en_core_web_sm")

def clean_text(text):
    """Strips special characters, lowercases, and lemmatizes the text."""
    if pd.isna(text):
        return ""
    text = re.sub(r'[^a-zA-Z\s]', '', str(text)).lower()
    doc = nlp(text)
    cleaned = [token.lemma_ for token in doc if not token.is_stop and not token.is_space]
    return " ".join(cleaned)

def load_and_preprocess(filepath):
    """Loads the CSV and builds the feature and target columns."""
    df = pd.read_csv(filepath)
    print(f"Dataset columns found: {df.columns.tolist()}")

    # 1. Map Text Columns (Combines Subject and Body/Description if both exist)
    if 'Ticket Subject' in df.columns and 'Ticket Description' in df.columns:
        df['full_text'] = df['Ticket Subject'].fillna('') + " " + df['Ticket Description'].fillna('')
    elif 'subject' in df.columns and 'body' in df.columns:
        df['full_text'] = df['subject'].fillna('') + " " + df['body'].fillna('')
    elif 'Subject' in df.columns and 'Description' in df.columns:
        df['full_text'] = df['Subject'].fillna('') + " " + df['Description'].fillna('')
    elif 'text' in df.columns:
        df['full_text'] = df['text'].fillna('')
    elif 'body' in df.columns:
        df['full_text'] = df['body'].fillna('')
    elif 'description' in df.columns:
        df['full_text'] = df['description'].fillna('')
    else:
        # Fallback: take the first text-like object column
        text_cols = df.select_dtypes(include=['object']).columns
        df['full_text'] = df[text_cols[0]].fillna('')

    # 2. Map Target Category Column
    target_col = None
    for col in ['Ticket Type', 'category', 'Category', 'queue', 'label', 'type', 'issue_type']:
        if col in df.columns:
            target_col = col
            break
            
    if target_col is None:
        raise ValueError(f"Could not identify a target category column in {df.columns.tolist()}")

    df['Category'] = df[target_col].astype(str)

    print(f"Target categories found: {df['Category'].unique()}")
    print("Cleaning text data...")
    df['cleaned_text'] = df['full_text'].apply(clean_text)
    
    return df