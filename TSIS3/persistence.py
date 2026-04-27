import json
import os

LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE    = "settings.json"

DEFAULT_SETTINGS = {
    "sound": True,
    "car_color": [0, 0, 200],
    "difficulty": "normal"
}


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE) as f:
                return json.load(f)
        except:
            pass
    return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)


def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE) as f:
                return json.load(f)
        except:
            pass
    return []


def save_score(username, score, distance, coins):
    lb = load_leaderboard()

    # remove existing entry for this username if exists
    lb = [e for e in lb if e["name"].lower() != username.lower()]

    lb.append({"name": username, "score": score, "distance": int(distance), "coins": coins})
    lb.sort(key=lambda x: x["score"], reverse=True)
    lb = lb[:10]

    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(lb, f, indent=2)
