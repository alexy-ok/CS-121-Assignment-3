from index import Index

if __name__ == "__main__":
    index = Index(load_from_file="index.shelve")
    
    while True:
        command = input("Enter q to query or x to quit: ")
        if command == "x":
            break
        elif command == "q":
            query = input("Enter query: ")
            
            results = index.search(query)
            print(f"Found {len(results)} results")
            results = results.split("\n")
            for result in results[:5]:
                print(f'Doc ID: {result.split(" ")[0]} Frequency: {result.split(" ")[1]} Importance: {result.split(" ")[2]} {result.split(" ")[3]} {result.split(" ")[4]} {result.split(" ")[5]}')
        else:
            print("Invalid command. Please enter 'q' or 'x'.")
    
    print("Exiting...")
    index.close()