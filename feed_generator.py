import os
import json
import sqlite3
from datetime import datetime
from scrapers.vandrouki import fetch_vandrouki_deals
from scrapers.travelbelka import fetch_travelbelka_deals
from scrapers.trains_rzd import fetch_train_deals

BASE_DIR = os.path.dirname(__file__)
FEED_PATH = os.path.join(BASE_DIR, "feed.json")

def generate_travel_feed():
    """
    Collects live deals across flights, trains, and hotels, and writes clean feed.json for the website.
    """
    deals = []
    seen_ids = set()

    # 1. Scrape live deals
    try:
        v_deals = fetch_vandrouki_deals()
        for d in v_deals:
            if d.get("id") not in seen_ids:
                seen_ids.add(d.get("id"))
                deals.append(d)
    except Exception as e:
        print(f"[Feed Gen] Vandrouki error: {e}")

    try:
        t_deals = fetch_train_deals()
        for d in t_deals:
            if d.get("id") not in seen_ids:
                seen_ids.add(d.get("id"))
                deals.append(d)
    except Exception as e:
        print(f"[Feed Gen] Trains error: {e}")

    try:
        b_deals = fetch_travelbelka_deals()
        for d in b_deals:
            if d.get("id") not in seen_ids:
                seen_ids.add(d.get("id"))
                deals.append(d)
    except Exception as e:
        print(f"[Feed Gen] Travelbelka error: {e}")

    # Format feed structure
    feed_data = {
        "updated_at": datetime.utcnow().isoformat(),
        "total_deals": len(deals),
        "deals": deals[:40]
    }

    with open(FEED_PATH, "w", encoding="utf-8") as f:
        json.dump(feed_data, f, ensure_ascii=False, indent=2)

    print(f"[Feed Gen] Successfully generated feed.json with {len(deals[:40])} deals.")
    return len(deals)

if __name__ == "__main__":
    generate_travel_feed()
