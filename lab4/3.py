n = int(input())

first = True
for i in range(0, n + 1, 12):
    if first:
        print(i, end='')
        first = False
    else:
        print(f' {i}', end='')
print()