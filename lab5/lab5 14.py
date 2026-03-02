import re

s = input()
pattern = re.compile(r'^\d+$')
if pattern.match(s):
    print("Match")
else:
    print("No match")
