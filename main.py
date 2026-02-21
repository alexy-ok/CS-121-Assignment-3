from index import Index
from parser import DocumentParser
import logging
import os

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("log.txt", mode="w")],
    )
    log = logging.getLogger(__name__)

    index = Index()

    dev_dir_names = [d for d in os.listdir("DEV") if os.path.isdir(os.path.join("DEV", d))]
    log.info(f"Found {len(dev_dir_names)} directories to process")
    i = 0

    for dir in dev_dir_names:
        i += 1
        log.info(f"Processing directory #{i}/{len(dev_dir_names)}: {dir}")
        files = os.listdir(os.path.join("DEV", dir))
        log.info(f"Found {len(files)} files to process")

        for file in files:
            try:
                parser = DocumentParser(os.path.join("DEV", dir, file))
                # doc_id, normal_tokens, important_tokens, results = parser.parse()
                doc_hash, results = parser.parse()
                for token, data in results.items():
                    index.add(token, doc_hash, data['frequency'], data['importance'])
                # for token, in normal_tokens:
                #     index.add(token, doc_id)

                index.increment_doc_count()

            except Exception as e:
                log.error(f"Error parsing file {file}: {e}")

    index.print_stats()
    index.close()
        