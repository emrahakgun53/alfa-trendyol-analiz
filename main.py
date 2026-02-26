from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import requests
import base64
import pandas as pd

app = FastAPI()

import os

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
SUPPLIER_ID = os.getenv("SUPPLIER_ID")

def trendyol_urunleri():
    auth = base64.b64encode(f"{API_KEY}:{API_SECRET}".encode()).decode()

    headers = {
        "Authorization": "Basic " + auth,
        "Content-Type": "application/json"
    }

    url = f"https://api.trendyol.com/sapigw/suppliers/{SUPPLIER_ID}/products"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()["content"]
    else:
        return []

@app.get("/", response_class=HTMLResponse)
def panel():
    urunler = trendyol_urunleri()

    if not urunler:
        return "<h3>API bilgilerini girmediniz veya veri çekilemedi.</h3>"

    df = pd.DataFrame(urunler)
    df = df[["title", "salePrice", "quantity", "categoryName"]]

    kategori_ort = df.groupby("categoryName")["salePrice"].mean().reset_index()
    kategori_ort.columns = ["categoryName", "kategori_ort"]

    df = df.merge(kategori_ort, on="categoryName")

    def durum(row):
        if row["salePrice"] < row["kategori_ort"] * 0.95:
            return "Ucuz"
        elif row["salePrice"] > row["kategori_ort"] * 1.05:
            return "Pahalı"
        else:
            return "Normal"

    df["Durum"] = df.apply(durum, axis=1)

    return df.to_html(index=False)
