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
    
    def __str__(self):
        return f"{self.document_id} {self.freq} {self.importance_counts[Tag.H1.name]} {self.importance_counts[Tag.H2.name]} {self.importance_counts[Tag.H3.name]} {self.importance_counts[Tag.BOLD.name]}"

class Index:
    def __init__(self, load_from_file=None):
        self._memory_index = {}
        self._partial_paths = []
        self._total_doc_count = 0
        self.index = None
        if load_from_file:
            self.load(load_from_file)

    def add(self, token: str, document_id: str, frequency: int, importance: dict[Tag, int], tag=None):
        self._memory_index.setdefault(token, []).append(
            Posting(document_id, frequency, importance)
        )

    def increment_doc_count(self):
        self._total_doc_count += 1

    def flush_partial(self):
        if not self._memory_index:
            return
        path = f"index_part_{len(self._partial_paths)}.shelve"
        partial = shelve.open(path, flag="c")
        try:
            for token, postings in self._memory_index.items():
                sorted_postings = sorted(postings, key=lambda x: int(x.document_id))
                partial[token] = [str(posting) for posting in sorted_postings]

            partial.sync()
        finally:
            partial.close()
        self._partial_paths.append(path)
        self._memory_index = {}

    def merge_partials(self):
        self.index = shelve.open("index.shelve", flag="c")
        self.index["stats:unique_docs"] = 0
        for path in self._partial_paths:
            partial = shelve.open(path, flag="r")
            try:
                for token in partial:
                    postings = partial[token]
                    existing = self.index.get(token, [])
                    sorted_postings = sorted(postings + existing, key=lambda x: int(x.split(" ")[0]))
                    self.index[token] = sorted_postings
            finally:
                partial.close()
        self.index["stats:unique_docs"] = self._total_doc_count
        self.index.sync()

    def search(self, token: str):
        if self.index is None:
            return []
        return self.index.get(token, [])

    def print_stats(self):
        if self.index is None:
            return
        doc_count = self.index["stats:unique_docs"]
        token_count = len(self.index) - 1
        print(f"Total unique tokens: {token_count}")
        print(f"Total documents: {doc_count}")

    def load(self, path="index.shelve"):
        """Load an existing index from a shelve file."""
        if self.index is not None:
            self.index.close()
        self.index = shelve.open(path, flag="r")
        self._total_doc_count = self.index.get("stats:unique_docs", 0)

    def close(self):
        if self.index is not None:
            self.index.close()
            self.index = None
