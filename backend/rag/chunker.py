import re

class TextChunker:
    def __init__(self, chunk_size=500, overlap=50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def clean_text(self, text):
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def chunk(self, text):
        text = self.clean_text(text)
        sentences = re.split(r"(?<=[.!?]) +", text)

        chunks = []
        current = ""

        for sentence in sentences:
            if len(current) + len(sentence) <= self.chunk_size:
                current += " " + sentence
            else:
                chunks.append(current.strip())
                current = sentence

        if current:
            chunks.append(current.strip())

        return chunks

def is_valid_page(text):
    return len(text) > 200