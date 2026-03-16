import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
        
    try:
        n = int(data[0])
        numbers = [int(data[i]) for i in range(1, min(n + 1, len(data)))]
        
        if numbers:
            truthy_count = sum(map(bool, numbers))
            print(truthy_count)
        else:
            if n == 0:
                print(0)
            
    except (ValueError, IndexError):
        return

if __name__ == "__main__":
    main()
