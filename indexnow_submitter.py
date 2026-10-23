import requests
import json

KEY = "8f4b23d91e604f849c71629851726a9c"
HOST = "magomedta.github.io"
KEY_LOCATION = f"https://{HOST}/travel-deals-radar/{KEY}.txt"

URL_LIST = [
    f"https://{HOST}/travel-deals-radar/",
    f"https://{HOST}/travel-deals-radar/feed.json",
    f"https://{HOST}/travel-deals-radar/sitemap.xml"
]

def submit_indexnow():
    payload = {
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": URL_LIST
    }
    
    headers = {"Content-Type": "application/json; charset=utf-8"}
    
    # Ping Yandex IndexNow
    try:
        r_yandex = requests.post("https://yandex.com/indexnow", json=payload, headers=headers, timeout=10)
        print("Yandex IndexNow status:", r_yandex.status_code)
    except Exception as e:
        print("Yandex IndexNow error:", e)

    # Ping Bing / IndexNow.org
    try:
        r_indexnow = requests.post("https://api.indexnow.org/indexnow", json=payload, headers=headers, timeout=10)
        print("IndexNow.org status:", r_indexnow.status_code)
    except Exception as e:
        print("IndexNow error:", e)

if __name__ == "__main__":
    submit_indexnow()
