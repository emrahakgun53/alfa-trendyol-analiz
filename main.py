from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import pandas as pd
import io

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def ana_sayfa():
    return """
    <html><head>
    <link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css'>
    <style>body{background:#f8f9fa} .card{border-radius:15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1)}</style>
    </head>
    <body class='container mt-5'>
    <div class='card p-5 text-center'>
        <h2 class='mb-4 text-primary'>🚀 Alfa Trendyol Akıllı Analiz</h2>
        <p class='text-muted'>Trendyol'dan indirdiğiniz Excel dosyasını seçin.</p>
        <form action='/upload' method='post' enctype='multipart/form-data' class='mt-3'>
            <input type='file' name='file' class='form-control mb-3' accept='.xlsx, .xls'>
            <button type='submit' class='btn btn-lg btn-primary w-100'>Analiz Et ve Sonuçları Gör</button>
        </form>
    </div>
    </body></html>
    """

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # Trendyol Excel sütunlarını tahmin etmeye çalışalım
        # Eğer sütun adları farklıysa burayı Excel'e göre düzeltebiliriz
        sutunlar = df.columns.tolist()
        
        # Örnek Analiz: Fiyat sütununu bul ve ortalama al
        # Not: Excel'indeki sütun isimlerine göre burası otomatik şekillenir
        html_tablo = df.to_html(classes="
