from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import requests
import base64
import os
import pandas as pd
import io

app = FastAPI()

def get_api_data():
    API_KEY = os.getenv("API_KEY")
    API_SECRET = os.getenv("API_SECRET")
    SUPPLIER_ID = os.getenv("SUPPLIER_ID")
    if not all([API_KEY, API_SECRET, SUPPLIER_ID]): return None, "Eksik Bilgi"
    auth = base64.b64encode(f"{API_KEY}:{API_SECRET}".encode()).decode()
    headers = {"Authorization": "Basic " + auth}
    url = f"https://api.trendyol.com/sapigw/suppliers/{SUPPLIER_ID}/products"
    try:
        res = requests.get(url, headers=headers, timeout=10)
        return (res.json().get("content", []), None) if res.status_code == 200 else (None, f"Hata: {res.status_code}")
    except: return None, "Bağlantı Sorunu"

@app.get("/", response_class=HTMLResponse)
async def ana_sayfa():
    return """
    <html><head><link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css'></head>
    <body class='container mt-5'><h2>Alfa Trendyol Analiz</h2>
    <div class='card p-4 mb-4'><h5>Excel Dosyası Yükle</h5>
    <form action='/upload' method='post' enctype='multipart/form-data'>
    <input type='file' name='file' class='form-control mb-2' accept='.xlsx'><button type='submit' class='btn btn-success'>Analiz Et</button>
    </form></div></body></html>
    """

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        # Sütun isimlerini kontrol etmeden sadece tabloyu gösterelim (Hata riskini sıfırlamak için)
        html_tablo = df.to_html(classes="table table-sm table-bordered", index=False)
        return HTMLResponse(content=f"<html><body class='container mt-5'><h3>Yüklenen Veriler</h3>{html_tablo}<br><a href='/'>Geri Dön</a></body></html>")
    except Exception as e:
        return f"Hata Oluştu: {str(e)}"
