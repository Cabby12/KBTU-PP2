import re

s = input()
if re.search(r'^[a-zA-Z].*\d$', s):
    print("Yes")
else:
    print("No")
