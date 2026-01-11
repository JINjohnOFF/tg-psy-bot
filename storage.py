import json
from threading import Lock
from datetime import datetime

FILE = "data.json"
lock = Lock()
MAX_MESSAGES = 500


def load():
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"groups": {}}


def save(data):
    with lock:
        with open(FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def get_user(group_id, user_id):
    return load()["groups"].get(str(group_id), {}).get("users", {}).get(str(user_id))


def save_message(group_id, user_id, text):
    data = load()
    group = data["groups"].setdefault(str(group_id), {"users": {}})
    user = group["users"].setdefault(str(user_id), {
        "messages": [],
        "passport": {
            "version": 0,
            "text": None,
            "confidence": 0.0,
            "last_update": None
        },
        "shift": {
            "detected": False,
            "reason": None
        }
    })

    user["messages"].append(text[-500:])
    if len(user["messages"]) > MAX_MESSAGES:
        user["messages"] = user["messages"][-MAX_MESSAGES:]

    save(data)


def update_passport(group_id, user_id, passport_data):
    data = load()
    user = data["groups"][str(group_id)]["users"][str(user_id)]

    user["passport"]["version"] += 1
    user["passport"]["text"] = passport_data["text"]
    user["passport"]["confidence"] = passport_data["confidence"]
    user["passport"]["last_update"] = datetime.utcnow().isoformat()

    user["shift"]["detected"] = passport_data["shift"]["detected"]
    user["shift"]["reason"] = passport_data["shift"]["reason"]

    user["messages"] = []
    save(data)