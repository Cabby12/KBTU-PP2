n = int(input())
arr = list(map(int, input().split()))


counts = {}
for num in arr:
    if num in counts:
        counts[num] += 1
    else:
        counts[num] = 1


max_count = 0
for cnt in counts.values():
    if cnt > max_count:
        max_count = cnt


result = 10**9
for num, cnt in counts.items():
    if cnt == max_count and num < result:
        result = num

print(result)