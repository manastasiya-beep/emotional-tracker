import random
from collections import Counter
from datetime import datetime, timedelta, timezone

import db
from config import PAINTINGS, WEEKLY_ENTRIES_THRESHOLD, WEEKLY_WINDOW_DAYS


def pick_painting(zone, exclude_ids=None, fallback_zone=None):
    candidates = [p for p in PAINTINGS if p["zone"] == zone]
    exclude_ids = set(exclude_ids or [])
    candidates = [p for p in candidates if p["id"] not in exclude_ids]
    if not candidates and fallback_zone:
        candidates = [
            p for p in PAINTINGS
            if p["zone"] == fallback_zone and p["id"] not in exclude_ids
        ]
    if not candidates:
        candidates = [p for p in PAINTINGS if p["zone"] == zone]
    return random.choice(candidates)


def dominant_zone(entries):
    counts = Counter(entry["zone"] for entry in entries)
    highest_count = max(counts.values())
    tied_zones = {zone for zone, count in counts.items() if count == highest_count}
    for entry in reversed(entries):
        if entry["zone"] in tied_zones:
            return entry["zone"]
    return None


def painting_valence(zone):
    return "pleasant" if zone in {"yellow", "green"} else "unpleasant"


def neighboring_zone(zone):
    return {"red": "blue", "blue": "red", "yellow": "green", "green": "yellow"}[zone]


def maybe_give_weekly_reward(telegram_id):
    since = (datetime.now(timezone.utc) - timedelta(days=WEEKLY_WINDOW_DAYS)).isoformat()
    recent = db.entries_since(telegram_id, since)
    if len(recent) < WEEKLY_ENTRIES_THRESHOLD:
        return None

    last_reward = db.last_weekly_reward(telegram_id)
    if last_reward:
        last_given = datetime.fromisoformat(last_reward["given_at"])
        if datetime.now(timezone.utc) - last_given < timedelta(days=WEEKLY_WINDOW_DAYS):
            return None

    selected_zone = dominant_zone(recent)

    painting = pick_painting(selected_zone)

    db.record_weekly_reward(telegram_id, selected_zone, painting["id"])
    return painting
