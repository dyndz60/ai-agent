import os
import requests
from flask import Flask, request, jsonify
import openai

app = Flask(__name__)

# جلب بيانات الاعتماد ومتغيرات البيئة
WHATSAPP_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "smart_agent_verify_token_123")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

@app.route("/", methods=["GET"])
def home():
    return "Global AI Sales Agent with Binance Pay & USDT is Live!"

# التحقق من الويب هوك الخاص بـ Meta
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
    return "Hello World", 200

# استقبال رسائل واتساب والرد عبر الذكاء الاصطناعي
@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.get_json()
    
    try:
        if data and "entry" in data:
            for entry in data["entry"]:
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    if "messages" in value:
                        message = value["messages"][0]
                        from_number = message["from"]
                        msg_body = message["text"]["body"]
                        
                        # توليد الرد باستخدام OpenAI GPT
                        ai_response = generate_ai_response(msg_body)
                        
                        # إرسال الرد عبر WhatsApp Cloud API
                        send_whatsapp_message(from_number, ai_response)
                        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"Error processing message: {e}")
        return jsonify({"status": "error"}), 200

def generate_ai_response(user_message):
    try:
        prompt = (
            "You are a professional, multilingual AI sales agent for B2B lead generation and order automation. "
            "You handle cross-border sales and payment collection via crypto-assets: "
            "Binance Pay (UID: 784156162) and USDT-TRC20 (Address: TMejUgCAzn9ZvjMvfhpzedPtpT9YDQpPMQ). "
            "Detect the user's language dynamically and respond in that same language. "
            "Be persuasive, helpful, and guide them to complete their purchase using the crypto payment methods provided. "
            f"User message: {user_message}"
        )
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return "Hello! Thank you for your interest. We are currently experiencing a brief technical issue, but please feel free to pay via Binance Pay (UID: 784156162) or USDT-TRC20 (Address: TMejUgCAzn9ZvjMvfhpzedPtpT9YDQpPMQ)."

def send_whatsapp_message(to_number, message_text):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message_text}
    }
    requests.post(url, headers=headers, json=payload)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
