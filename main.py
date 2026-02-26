from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import pandas as pd
import io

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def ana_sayfa():
return """
<html><head><link rel='stylesheet' href=''></head>
<body class='container mt-5 text-center'>
<div class='card p-5 shadow-sm'>
<h2 class='text-primary mb-4'>Alfa Trendyol Analiz 🚀</h2>
<form action='/upload' method='post' enctype='multipart/form-data'>
<input type='file' name='file' class='form-control mb-3' accept='.xlsx, .xls'>
<button type='submit' class='btn btn-lg btn-warning w-100'>Şimdi Analiz Et</button>
</form>
</div>
</body></html>
"""

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
try:
contents = await file.read()
df = pd.read_excel(io.BytesIO(contents))
html_tablo = df.to_html(classes="table table-striped mt-4", index=False)
return HTMLResponse(content=f"<html><body class='p-5'><h3>Veri Başarıyla Yüklendi</h3><a href='/'>Geri Dön</a>{html_tablo}</body></html>")
except Exception as e:
return HTMLResponse(content=f"<html><body><h3>Hata: {str(e)}</h3><p>Excel dosyasinin formatini kontrol edin.</p><a href='/'>Geri Dön</a></body></html>")
