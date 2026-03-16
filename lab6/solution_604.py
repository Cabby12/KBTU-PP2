import sys

def main():
    
    input_data = sys.stdin.read().split()
    if not input_data:
        return
        
    try:
        n = int(input_data[0])
        
        
        a = [int(input_data[i]) for i in range(1, n + 1)]
        
        
        b = [int(input_data[i]) for i in range(n + 1, 2 * n + 1)]
        
        
        dot_product = sum(x * y for x, y in zip(a, b))
        
        print(dot_product)
        
    except (ValueError, IndexError):
        
        return

if __name__ == "__main__":
    main()
