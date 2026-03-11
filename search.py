from index import Index
import nltk
import time


try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab", quiet=True)


def tokenize_and_stem(query: str):
    stemmer = nltk.stem.PorterStemmer()
    tokens = nltk.tokenize.word_tokenize(query)
    return [stemmer.stem(t.lower()) for t in tokens if t.isalnum()]

def search(query: str, index: Index):
    start_time = time.perf_counter()
    query = query.lower()
    tokens = tokenize_and_stem(query)
    doc_ids = index.boolean_and(tokens)
    doc_ids = index.sort_tfidf(doc_ids, tokens)
    end_time = time.perf_counter()
    elapsed_ms = (end_time - start_time) * 1000
    return doc_ids, elapsed_ms

if __name__ == "__main__":
    # Load the index
    index = Index()
    index.load()

    print("Interactive query interface (type 'exit' to quit)\n")

    while True:
        query = input("Enter query: ").strip()
        if query.lower() in ("exit", "quit"):
            break
        doc_ids, elapsed_ms = search(query, index)
        print(f"Found {len(doc_ids)} results (processed in {elapsed_ms:.2f} ms)")
        if not doc_ids:
            print("No results found.\n")
            continue
        print("Top results:")
        for doc_id in doc_ids[:5]:  # show top 5
            url = index.doc_id_to_url.get(str(doc_id[0]), "(URL not found)")
            print(f"- {url}")
        print()

    index.close()
