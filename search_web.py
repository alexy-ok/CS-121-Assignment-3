import streamlit as st
from index import Index
from search import tokenize_and_stem, search
import nltk
import time

index = Index()
index.load()

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)

st.title("CS 121 Assignment 3 Search Engine")

query = st.text_input("Enter your query")

if st.button("Search") or query:
    doc_ids, elapsed_ms, cached = search(query, index)
    st.write(f"Found {len(doc_ids)} results (processed in {elapsed_ms:.2f} ms) {"(cached)" if cached else ""}")
    if not doc_ids:
        st.write("No results found.")
    else:
        st.write("Top results:")
        for doc_id in doc_ids[:5]:
            url = index.doc_id_to_url.get(str(doc_id[0]), "(URL not found)")
            st.write(f"{url} (score: {doc_id[1]:.4f})")

