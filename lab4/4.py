start, end = map(int, input().split())
a = [i**2 for i in range(start, end+1)]
for i in a:
    print(i)