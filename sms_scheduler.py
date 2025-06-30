from flask import Flask
import schedule
import time
import threading
import requests
from datetime import datetime
from bs4 import BeautifulSoup

app = Flask(__name__)

# 🚨 Fast2SMS API Key (keep this safe!)
FAST2SMS_API_KEY = "WxVtBRKApjuiNZMwomHGv1kCUl9cfOnhX8a6yY4dIJ7PTQ2zDEiA80nLbq9TFOm5WoNt6JMUKX2HGY3s"
MOBILE_NUMBERS = "9999999999"  # <-- Replace with your actual comma-separated numbers

def fetch_gita_quote():
    try:
        res = requests.get("https://www.holy-bhagavad-gita.org/chapter/2/verse/47", timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        quote_elem = soup.select_one('.verse__translation-text')
        return quote_elem.text.strip() if quote_elem else "Perform your duty without attachment to results. – Gita 2.47"
    except:
        return "Perform your duty without attachment to results. – Gita 2.47"

def days_left():
    return (datetime(2026, 1, 1) - datetime.now()).days

def send_sms(time_of_day):
    quote = fetch_gita_quote()
    dleft = days_left()

    if time_of_day == "morning":
        message = (
            f"🌅 Good Morning!\n"
            f"{quote}\n\n"
            f"🔔 Stay focused. Each small effort counts.\n"
            f"📅 {dleft} days to Jan 2026. Let’s win this journey!"
        )
    else:  # evening
        message = (
            f"🌙 Good Night!\n"
            f"{quote}\n\n"
            f"📘 Reflect on your progress today.\n"
            f"📅 {dleft} days left to Jan 2026. Rest well, rise stronger."
        )

    payload = {
        "authorization": FAST2SMS_API_KEY,
        "message": message,
        "language": "english",
        "route": "q",
        "numbers": MOBILE_NUMBERS,
    }

    try:
        response = requests.post("https://www.fast2sms.com/dev/bulkV2", data=payload)
        print(f"[{datetime.now()}] SMS sent ({time_of_day}). Response: {response.text}")
    except Exception as e:
        print(f"[{datetime.now()}] SMS failed ({time_of_day}):", e)

def schedule_sms():
    schedule.every().day.at("08:00").do(send_sms, time_of_day="morning")
    schedule.every().day.at("21:00").do(send_sms, time_of_day="evening")
    while True:
        schedule.run_pending()
        time.sleep(60)

@app.route('/')
def home():
    return f"✅ SMS Scheduler Running — {days_left()} days left to Jan 2026."

if __name__ == '__main__':
    threading.Thread(target=schedule_sms).start()
    app.run(host="0.0.0.0", port=5000)