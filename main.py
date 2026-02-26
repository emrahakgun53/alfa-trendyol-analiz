from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
import base64
import os

app = FastAPI()

# Render'daki değişkenleri oku
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
SUPPLIER_ID = os.getenv("SUPPLIER_ID")

@app.get("/", response_class=HTMLResponse)
def debug_panel():
    # 1. Aşama: Değişkenler dolu mu?
    if not all([API_KEY, API_SECRET, SUPPLIER_ID]):
        return f"<h3>Hata: Değişkenler eksik!</h3><p>API_KEY: {'OK' if API_KEY else 'BOŞ'}<br>API_SECRET: {'OK' if API_SECRET else 'BOŞ'}<br>SUPPLIER_ID: {'OK' if SUPPLIER_ID else 'BOŞ'}</p>"

    # 2. Aşama: Trendyol'a bağlanmayı dene
    auth = base64.b64encode(f"{API_KEY}:{API_SECRET}".encode()).decode()
    headers = {"Authorization": "Basic " + auth, "Content-Type": "application/json"}
    url = f"https://api.trendyol.com/sapigw/suppliers/{SUPPLIER_ID}/products"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return "<h3>BAŞARILI! Veri geliyor.</h3><p>Şimdi ana kodu geri yükleyebiliriz.</p>"
        else:
            return f"<h3>Trendyol Reddediyor!</h3><p>Hata Kodu: {response.status_code}<br>Mesaj: {response.text}</p>"
    except Exception as e:
        return f"<h3>Bağlantı Hatası!</h3><p>{str(e)}</p>"
