import re
from app.utils.utils import clean_full_text

def extract_paragraphs(text):
    pattern = (
        # 1. Question lines (e.g., ১। প্রশ্ন / 41) প্রশ্ন)
        r'^[০-৯0-9]+[।\.)]\s.*$'
        # 2. Option lines starting with ক/খ/গ/ঘ in any format
        r'|^\s*\(?[কখগঘ]\)?[)।]?\s*.*$'
        # 3. Board references [ ... digits ... ] inline or standalone
        r'|\[.*?\d+.*?\]'
        # 4. Answer lines (উত্তর:)
        r'|^.*উত্তর:.*$'
    )
    
    cleaned = re.sub(pattern, '', text, flags=re.MULTILINE)
    cleaned = re.sub(r'\n{2,}', '\n\n', cleaned).strip()
    return cleaned

with open("app/knowledge_bases/HSC26-Bangla1st-Paper.txt", "r", encoding="utf-8") as f:
    text = f.read()
    cleaned_text = extract_paragraphs(text)
    cleaned_text = clean_full_text(cleaned_text)

with open("app/knowledge_bases/HSC26-Bangla1st-Paper-cleaned.txt", "w", encoding="utf-8") as f:
    f.write(cleaned_text)