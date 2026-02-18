import shelve

class Posting:
    def __init__(self, document_id, freq):
        self.document_id = document_id
        self.freq = freq
        #TODO: H1, H2, H3, Bold counts

class Index:
    def __init__(self):
        self.index = shelve.open('index.db')
        self.index['stats:unique_docs'] = 0

    def add(self, token: str, document_id: str):
        if token not in self.index:
            self.index[token] = {}

        doc_list = self.index[token]

        if document_id not in doc_list:
            doc_list[document_id] = Posting(document_id, 1)
        else:
            doc_list[document_id] = Posting(document_id, doc_list[document_id].freq + 1)
    
        self.index[token] = doc_list
        self.index.sync()

    def search(self, token: str):
        return self.index.get(token, [])

    def print_stats(self):
        print(f"Total unique tokens: {len(self.index)}")
        print(f"Total documents: {self.index['stats:unique_docs']}")


    def close(self):
        self.index.close()