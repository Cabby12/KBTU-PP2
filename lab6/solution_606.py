import sys

def main():
    
    data = sys.stdin.read().split()
    if not data:
        return
        
    try:
        
        n = int(data[0])
        
        numbers = [int(data[i]) for i in range(1, min(n + 1, len(data)))]
        
        
        if all(x >= 0 for x in numbers):
            print("Yes")
        else:
            print("No")
            
    except (ValueError, IndexError):
        return

if __name__ == "__main__":
    main()
