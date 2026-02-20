from index import Index
from parser import DocumentParser
import os

if __name__ == "__main__":
    index = Index()

    dev_dir_names = [d for d in os.listdir("DEV") if os.path.isdir(os.path.join("DEV", d))]
    for dir in dev_dir_names:
        for file in os.listdir(os.path.join("DEV", dir)):
            try:
                parser = DocumentParser(os.path.join("DEV", dir, file))
                doc_id, normal_tokens, important_tokens = parser.parse()
                for token in normal_tokens:
                    index.add(token, doc_id)
                    
                index.increment_doc_count()
                
            except Exception as e:
                print(f"Error parsing file {file}: {e}")

    index.print_stats()
    index.close()
        