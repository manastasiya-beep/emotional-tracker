import random
from collections import Counter
from datetime import datetime, timedelta, timezone

import db
from config import PAINTINGS, WEEKLY_ENTRIES_THRESHOLD, WEEKLY_WINDOW_DAYS


def pick_painting(zone, exclude_id=None):
    candidates = [p for p in PAINTINGS if p["zone"] == zone]
    if exclude_id is not None and len(candidates) > 1:
        candidates = [p for p in candidates if p["id"] != exclude_id]
    return random.choice(candidates)


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

    zone_counts = Counter(e["zone"] for e in recent)
    dominant_zone = zone_counts.most_common(1)[0][0]

    painting = pick_painting(dominant_zone)

    db.record_weekly_reward(telegram_id, dominant_zone, painting["id"])
    return painting
