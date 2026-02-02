n = int(input())

doramas = {}

for _ in range(n):
    name, episodes = input().split()
    episodes = int(episodes)

    if name in doramas:
        doramas[name] += episodes
    else:
        doramas[name] = episodes

for name in sorted(doramas.keys()):
    print(name, doramas[name])