from fastapi import FastAPI, Request
import requests

app = FastAPI()

OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
WHATSAPP_TOKEN = "YOUR_WHATSAPP_TOKEN"

@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()
    
    try:
        message = data['entry'][0]['changes'][0]['value']['messages'][0]
        user_text = message['text']['body']
        sender_id = message['from']
        
        ai_response = ask_ai(user_text)
        send_whatsapp(sender_id, ai_response)
    except Exception as e:
        pass
        
    return {"status": "success"}

def ask_ai(prompt):
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "أنت مساعد مبيعات للمتجر، أجب باختصار ولطف."},
            {"role": "user", "content": prompt}
        ]
    }
    res = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
    return res.json()['choices'][0]['message']['content']

def send_whatsapp(to, text):
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    requests.post("https://graph.facebook.com/v18.0/YOUR_PHONE_NUMBER_ID/messages", json=payload, headers=headers)
  
