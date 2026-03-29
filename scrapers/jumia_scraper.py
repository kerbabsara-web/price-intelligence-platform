import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# 🔹 Filtre smartphones
def is_phone(name):
    name = name.lower()

    keywords = ["samsung", "iphone", "galaxy"]
    excluded = [
        "tv", "télé", "ecouteur", "écouteur",
        "chargeur", "cable", "coque",
        "carte", "memory", "adaptateur"
    ]

    if any(word in name for word in excluded):
        return False

    return any(keyword in name for keyword in keywords)

# 🔹 Nettoyage prix
def clean_price(price):
    return float(price.replace("Dhs", "").replace(",", "").strip())

# 🔹 Nettoyage nom
def clean_name(name):
    return name.replace("\n", "").strip()

# 🔹 Scraper Jumia
def scrape_jumia(keyword):
    headers = {"User-Agent": "Mozilla/5.0"}
    data = []

    for page in range(1, 4):
        url = f"https://www.jumia.ma/catalog/?q={keyword}&page={page}"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "lxml")

        products = soup.find_all("article", class_="prd")

        for product in products:
            try:
                name = clean_name(product.find("h3").text)

                if not is_phone(name):
                    continue

                price = clean_price(product.find("div", class_="prc").text)

                data.append({
                    "name": name,
                    "price": price,
                    "platform": "jumia",
                    "timestamp": datetime.now().isoformat()
                })

            except:
                continue

    return data

# 🔹 Supprimer doublons
def remove_duplicates(data):
    unique = []
    seen = set()

    for item in data:
        key = (item["name"], item["price"])
        if key not in seen:
            unique.append(item)
            seen.add(key)

    return unique

# 🔹 MAIN
if __name__ == "__main__":
    results = []

    print("🔄 Scraping Samsung Jumia...")
    results += scrape_jumia("samsung")

    print("🔄 Scraping iPhone Jumia...")
    results += scrape_jumia("iphone")

    results = remove_duplicates(results)

    print(f"📊 Produits Jumia : {len(results)}")

    with open("../data/jumia.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print("✅ Jumia terminé !")