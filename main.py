import time
import sys
import logging
from datetime import datetime
from colorama import init, Fore, Style

import database
from config import SCAN_INTERVAL_SECONDS, MAX_POSTS_PER_CYCLE, TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID
from scrapers.vandrouki import fetch_vandrouki_deals
from scrapers.travelbelka import fetch_travelbelka_deals
from scrapers.trains_rzd import fetch_train_deals
from publisher import publish_travel_deal

init(autoreset=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def print_banner():
    print(Fore.CYAN + Style.BRIGHT + """
 =======================================================
   ✈️🚆 АВТОНОМНЫЙ СКАНЕР АВИА / ЖД / ТУРОВ v1.0
   100% Автопилот | Российский рынок | Без участия человека
 =======================================================
    """ + Style.RESET_ALL)
    stats = database.get_stats()
    tg_status = Fore.GREEN + f"АКТИВЕН ({TELEGRAM_CHANNEL_ID})" if TELEGRAM_BOT_TOKEN else Fore.YELLOW + "РЕЖИМ ДЕМО (Укажите токен в .env для автопостинга в Telegram)"
    print(f"[*] Telegram канал:     {tg_status}")
    print(f"[*] База сделок:        {stats['total_deals']} предложений сохранено")
    print(f"[*] Частота проверки:   Каждые {SCAN_INTERVAL_SECONDS} секунд")
    print(Fore.CYAN + "-------------------------------------------------------\n")

def run_travel_scan_cycle():
    """Executes single scan across Vandrouki, Travelbelka and RZD Train feeds."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {Fore.BLUE}Сканирование рейсов, ЖД билетов (РЖД) и горящих туров...{Style.RESET_ALL}")

    v_deals = fetch_vandrouki_deals()
    b_deals = fetch_travelbelka_deals()
    t_deals = fetch_train_deals()
    all_deals = v_deals + b_deals + t_deals

    new_deals_count = 0

    for deal in all_deals:
        deal_id = deal.get("id")
        title = deal.get("title")
        source = deal.get("source")
        url = deal.get("url")

        if not database.is_deal_seen(deal_id, title=title):
            new_deals_count += 1
            database.save_deal(
                deal_id=deal_id,
                title=title,
                source=source,
                price="Горящий",
                url=url
            )

            # Publish to Telegram
            publish_travel_deal(deal)

            print(Fore.GREEN + Style.BRIGHT + " [НОВЫЙ БИЛЕТ] " + Style.RESET_ALL +
                  f"{Fore.YELLOW}{title}{Style.RESET_ALL} ({Fore.CYAN}{source}{Style.RESET_ALL})")

            time.sleep(3.0) # Safe pacing between posts

            if new_deals_count >= MAX_POSTS_PER_CYCLE:
                break

    if new_deals_count > 0:
        try:
            from feed_generator import generate_travel_feed
            generate_travel_feed()
        except Exception as e:
            logging.warning(f"Failed updating web feed: {e}")
    else:
        print(f"[{timestamp}] Все найденные предложения уже есть в базе. Мониторинг продолжается...")

    return new_deals_count

def main():
    print_banner()

    # Instant test mode
    if "--test" in sys.argv:
        print(Fore.YELLOW + "[*] Запуск в режиме мгновенного тестирования..." + Style.RESET_ALL)
        found = run_travel_scan_cycle()
        print(Fore.GREEN + f"\n[✔] Тест успешно завершен! Обработано новых сделок: {found}" + Style.RESET_ALL)
        return

    print(Fore.GREEN + "[*] Бот-сканер авиабилетов запущен 24/7. Нажмите Ctrl+C для остановки.\n" + Style.RESET_ALL)
    try:
        while True:
            run_travel_scan_cycle()
            time.sleep(SCAN_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n[*] Сканер остановлен пользователем." + Style.RESET_ALL)

if __name__ == "__main__":
    main()
