n = int(input())
numbers = list(map(int, input().split()))
squared_numbers = map(lambda x: x**2, numbers)
print(sum(squared_numbers))
