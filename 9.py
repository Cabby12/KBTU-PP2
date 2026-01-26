n = int(input())
arr = list(map(int, input().split()))


min_val = min(arr)
max_val = max(arr)


result = [min_val if x == max_val else x for x in arr]
print(*result)