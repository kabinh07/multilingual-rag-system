import re

def __clean_text(text):
    text = re.sub(r'[\u200B-\u200D\uFEFF]', ' ', text)
    text = re.sub(r'--- Page \d+ ---', ' ', text)
    text = re.sub('[a-zA-Z0-9]', ' ', text)
    text = re.sub(r'^.*শব্দার্থ ও টীকা.*$', ' ', text)
    text = re.sub(r'^.*সৃজনশীল প্রশ্ন.*$', ' ', text)
    text = re.sub(r'^.*অনলাইন ব্যাচ.*$', ' ', text)
    text = re.sub(r'^.*পাঠ্যপুস্তকের প্রশ্ন.*$', ' ', text)
    text = re.sub(r'^.*হুনির্বাচনী.*$', ' ', text)
    text = re.sub(r'^.*শব্দের অর্থ ও ব্যাখ্যা.*$', ' ', text)
    text = re.sub(r'^.*নিচের কোনটি সঠিক.*$', ' ', text)
    text = re.sub(r'^.*নিচের উদ্দীপকটি পড়ে.*$', ' ', text)
    # text = re.sub(r'^.*সমাধান.*$', ' ', text)
    # text = re.sub(r'^.*॥\..*$', ' ', text)   
    text = re.sub( r'^[\W_]+$', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def __remove_mcq_and_refs(text):
    pattern = (
        # Qeustion lines
        r'^[০-৯0-9]+[।\.)]\s.*$'
        # Option lines of MCQs
        r'|^\s*\(?[কখগঘ]\)?[)।]?\s*.*$'
        # Board references
        r'|\[.*?\d+.*?\]'
        # Answer lines
        r'|^.*উত্তর:.*$'
    )
    
    cleaned = re.sub(pattern, '', text, flags=re.MULTILINE)
    cleaned = re.sub(r'\n{2,}', '\n\n', cleaned).strip()
    return cleaned

def clean_full_text(text, remove_mcqs=False):
    if remove_mcqs:
        text = __remove_mcq_and_refs(text)
    new_texts = []
    for line in text.splitlines():
        line = __clean_text(line)
        if line != "":
            new_texts.append(line)
    return "\n".join(new_texts)