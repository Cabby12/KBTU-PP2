n = int(input())
arr = list(map(int, input().split()))

freq = {}
for num in arr:
    freq[num] = freq.get(num, 0) + 1

result = min(freq.items(), key=lambda x: (-x[1], x[0]))[0]
print(result)