n = int(input())
numbers = list(map(int, input().split()))

for i in range(len(numbers)):
    numbers[i] = numbers[i] ** 2

print(*numbers)