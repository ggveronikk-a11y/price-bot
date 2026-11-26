import requests
import os

# Настройки
NM_ID = 438382874  # ID товара на Wildberries
TARGET_PRICE = 22000  # Целевая цена в рублях
BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

def get_price():
    """Получаем текущую цену товара на WB, пробуем несколько способов"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.wildberries.ru/",
        "Origin": "https://www.wildberries.ru",
    }

    # Список способов получить цену (от самого надёжного к запасным)
    attempts = [
        ("https://card.wb.ru/cards/v2/detail",
         {"appType": 1, "curr": "rub", "dest": -1257786, "spp": 30, "reg": 0, "lang": "ru", "for": 1, "nm": NM_ID}),
        ("https://card.wb.ru/cards/detail",
         {"appType": 1, "curr": "rub", "dest": -1257786, "spp": 30, "nm": NM_ID}),
    ]

    for url, params in attempts:
        try:
            r = requests.get(url, params=params, headers=headers, timeout=15)
            if r.status_code != 200:
                print(f"Статус {r.status_code} на {url}")
                continue
            data = r.json()
            products = data.get("products") or data.get("data", {}).get("products")
            if not products:
                continue
            prod = products[0]

            # Новый формат цены (копейки)
            for size in prod.get("sizes", []):
                price = size.get("price", {}).get("total")
                if price:
                    return price / 100

            # Старый формат цены
            price = prod.get("salePriceU") or prod.get("priceU")
            if price:
                return price / 100
        except Exception as e:
            print(f"Ошибка на {url}: {e}")
            continue

    print("Не удалось получить цену ни одним способом")
    return None

def send_telegram(text):
    """Отправляем сообщение в Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data, timeout=10)

def main():
    price = get_price()

    if price is None:
        send_telegram("⚠️ Бот не смог получить цену Sony Xperia 5 IV. Wildberries, возможно, блокирует запросы. Нужно менять способ получения цены.")
        print("Не удалось получить цену")
        return

    print(f"Текущая цена: {price} ₽")

    if price <= TARGET_PRICE:
        message = (
            f"🔥 <b>Цена упала!</b>\n\n"
            f"Товар: Sony Xperia 5 IV\n"
            f"Текущая цена: <b>{price:.0f} ₽</b>\n"
            f"Целевая цена: {TARGET_PRICE} ₽\n\n"
            f"Ссылка: https://www.wildberries.ru/catalog/{NM_ID}/detail.aspx"
        )
        send_telegram(message)
        print(f"✅ Уведомление отправлено! Цена {price} ₽")
    else:
        print(f"Цена {price} ₽ выше целевой {TARGET_PRICE} ₽")

if __name__ == "__main__":
    main()
