from index import Index

if __name__ == "__main__":
    index = Index()
    index.load()
    index.merge_partials_bin()
    index.close()
