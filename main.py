from fastapi import FastAPI, UploadFile, File, Form
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
    
    if not all([API_KEY, API_SECRET, SUPPLIER_ID]):
        return None, "API Bilgileri Eksik"

    auth = base64.b64encode(f"{API_KEY}:{API_SECRET}".encode()).decode()
    headers = {"Authorization": "Basic " + auth}
    url = f"https://api.trendyol.com/sapigw/suppliers/{SUPPLIER_ID}/products"
    
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return res.json()["content"], None
        else:
            return None, f"Trendyol API Hatası (Kod: {res.status_code})"
    except:
        return None, "Bağlantı Hatası"

def analiz_et(df):
    # Temel analiz mantığı
    df = df[["title", "salePrice", "quantity", "categoryName"]].copy()
    kat_ort = df.groupby("categoryName")["salePrice"].mean().reset_index()
    kat_ort.columns = ["categoryName", "kat_ort"]
    df = df.merge(kat_ort, on="categoryName")
    
    def durum(row):
        if row["salePrice"] < row["kat_ort"] * 0.95: return "🟢 Ucuz (Fırsat)"
        elif row["salePrice"] > row["kat_ort"] * 1.05: return "🔴 Pahalı"
        return "🟡 Normal"
    
    df["Analiz"] = df.apply(durum, axis=1)
    return df.to_html(classes="table table-striped", index=False)

@app.get("/", response_class=HTMLResponse)
async def ana_sayfa():
    urunler, hata = get_api_data()
    
    content = """
    <html>
        <head><link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css'></head>
        <body class='container mt-5'>
            <h2 class='mb-4'>Alfa Trendyol Analiz Paneli</h2>
    """
    
    if urunler:
        content += "<h4>✅ API Aktif: Canlı Veriler</h4>"
        content += analiz_et(pd.DataFrame(urunler))
    else:
        content += f"""
        <div class='alert alert-warning'>
            <strong>API Bağlantısı Kurulamadı:</strong> {hata}<br>
            Şu an Trendyol onay vermediği için manuel devam edebilirsiniz.
        </div>
        <div class='card p-4'>
            <h5>Excel ile Analiz Yap</h5>
            <form action='/upload' method='post' enctype='multipart/form-data'>
                <input type='file' name='file' class='form-control mb-3' accept='.xlsx, .xls'>
                <button type='submit' class='btn btn-primary'>Yükle ve Analiz Et</button>
            </form>
        </div>
        """
    content += "</body></html>"
    return content

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_excel(io.BytesIO(contents))
    return HTMLResponse(content=f"<html><body class='container mt-5'><h2>Excel Sonuçları</h2>{analiz_et(df)}<br><a href='/'>Geri Dön</a></body></html>")
