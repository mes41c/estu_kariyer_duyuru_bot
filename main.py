import requests
from bs4 import BeautifulSoup
import os

# GitHub Secrets'tan alınacak hassas veriler
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
FILE_PATH = "last_announcement.txt"

# Hedef URL (Senin attığın HTML'in ait olduğu canlı sayfa)
TARGET_URL = "https://kariyer.eskisehir.edu.tr/tr/Duyuru"
BASE_URL = "https://kariyer.eskisehir.edu.tr"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram gönderme hatası: {e}")

def check_announcements():
    try:
        # Siteye istek at (User-Agent eklemek iyi bir pratiktir, bot sanılmasın diye)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(TARGET_URL, headers=headers)
        
        if response.status_code != 200:
            print("Siteye erişilemedi.")
            return

        soup = BeautifulSoup(response.content, 'html.parser')

        # Senin attığın HTML yapısına göre en son duyuruyu buluyoruz
        # Yapı: h3 class="gdlr-core-blog-title" -> a href="..."
        latest_item = soup.find('h3', class_='gdlr-core-blog-title')
        
        if not latest_item:
            print("Duyuru başlığı bulunamadı.")
            return

        link_tag = latest_item.find('a')
        title = link_tag.text.strip()
        link = link_tag['href']

        # Eğer link relative (göreceli) ise domaini başına ekle
        if not link.startswith("http"):
            full_link = BASE_URL + link
        else:
            full_link = link

        # En son kaydedilen duyuruyu oku
        last_seen_url = ""
        if os.path.exists(FILE_PATH):
            with open(FILE_PATH, "r", encoding="utf-8") as f:
                last_seen_url = f.read().strip()

        # Karşılaştırma yap
        if full_link != last_seen_url:
            print("Yeni duyuru bulundu!")
            message = f"📢 **Yeni ESTÜ Duyurusu!**\n\n🔹 {title}\n\n🔗 <a href='{full_link}'>Duyuruya Git</a>"
            send_telegram_message(message)

            # Yeni linki kaydet
            with open(FILE_PATH, "w", encoding="utf-8") as f:
                f.write(full_link)
        else:
            print("Yeni duyuru yok.")

    except Exception as e:
        print(f"Bir hata oluştu: {e}")

if __name__ == "__main__":
    check_announcements()