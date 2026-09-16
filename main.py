import os
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

# ከ Render Environment Variables የሚወስደው የቴሌግራም ቶከን
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

@app.route('/')
def home():
    return "Bravo Bingo Bot and Mini App is running successfully!"

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    # ቴሌግራም የሚልካቸውን መልዕክቶች መቀበያ
    update = request.get_json()
    if update:
        chat_id = None
        text = ""
        
        # ከተለመዱት መልዕክቶች (Message) ወይም (Callback Query) ቻት አይዲ ማግኘት
        if "message" in update:
            chat_id = update["message"]["chat"]["id"]
            text = update["message"].get("text", "")
        elif "callback_query" in update:
            chat_id = update["callback_query"]["message"]["chat"]["id"]
            text = update["callback_query"].get("data", "")
            
        # /start ሲሉ ቦቱ መልስ እንዲሰጥ
        if chat_id and text == "/start":
            send_message(chat_id, "ሰላም! እንኳን ወደ 🌟 እናቴ ቢንጎ (Bravo Bingo) 🌟 በደህና መጡ! የሚኒ አፑን በመክፈት መጫወት ይችላሉ።")
            
    return "OK", 200

def send_message(chat_id, text):
    if TELEGRAM_TOKEN:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text
        }
        try:
            requests.post(url, json=payload)
        except Exception as e:
            print(f"Error sending message: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

