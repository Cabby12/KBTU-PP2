import re

s = input()
sequences = re.findall(r'\d{2,}', s)
print(" ".join(sequences))
