import re
import html

MAX_CONTENT_LENGTH = 2000

def clean_text(text: str) -> str:

    if not text:
        return ""
    
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', text)

    text = html.escape(text)

    text = " ".join(text.split())

    if len(text) > MAX_CONTENT_LENGTH:
        text = text[:MAX_CONTENT_LENGTH]
    return text.strip()

def is_valid_content(text: str) -> bool:

    if not text:
        return False

    has_letters = bool(re.search(r'[a-zA-Z0-9]{3,}', text))

    is_not_repetition = not bool(re.search(r'(.)\1{15,}', text))

    return has_letters and is_not_repetition

