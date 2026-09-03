import os
import requests
from flask import Flask, request, jsonify
import openai

app = Flask(__name__)

# جلب بيانات الاعتماد ومتغيرات البيئة
WHATSAPP_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "smart_support_bot_verify_token")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# إعداد مفتاح الذكاء الاصطناعي
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

@app.route("/", methods=["GET"])
def home():
    return "Global AI Sales Agent is live and running!", 200

# التحقق من الـ Webhook
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification failed", 403
    return "Webhook endpoint active.", 200

# استقبال رسائل العملاء من أي دولة والرد عليهم بالذكاء الاصطناعي وبنفس لغتهم
@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.get_json()
    print("Received data:", data)

    try:
        if "entry" in data and data["entry"]:
            changes = data["entry"][0].get("changes", [])
            if changes and "value" in changes[0]:
                value = changes[0]["value"]
                if "messages" in value:
                    message = value["messages"][0]
                    sender_phone = message["from"]
                    message_body = message.get("text", {}).get("body", "")

                    print(f"Message from {sender_phone}: {message_body}")

                    # توليد رد ذكي واحترافي عبر الذكاء الاصطناعي بناءً على لغة ونوع رسالة العميل
                    ai_reply = generate_ai_response(message_body)

                    # إرسال الرد للعميل عبر واتساب
                    send_whatsapp_message(sender_phone, ai_reply)

    except Exception as e:
        print(f"Error: {e}")

    return jsonify({"status": "success"}), 200

def generate_ai_response(user_message):
    if not OPENAI_API_KEY:
        return "Hello! Thank you for contacting us. How can we help you grow your business today?"

    try:
        # توجيه الذكاء الاصطناعي ليكون وكيل مبيعات محترف يرد بنفس لغة العميل ويعرض خدمات التشغيل الآلي والاشتراك
        prompt = (
            "You are an elite, persuasive global B2B sales agent for an AI automation agency. "
            "Your goal is to help local businesses (restaurants, stores, etc.) automate their customer support "
            "and WhatsApp orders to increase their revenue. "
            "Detect the language of the user's message and reply fluently in that exact same language. "
            "Be professional, concise, and encourage them to subscribe to our monthly automated service. "
            f"User message: {user_message}"
        )

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"OpenAI Error: {e}")
        return "Hello! We offer advanced AI automation solutions for your business. Would you like to know more about our monthly plans?"

def send_whatsapp_message(recipient_phone, text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_phone,
        "type": "text",
        "text": {"body": text},
    }

    response = requests.post(url, json=payload, headers=headers)
    print("WhatsApp send response:", response.json())

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
