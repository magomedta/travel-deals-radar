import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import requests
import re
import html
import xml.etree.ElementTree as ET
import logging
from config import TRAVELPAYOUTS_MARKER

FEED_URL = "https://travelbelka.ru/feed/"

def clean_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    text = re.sub(r'<[^>]+>', ' ', raw_html)
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def fetch_travelbelka_deals():
    """
    Scrapes hot package tours, hotel drops and charter flights from Travelbelka.
    """
    deals = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        resp = requests.get(FEED_URL, headers=headers, timeout=12)
        if resp.status_code != 200:
            return []

        root = ET.fromstring(resp.content)
        items = root.findall(".//item")

        for item in items:
            title_elem = item.find("title")
            link_elem = item.find("link")
            guid_elem = item.find("guid")
            desc_elem = item.find("description")
            content_elem = item.find("{http://purl.org/rss/1.0/modules/content/}encoded")

            title = title_elem.text.strip() if title_elem is not None and title_elem.text else "Горящий тур"
            link = link_elem.text.strip() if link_elem is not None and link_elem.text else ""
            deal_id = guid_elem.text.strip() if guid_elem is not None and guid_elem.text else link

            content_text = content_elem.text if content_elem is not None and content_elem.text else ""
            desc_text = desc_elem.text if desc_elem is not None and desc_elem.text else ""

            # Extract first real photo (skip emojis and avatars)
            image_url = ""
            img_matches = re.findall(r'https://[^\s"\'<>]+\.(?:jpg|jpeg|png|webp)', content_text or desc_text)
            real_imgs = [img for img in img_matches if 'emoji' not in img.lower() and 's.w.org' not in img.lower() and 'avatar' not in img.lower()]
            if real_imgs:
                image_url = real_imgs[0]

            clean_summary = clean_html(desc_text or content_text)
            if len(clean_summary) > 280:
                clean_summary = clean_summary[:277] + "..."

            partner_url = f"https://www.aviasales.ru/?marker={TRAVELPAYOUTS_MARKER}"
            hotel_url = f"https://ostrovok.ru/?marker={TRAVELPAYOUTS_MARKER}"

            deals.append({
                "id": deal_id,
                "title": title,
                "summary": clean_summary,
                "url": link,
                "aviasales_url": partner_url,
                "hotel_url": hotel_url,
                "image": image_url,
                "source": "Travelbelka",
                "deal_type": "tour"
            })

    except Exception as e:
        logging.error(f"[Travelbelka] Fetch error: {e}")

    return deals

if __name__ == "__main__":
    results = fetch_travelbelka_deals()
    print(f"Fetched {len(results)} deals from Travelbelka:")
    for d in results[:3]:
        print("=" * 50)
        print("TITLE:", d["title"])
        print("IMAGE:", d["image"])
