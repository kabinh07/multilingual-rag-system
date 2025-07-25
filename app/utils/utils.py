import re

def __clean_text(text):
    text = re.sub(r'[\u200B-\u200D\uFEFF]', ' ', text)
    text = re.sub(r'--- Page \d+ ---', ' ', text)
    text = re.sub('[a-zA-Z0-9]', ' ', text)
    text = re.sub(r'শব্দার্থ ও টীকা.*', ' ', text)
    text = re.sub(r'সৃজনশীল প্রশ্ন.*', ' ', text)
    text = re.sub(r'অনলাইন ব্যাচ.*', ' ', text)
    text = re.sub(r'পাঠ্যপুস্তকের প্রশ্ন.*', ' ', text)
    text = re.sub(r'বহুনির্বাচনী.*', ' ', text)
    text = re.sub(r'শব্দের অর্থ ও ব্যাখ্যা.*', ' ', text)
    text = re.sub( r'^[\W_]+$', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def clean_full_text(text):
    new_texts = []
    for line in text.splitlines():
        line = __clean_text(line)
        if line != "":
            new_texts.append(line)
        elif line == "" and len(new_texts) > 0 and new_texts[-1] != "\n":
            new_texts.append("\n")
        else:
            continue
    print("\n".join(new_texts)[:100])
    return "\n".join(new_texts)