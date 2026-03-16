import sys

def main():
    line1 = sys.stdin.readline()
    if not line1:
        return
    n = int(line1.strip())
    
    data = sys.stdin.read().split()
    numbers = [int(x) for x in data]
    
    even_numbers = filter(lambda x: x % 2 == 0, numbers)
    
    print(len(list(even_numbers)))

if __name__ == "__main__":
    main()
