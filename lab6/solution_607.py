import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
        
    try:
        n = int(data[0])
        words = [data[i] for i in range(1, min(n + 1, len(data)))]
        
        if words:
            longest = max(words, key=len)
            print(longest)
            
    except (ValueError, IndexError):
        return

if __name__ == "__main__":
    main()
