i = int(input()) + 1
a = [i**2 for i in range(i)]
a.pop(0)
for i in a:
    print(i)