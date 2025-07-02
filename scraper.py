import requests
import csv
import time
from bs4 import BeautifulSoup

BASE_URL = "https://semerkandonline.com"
COLLECTION_URL = f"{BASE_URL}/collections/bucher-1/products.json"

def get_all_products():
    products = []
    page = 1
    while page<=1:
        print(f"🔄 Lade Seite {page}")
        res = requests.get(f"{COLLECTION_URL}?page={page}")
        if res.status_code != 200:
            break
        data = res.json()
        new_products = data.get("products", [])
        if not new_products:
            break
        products.extend(new_products)
        page += 1
        time.sleep(1)
    return products

def get_detailed_fields(product_url):
    res = requests.get(product_url)
    soup = BeautifulSoup(res.text, "html.parser")

    def sel_text(selector):
        el = soup.select_one(selector)
        return el.get_text(strip=True) if el else ""

    # Key-Value-Infos wie Autor, Einband, Seitenanzahl, Abmessung, ISBN
    info = {}
    for p in soup.select("p.custom-metafield"):
        text = p.get_text(strip=True)
        if ":" in text:
            key, val = text.split(":", 1)
            info[key.strip().lower()] = val.strip()

    return {
        "author": info.get("autor", ""),
        "pages": info.get("seitenanzahl", ""),
        "format": info.get("einband", ""),
        "dimensions": info.get("abmessung", ""),
        "isbn": sel_text("div.productView-barcode"),
        "sku": sel_text("div.productView-sku"),
    }

def convert_product(product):
    variants = product.get("variants", [])
    price = variants[0]["price"] if variants else ""
    handle = product.get("handle", "")
    url = BASE_URL + "/products/" + handle

    base = {
        "title": product.get("title", ""),
        "description": product.get("body_html", ""),
        "product_type": product.get("product_type", ""),
        "tags": ", ".join(product.get("tags", [])),
        "vendor": product.get("vendor", ""),
        "price": price,
        "url": url,
    }

    # Detaildaten hinzufügen
    try:
        details = get_detailed_fields(url)
    except Exception as e:
        print(f"⚠️ Fehler beim Detailabruf: {url} ({e})")
        details = {
            "author": "", "pages": "", "format": "",
            "dimensions": "", "isbn": "", "sku": ""
        }

    base.update(details)
    return base

if __name__ == "__main__":
    all_products = get_all_products()
    print(f"📦 Gesamtanzahl Produkte: {len(all_products)}")

    books = []
    for i, product in enumerate(all_products, 1):
        print(f"🔍 Verarbeite [{i}/{len(all_products)}]: {product.get('title')}")
        books.append(convert_product(product))
        time.sleep(0.5)

    if books:
        with open("books_detailed.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=books[0].keys())
            writer.writeheader()
            writer.writerows(books)
        print("✅ CSV gespeichert: books_detailed.csv")
    else:
        print("⚠️ Keine Bücher gespeichert.")
