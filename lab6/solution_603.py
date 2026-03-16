import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    try:
        n = int(data[0])
    except (ValueError, IndexError):
        return

    words = [data[i] for i in range(1, min(n + 1, len(data)))]
    
    result = []
    for i, word in enumerate(words):
        result.append(f"{i}:{word}")
    
    if result:
        print(" ".join(result))

if __name__ == "__main__":
    main()
