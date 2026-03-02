import re

def double_digit(match):
    return match.group() * 2

s = input()
result = re.sub(r'\d', double_digit, s)
print(result)
