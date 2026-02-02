n = int(input())

first_occurrence = {}
strings = []

for i in range(1, n + 1):
    s = input().strip()
    strings.append(s)
    if s not in first_occurrence:
        first_occurrence[s] = i

unique_strings = sorted(set(strings))

for s in unique_strings:
    print(s, first_occurrence[s])