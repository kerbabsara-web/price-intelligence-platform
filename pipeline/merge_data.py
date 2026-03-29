import undetected_chromedriver as uc
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import json
import time
from datetime import datetime
import re

# ---------------------------------------------------------
# 🔹 CONFIGURATION ET FILTRES COMMUNS
# ---------------------------------------------------------
def is_phone(name):
    name = name.lower().strip()
    brands = ["samsung", "iphone", "xiaomi", "redmi", "galaxy", "huawei", "oppo", "pixel", "apple"]
    blacklist = ["coque", "étui", "case", "protection", "verre", "câble", "cable", "chargeur", "adaptateur", "support", "ecouteur", "buds", "watch", "tv", "télé"]
    
    has_brand = any(b in name for b in brands)
    is_acc = any(a in name for a in blacklist)
    return has_brand and not is_acc

def clean_price(price_text):
    if not price_text: return None
    clean = "".join(filter(str.isdigit, price_text))
    try:
        return float(clean)
    except:
        return None

# ---------------------------------------------------------
# 🔹 SCRAPER JUMIA (via Requests)
# ---------------------------------------------------------
def scrape_jumia(keyword):
    print(f"🔄 Jumia : Scraping {keyword}...")
    headers = {"User-Agent": "Mozilla/5.0"}
    data = []

    for page in range(1, 3): # On limite à 2 pages pour l'exemple
        url = f"https://www.jumia.ma/catalog/?q={keyword}&page={page}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "lxml")
            products = soup.find_all("article", class_="prd")

            for product in products:
                name = product.find("h3", class_="name").text.strip() if product.find("h3", class_="name") else ""
                if not is_phone(name): continue

                price_raw = product.find("div", class_="prc").text if product.find("div", class_="prc") else ""
                price = clean_price(price_raw)

                if price:
                    data.append({
                        "name": name,
                        "price": price,
                        "platform": "jumia",
                        "timestamp": datetime.now().isoformat()
                    })
        except Exception as e:
            print(f"⚠️ Erreur Jumia : {e}")
    return data

# ---------------------------------------------------------
# 🔹 SCRAPER ELECTROPLANET (via Selenium UC)
# ---------------------------------------------------------
def scrape_electroplanet(keyword):
    print(f"🔄 Electroplanet : Scraping {keyword}...")
    options = uc.ChromeOptions()
    options.add_argument('--log-level=3')
    
    results = []
    try:
        with uc.Chrome(options=options, version_main=146) as driver:
            driver.get(f"https://www.electroplanet.ma/catalogsearch/result/?q={keyword}")
            time.sleep(10) # Attente Cloudflare

            items = driver.find_elements(By.CSS_SELECTOR, "li.product-item")
            for item in items:
                try:
                    name = item.find_element(By.CSS_SELECTOR, "a.product-item-link").get_attribute("textContent").strip()
                    if not is_phone(name): continue
                    
                    price_raw = item.find_element(By.CSS_SELECTOR, "span.price").get_attribute("textContent")
                    price = clean_price(price_raw)

                    if price:
                        results.append({
                            "name": name,
                            "price": price,
                            "platform": "electroplanet",
                            "timestamp": datetime.now().isoformat()
                        })
                except:
                    continue
    except Exception as e:
        print(f"⚠️ Erreur Electroplanet : {e}")
    return results

# ---------------------------------------------------------
# 🔹 LOGIQUE DE FUSION ET NETTOYAGE
# ---------------------------------------------------------
def remove_duplicates(data):
    unique = []
    seen = set()
    for item in data:
        # On crée une clé unique basée sur le nom et le prix
        key = (item["name"].lower(), item["price"])
        if key not in seen:
            unique.append(item)
            seen.add(key)
    return unique

# ---------------------------------------------------------
# 🔹 EXECUTION
# ---------------------------------------------------------
if __name__ == "__main__":
    all_data = []
    search_terms = ["samsung", "iphone"]

    for term in search_terms:
        # 1. Récupère Jumia
        jumia_res = scrape_jumia(term)
        all_data.extend(jumia_res)
        
        # 2. Récupère Electroplanet
        electro_res = scrape_electroplanet(term)
        all_data.extend(electro_res)
        
        time.sleep(2)

    # Nettoyage
    final_data = remove_duplicates(all_data)
    
    # Tri par prix croissant
    final_data = sorted(final_data, key=lambda x: x['price'])

    # Sauvegarde finale
    with open("all_products.json", "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)

    print(f"\n✅ TERMINÉ !")
    print(f"📊 Total des produits uniques fusionnés : {len(final_data)}")
    print(f"📂 Fichier créé : all_products.json")