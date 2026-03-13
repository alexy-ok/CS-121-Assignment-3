from index import Index
from parser import DocumentParser
import logging
import os
import hashlib
import re

SEEN_HASHES = set()
duplicates_removed = 0


def exact_duplicate(text: str):
    # Normalize text
    normalized = re.sub(r"\s+", " ", text.lower()).strip()

    # Create a 64-bit hash
    h = hashlib.blake2b(normalized.encode(), digest_size=8).hexdigest()

    if h in SEEN_HASHES:
        return True

    SEEN_HASHES.add(h)
    return False

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("log.txt", mode="w")],
    )
    log = logging.getLogger(__name__)

    index = Index()

    dev_dir_names = [
        d for d in os.listdir("DEV") if os.path.isdir(os.path.join("DEV", d))
    ]
    log.info(f"Found {len(dev_dir_names)} directories to process")

    total_docs = sum(
        sum(
            1
            for f in os.listdir(os.path.join("DEV", d))
            if os.path.isfile(os.path.join("DEV", d, f))
        )
        for d in dev_dir_names
    )
    log.info(f"Total documents to process: {total_docs}")

    flush_every = max(1, total_docs // 10)
    doc_count = 0
    i = 0

    for dir in dev_dir_names:
        i += 1
        log.info(f"Processing directory #{i}/{len(dev_dir_names)}: {dir}")
        files = os.listdir(os.path.join("DEV", dir))
        log.info(f"Found {len(files)} files to process")

        for file in files:
            try:
                parser = DocumentParser(os.path.join("DEV", dir, file))
                url, results, doc_length, text = parser.parse()

                # skip duplicate pages
                if exact_duplicate(text):
                    duplicates_removed += 1
                    continue

                index.doc_id_to_url[doc_count] = url
                index.log_document_length(doc_count, doc_length)
                for token, data in results.items():
                    index.add(token, doc_count, data["frequency"], data["importance"])

                index.increment_doc_count()
                doc_count += 1
                if doc_count % flush_every == 0:
                    index.flush_partial()

            except Exception as e:
                log.error(f"Error parsing file {file}: {e}")

    index.flush_partial()
    index.merge_partials_bin()
    index.close()
    log.info(f"Removed {duplicates_removed} duplicate pages")
    log.info("Indexing complete")
