import requests
import json
import logging
import urllib.parse
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, TRAVELPAYOUTS_MARKER

def format_travel_post(deal: dict) -> str:
    """Formats high-converting travel alert for Russian market."""
    title = deal.get("title", "Горящий билет")
    summary = deal.get("summary", "")
    source = deal.get("source", "Авиасейлс")
    deal_type = deal.get("deal_type", "flight")

    if deal_type == "train":
        header = "🚆 <b>ГОРЯЩИЙ ЖД БИЛЕТ / АКЦИЯ РЖД</b>"
        status_note = "⏳ <i>Статус: АКТУАЛЬНО (Места на Сапсаны/купе быстро разбирают!)</i>"
    elif deal_type == "tour":
        header = "🏖️ <b>ГОРЯЩИЙ ТУР / СПЕЦПРЕДЛОЖЕНИЕ</b>"
        status_note = "⏳ <i>Статус: АКТУАЛЬНО (Горящие туры раскупают за минуты!)</i>"
    else:
        header = "✈️ <b>ГОРЯЩИЙ АВИАБИЛЕТ / ОШИБКА ТАРИФА</b>"
        status_note = "⏳ <i>Статус: АКТУАЛЬНО (Билеты по промо-ценам быстро разбирают!)</i>"

    post = (
        f"{header}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 <b>{title}</b>\n\n"
        f"{summary}\n\n"
        f"{status_note}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔎 <i>Источник данных: {source}</i>\n"
        f"🔔 <i>Включите уведомления, чтобы первыми успевать на раздачи!</i>"
    )
    return post

def publish_travel_deal(deal: dict) -> bool:
    """Dispatches travel deal to designated Russian Telegram channel."""
    title = deal.get("title", "Горящий билет")
    deal_type = deal.get("deal_type", "flight")

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        print(f"\n[DEMO TRAVEL ALERT ({deal_type.upper()})] Would post: {title}")
        return True

    text = format_travel_post(deal)
    image_url = deal.get("image")

    share_text = urllib.parse.quote(f"🔥 Горящий билет / скидка: {title}! Успей забрать:")
    share_url = f"https://t.me/share/url?url=https://t.me/{TELEGRAM_CHANNEL_ID.replace('@', '')}&text={share_text}"

    if deal_type == "train":
        inline_keyboard = {
            "inline_keyboard": [
                [
                    {"text": "🚆 Купить ЖД билет (Яндекс Путешествия)", "url": deal.get("train_url", f"https://travel.yandex.ru/trains/?utm_source=partner&marker={TRAVELPAYOUTS_MARKER}")}
                ],
                [
                    {"text": "🎫 Билеты на поезд (Туту.ру)", "url": deal.get("tutu_url", f"https://www.tutu.ru/poezda/?marker={TRAVELPAYOUTS_MARKER}")}
                ],
                [
                    {"text": "📢 Переслать попутчику", "url": share_url}
                ]
            ]
        }
    elif deal_type == "tour":
        inline_keyboard = {
            "inline_keyboard": [
                [
                    {"text": "🏖️ Забронировать тур/отель (Островок)", "url": deal.get("hotel_url", f"https://ostrovok.ru/?marker={TRAVELPAYOUTS_MARKER}")}
                ],
                [
                    {"text": "✈️ Подобрать перелет (Aviasales)", "url": deal.get("aviasales_url", f"https://www.aviasales.ru/?marker={TRAVELPAYOUTS_MARKER}")}
                ],
                [
                    {"text": "📢 Переслать попутчику", "url": share_url}
                ]
            ]
        }
    else:
        inline_keyboard = {
            "inline_keyboard": [
                [
                    {"text": "✈️ Купить билет на Aviasales", "url": deal.get("aviasales_url", f"https://www.aviasales.ru/?marker={TRAVELPAYOUTS_MARKER}")}
                ],
                [
                    {"text": "🏨 Отели со скидкой (Травелата)", "url": deal.get("hotel_url", f"https://travelata.ru/?utm_source=partner&marker={TRAVELPAYOUTS_MARKER}")}
                ],
                [
                    {"text": "📢 Переслать попутчику", "url": share_url}
                ]
            ]
        }

    # 1. Try sendPhoto by downloading bytes directly (avoids Telegram URL download blocking)
    posted = False
    if image_url:
        try:
            img_req = requests.get(image_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
            if img_req.status_code == 200 and len(img_req.content) > 1000:
                photo_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
                data = {
                    "chat_id": TELEGRAM_CHANNEL_ID,
                    "caption": text,
                    "parse_mode": "HTML",
                    "reply_markup": json.dumps(inline_keyboard)
                }
                files = {
                    "photo": ("cover.jpg", img_req.content, "image/jpeg")
                }
                resp = requests.post(photo_url, data=data, files=files, timeout=15)
                if resp.status_code == 200 and resp.json().get("ok"):
                    posted = True
                else:
                    logging.warning(f"[Travel Photo] sendPhoto upload failed: {resp.text[:100]}")
        except Exception as e:
            logging.warning(f"[Travel Photo] Exception fetching image: {e}")

    # 2. Fallback to sendMessage if photo upload failed
    if not posted:
        msg_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHANNEL_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
            "reply_markup": json.dumps(inline_keyboard)
        }
        try:
            resp = requests.post(msg_url, json=payload, timeout=10)
            if resp.status_code == 200 and resp.json().get("ok"):
                posted = True
            else:
                logging.error(f"[Travel] sendMessage error: {resp.text}")
        except Exception as e:
            logging.error(f"[Travel] Exception: {e}")

    return posted
