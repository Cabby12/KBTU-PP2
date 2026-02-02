import sys
read = sys.stdin.readline
write = sys.stdout.write
n = int(read())
db = {}
for _ in range(n):
    line = read().split()
    if line[0] == "set":
        db[line[1]] = line[2]
    else:
        key = line[1]
        if key in db:
            write(db[key] + '\n')
        else:
            write(f"KE: no key {key} found in the document\n")