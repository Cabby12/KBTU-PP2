n = int(input())
numbers = list(map(int, input().split()))

maxnum = numbers[0]
pos = 0

for i in range(len(numbers)):  
    if numbers[i] > maxnum:
        maxnum = numbers[i]
        pos = i  
print(pos+1)  