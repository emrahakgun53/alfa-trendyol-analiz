from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import pandas as pd
import io

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def ana_sayfa():
return """
<html><head>
<link rel='stylesheet' href=''>
<style>
body{background: #f4f7f6; font-family: 'Segoe UI', sans-serif;}
.upload-card {background: white; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); padding: 40px; margin-top: 50px;}
.btn-trendyol {background: #f27a1a; color: white; border: none; padding: 12px; font-weight: bold; width: 100%; border-radius: 10px;}
.btn-trendyol:hover {background: #e66e00; color: white;}
</style>
</head>
<body>
<div class='container'>
<div class='row justify-content-center'>
<div class='col-md-6 upload-card text-center'>
<h2 class='text-primary mb-4'>Alfa Analiz Paneli 🚀</h2>
<p class='text-muted text-start'>1. Trendyol panelinden ürün listesini indirin.


2. Buraya yükleyip 'Analizi Başlat' deyin.</p>
<form action='/upload' method='post' enctype='multipart/form-data'>
<input type='file' name='file' class='form-control mb-3' accept='.xlsx, .xls'>
<button type='submit' class='btn btn-trendyol'>Analizi Başlat</button>
</form>
</div>
</div>
</div>
</body></html>
"""

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
try:
contents = await file.read()
df = pd.read_excel(io.BytesIO(contents))
fiyat_col = [c for c in df.columns if 'Fiyat' in str(c) or 'Price' in str(c)][0]
kat_col = [c for c in df.columns if 'Kategori' in str(c) or 'Category' in str(c)][0]
ad_col = [c for c in df.columns if 'Ad' in str(c) or 'Title' in str(c)][0]
stok_col = [c for c in df.columns if 'Stok' in str(c) or 'Quantity' in str(c)][0]
df['Kategori_Ortalamasi'] = df.groupby(kat_col)[fiyat_col].transform('mean')
def durum_belirle(row):
fiyat = row[fiyat_col]
ort = row['Kategori_Ortalamasi']
if fiyat < ort * 0.90: return "<span class='badge bg-success'>FIRSAT (UCUZ)</span>"
if fiyat > ort * 1.10: return "<span class='badge bg-danger'>PAHALI (DÜZENLE)</span>"
return "<span class='badge bg-warning text-dark'>NORMAL</span>"
df['Analiz_Sonucu'] = df.apply(durum_belirle, axis=1)
sonuc_df = df[[ad_col, kat_col, stok_col, fiyat_col, 'Analiz_Sonucu']].copy()
html_tablo = sonuc_df.to_html(classes="table table-striped table-hover mt-4", index=False, escape=False)
return HTMLResponse(content=f"""
<html><head><link rel='stylesheet' href=''></head>
<body class='p-5 bg-light'>
<div class='container bg-white p-4 rounded shadow-sm'>
<div class='d-flex justify-content-between align-items-center mb-4'>
<h3>📊 Akıllı Fiyat Analiz Raporu</h3>
<a href='/' class='btn btn-outline-secondary'>Yeni Dosya Yükle</a>
</div>
<div class='table-responsive'>{html_tablo}</div>
</div>
</body></html>
""")
except Exception as e:
return f"<h3>Hata: Excel formatı uyumsuz.</h3><p>Detay: {str(e)}</p><a href='/'>Geri Dön</a>"
