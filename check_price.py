import requests
import os

# Настройки
NM_ID = 438382874  # ID товара на Wildberries
TARGET_PRICE = 22000  # Целевая цена в рублях
BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

def get_price():
    """Получаем текущую цену товара на WB"""
    url = "https://card.wb.ru/cards/v2/detail"
    params = {
        "appType": 1,
        "curr": "rub",
        "dest": -1257786,
        "spp": 30,
        "nm": NM_ID,
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        prod = r.json()["products"][0]
        
        # Цена в копейках, делим на 100
        for size in prod.get("sizes", []):
            price = size.get("price", {}).get("total")
            if price:
                return price / 100
        
        return prod.get("salePriceU", 0) / 100
    except Exception as e:
        print(f"Ошибка: {e}")
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
