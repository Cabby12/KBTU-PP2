n = int(input())

surnames = set()

for _ in range(n):
    surname = input().strip()
    surnames.add(surname)

print(len(surnames))