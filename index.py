import heapq
import math
import os
import struct
import json
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

    def weighted_score(self):
        # TWEAK TAG WEIGHTS!
        return (
            self.freq * 1
            + self.importance_counts.get(Tag.H1.name, 0) * 5
            + self.importance_counts.get(Tag.H2.name, 0) * 4
            + self.importance_counts.get(Tag.H3.name, 0) * 3
            + self.importance_counts.get(Tag.BOLD.name, 0) * 2
        )


class Index:
    def __init__(self):
        self._memory_index = {}
        self._partial_paths = []
        self._total_doc_count = 0
        self.doc_id_to_url = {}
        self.doc_lengths = {}
        self.index = None
        self.lexicon = {}

    def load(self):
        if os.path.exists("lexicon.json"):
            with open("lexicon.json", "r", encoding="utf-8") as f:
                self.lexicon = json.load(f)
        if os.path.exists("index.bin"):
            self.index = open("index.bin", "rb")
        if os.path.exists("doc_lengths.json"):
            with open("doc_lengths.json", "r", encoding="utf-8") as f:
                self.doc_lengths = json.load(f)
            self._total_doc_count = len(self.doc_lengths)

    def add(
        self,
        token: str,
        document_id: int,
        frequency: int,
        importance: dict[Tag, int],
    ):
        self._memory_index.setdefault(token, []).append(
            Posting(document_id, frequency, importance)
        )

    def increment_doc_count(self):
        self._total_doc_count += 1

    def log_document_length(self, doc_id: int, length: int):
        self.doc_lengths[str(doc_id)] = length

    def flush_partial(self):
        if not self._memory_index:
            return
        path = f"index_part_{len(self._partial_paths)}.txt"

        with open(path, "w", encoding="utf-8") as partial:
            for token in sorted(self._memory_index.keys()):
                postings = self._memory_index[token]
                postings.sort(key=lambda x: x.document_id)

                postings_list = [
                    f"{p.document_id},{p.weighted_score()}" for p in postings
                ]
                line = f"{token}:" + ";".join(postings_list) + "\n"
                partial.write(line)

        self._partial_paths.append(path)
        self._memory_index = {}

    def merge_partials_bin(self):
        with open("doc_lengths.json", "w", encoding="utf-8") as f:
            json.dump(self.doc_lengths, f, indent=2)

        with open("index.bin", "wb") as index:
            files = [open(path, "r", encoding="utf-8") for path in self._partial_paths]
            merged_files = heapq.merge(*files)

            current_token = None
            current_postings = []
            for line in merged_files:
                # Find the last colon that separates token from postings
                # Postings always start with digits (doc_id), so find last colon before digits
                colon_idx = line.rfind(":")
                token = line[:colon_idx]
                postings = line[colon_idx + 1 :].strip()

                if current_token and token != current_token:
                    self._write_bin(
                        index, current_token, current_postings, self.doc_lengths
                    )
                    current_postings = []
                current_token = token
                current_postings.extend(postings.split(";"))

            if current_token:
                self._write_bin(
                    index, current_token, current_postings, self.doc_lengths
                )

            for file in files:
                file.close()

            self.write_lexicon()
            self.write_stats()

    def search(self, token: str):
        if token not in self.lexicon:
            return []

        metadata = self.lexicon[token]

        self.index.seek(metadata["offset"])
        data = self.index.read(metadata["size"])

        postings = []
        num_entries = metadata["size"] // 8
        for i in range(num_entries):
            doc_id, tfidf = struct.unpack("If", data[i * 8 : (i + 1) * 8])
            postings.append((doc_id, tfidf))

        return postings

    def boolean_and(self, tokens: list[str]):
        if not tokens:
            return []

        postings_lists = []
        for token in tokens:
            postings = self.search(token)
            if not postings:
                return []

            doc_ids = [p[0] for p in postings]
            postings_lists.append(doc_ids)
        postings_lists.sort(key=len)
        result = postings_lists[0]

        for other in postings_lists[1:]:
            result = self._merge_postings(result, other)
            if not result:
                return []
        return result

    def _merge_postings(self, p1: list[int], p2: list[int]):
        i = j = 0
        result = []

        while i < len(p1) and j < len(p2):
            if p1[i] == p2[j]:
                result.append(p1[i])
                i += 1
                j += 1
            elif p1[i] < p2[j]:
                i += 1
            else:
                j += 1

        return result

    def sort_tfidf(self, doc_ids: list[int], tokens: list[str]):
        doc_scores = {}
        doc_ids_set = set(doc_ids)
        for token in tokens:
            postings = self.search(token)
            for doc_id, tfidf in postings:
                if doc_id in doc_ids_set:
                    doc_scores[doc_id] = doc_scores.get(doc_id, 0) + tfidf

        result_with_scores = [(doc_id, doc_scores.get(doc_id, 0)) for doc_id in doc_ids]
        result_with_scores.sort(key=lambda x: x[1], reverse=True)

        return result_with_scores

    def close(self):
        if self.index is not None:
            self.index.close()

    def write_lexicon(self, path="lexicon.json"):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.lexicon, f, indent=2)

    def write_stats(self, path="stats.json"):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "unique_docs": self._total_doc_count,
                    "doc_id_to_url": self.doc_id_to_url,
                },
                f,
                indent=2,
            )

    def _write_bin(self, index, token, postings, doc_lengths):
        offset = index.tell()

        for p in postings:
            doc_id, weighted_score = p.split(",")
            tf = int(weighted_score) / doc_lengths[doc_id]
            tfidf = (1 + math.log(tf)) * math.log(self._total_doc_count / len(postings))

            index.write(struct.pack("If", int(doc_id), float(tfidf)))
        self.lexicon[token] = {"offset": offset, "size": index.tell() - offset}
