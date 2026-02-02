n = int(input())

counts = {}

for _ in range(n):
    number = input().strip()
    counts[number] = counts.get(number, 0) + 1

result = 0
for cnt in counts.values():
    if cnt == 3:
        result += 1

print(result)