import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
        
    try:
        n = int(data[0])
        numbers = [int(data[i]) for i in range(1, min(n + 1, len(data)))]
        
        if numbers:
            unique_sorted = sorted(set(numbers))
            print(*(unique_sorted))
            
    except (ValueError, IndexError):
        return

if __name__ == "__main__":
    main()
