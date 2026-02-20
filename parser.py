import json
import re
from bs4 import BeautifulSoup
from stemmer import porter_stemmer
from index import Tag

class DocumentParser:
    def __init__(self, file_path):
        self.file_path = file_path
        
    def _tokenize(self, text: str) -> list[str]:
        tokens = []
        current_token = []

        for char in text:
            if char.isalnum():
                current_token.append(char.lower())
            else:
                if current_token:
                    tokens.append(''.join(current_token))
                    current_token = []

        if current_token:
            tokens.append(''.join(current_token))

        return tokens

    def _tokenize_and_stem(self, text: str) -> list[str]:
        tokens = self._tokenize(text)
        return [porter_stemmer(token) for token in tokens if token]

    def parse(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        url = data["url"]
        html_content = data["content"]

        soup = BeautifulSoup(html_content, "html.parser")

        full_text = soup.get_text(separator=" ")
        normal_tokens = self._tokenize_and_stem(full_text)

        important_tokens = {
            Tag.H1: [],
            Tag.H2: [],
            Tag.H3: [],
            Tag.BOLD: []
        }

        # Title, H1, H2, H3, Bold Tags
        if soup.title:
            important_tokens[Tag.H1] += self._tokenize_and_stem(soup.title.get_text())

        for tag in soup.find_all("h1"):
            important_tokens[Tag.H1] += self._tokenize_and_stem(tag.get_text())

        for tag in soup.find_all("h2"):
            important_tokens[Tag.H2] += self._tokenize_and_stem(tag.get_text())

        for tag in soup.find_all("h3"):
            important_tokens[Tag.H3] += self._tokenize_and_stem(tag.get_text())

        for tag in soup.find_all(["b", "strong"]):
            important_tokens[Tag.BOLD] += self._tokenize_and_stem(tag.get_text())

        # Remove URL fragments (#section)
        doc_id = url.split("#")[0]

        return doc_id, normal_tokens, important_tokens