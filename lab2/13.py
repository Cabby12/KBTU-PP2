x = int(input())

is_prime = True
for i in range(2, int(x**0.5) + 1):
        if x % i == 0:
            is_prime = False
            break
    

print("Yes" if is_prime else "No")