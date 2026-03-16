import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
        
    try:
        n = int(data[0])
        
        keys = [data[i] for i in range(1, n + 1)]
        values = [data[i] for i in range(n + 1, 2 * n + 1)]
        
        if len(data) > 2 * n + 1:
            query = data[2 * n + 1]
            dictionary = dict(zip(keys, values))
            print(dictionary.get(query, "Not found"))
            
    except (ValueError, IndexError):
        return

if __name__ == "__main__":
    main()
