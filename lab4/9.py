def powers_of_two(n):
    for i in range(n + 1):
        yield 2 ** i

n = int(input())
print(' '.join(map(str, powers_of_two(n))))