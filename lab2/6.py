n = int(input())
numbers = list(map(int, input().split()))
maxnum = numbers[0]
for num in numbers:
    if num > maxnum:
       maxnum = num

print(maxnum)