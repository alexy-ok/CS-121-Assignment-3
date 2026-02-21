import shelve
from enum import Enum

class Tag(Enum):
    H1 = "H1"
    H2 = "H2"
    H3 = "H3"
    BOLD = "BOLD"

class Posting:
    def __init__(self, document_id, freq, importance: dict[Tag, int]):
        self.document_id = document_id
        self.freq = freq
        self.importance_counts = importance

class Index:
    def __init__(self):
        self.index = shelve.open('index.shelve')
        self.index['stats:unique_docs'] = 0

    def add(self, token: str, document_id: str, frequency: int, importance: dict[Tag, int], tag = None):
        if token not in self.index:
            self.index[token] = []

        self.index[token].append(
            Posting(document_id, frequency, importance)
        )
        # doc_list = self.index[token]

        # if document_id not in doc_list:
        #     doc_list[document_id] = Posting(document_id, 1)
        # else:
        #     doc_list[document_id].freq += 1

        # if tag is not None:
        #     doc_list[document_id].importance_counts[tag] += 1
    
        # self.index[token] = doc_list
        self.index.sync()

    def search(self, token: str):
        return self.index.get(token, [])

    def increment_doc_count(self):
        self.index['stats:unique_docs'] = int(self.index['stats:unique_docs']) + 1
        self.index.sync()

    def print_stats(self):
        print(f"Total unique tokens: {len(self.index)}")
        print(f"Total documents: {self.index['stats:unique_docs']}")


    def close(self):
        self.index.close()