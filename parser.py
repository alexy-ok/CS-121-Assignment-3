import json
from collections import Counter
from bs4 import BeautifulSoup
from index import Tag
import nltk

nltk.download('punkt')
nltk.download('punkt_tab')

class DocumentParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.stemmer = nltk.stem.PorterStemmer()
        
    def _tokenize_and_stem(self, text: str) -> list[str]:
        tokens = nltk.tokenize.word_tokenize(text)
        return [self.stemmer.stem(token) for token in tokens if token]

    def parse(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        url = data["url"]
        html_content = data["content"]

        soup = BeautifulSoup(html_content, "html5lib")

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

        normal_counts = Counter(normal_tokens)
        importance_counts = {tag: Counter(important_tokens[tag]) for tag in Tag}
        all_tokens = set(normal_counts) | set(t for tokens in important_tokens.values() for t in tokens)

        results = {}
        for token in all_tokens:
            results[token] = {
                "frequency": normal_counts.get(token, 0),
                "importance": {
                    tag.name: importance_counts[tag].get(token, 0)
                    for tag in Tag
                },
                "length": len(normal_tokens)
            }
        
        return results
        
