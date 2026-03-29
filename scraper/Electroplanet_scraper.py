import undetected_chromedriver as uc  # Crucial pour passer Cloudflare
from selenium.webdriver.common.by import By
import time
from datetime import datetime
import json
import re

# -------------------------------
# 🔹 Nettoyage du prix
# -------------------------------
def clean_price(price_text):
    if not price_text: 
        return None
    # On garde uniquement les chiffres (enlève "DH", les espaces, les virgules)
    clean = "".join(filter(str.isdigit, price_text))
    try:
        return float(clean)
    except:
        return None

# -------------------------------
# 🔹 Filtre intelligent (Smartphones uniquement)
# -------------------------------
def is_phone(name):
    name = name.lower().strip()
    # Marques cibles
    brands = ["samsung", "iphone", "xiaomi", "redmi", "galaxy", "huawei", "oppo", "pixel", "apple"]
    # Accessoires à filtrer pour éviter de polluer le JSON
    blacklist = ["coque", "étui", "case", "protection", "verre", "câble", "cable", "chargeur", "adaptateur", "support", "ecouteur", "buds", "watch"]
    
    has_brand = any(b in name for b in brands)
    is_acc = any(a in name for a in blacklist)
    
    return has_brand and not is_acc

# -------------------------------
# 🔹 Fonction de Scraping
# -------------------------------
def scrape_electroplanet(keyword):
    print(f"🔄 Scraping Electroplanet : {keyword}")
    
    options = uc.ChromeOptions()
    # On reste en mode "visible" pour faciliter le passage de Cloudflare
    
    try:
        # Le bloc 'with' gère l'ouverture et la fermeture propre du navigateur
        with uc.Chrome(options=options, version_main=146) as driver:
            driver.get(f"https://www.electroplanet.ma/catalogsearch/result/?q={keyword}")
            
            # Temps d'attente pour la vérification Cloudflare et le chargement JS
            time.sleep(10) 

            data = []
            # On cible les cartes produits
            items = driver.find_elements(By.CSS_SELECTOR, "li.product-item")
            print(f"🔍 Articles détectés sur la page : {len(items)}")

            for item in items:
                try:
                    # Extraction du nom (textContent est plus fiable que .text)
                    name_el = item.find_element(By.CSS_SELECTOR, "a.product-item-link")
                    name = name_el.get_attribute("textContent").strip()
                    
                    # Extraction du prix
                    price_el = item.find_element(By.CSS_SELECTOR, "span.price")
                    price_text = price_el.get_attribute("textContent")
                    price_val = clean_price(price_text)

                    # Si le prix est valide et que c'est bien un téléphone, on ajoute
                    if price_val and is_phone(name):
                        data.append({
                            "name": name,
                            "price": price_val,
                            "platform": "electroplanet",
                            "timestamp": datetime.now().isoformat()
                        })
                except:
                    continue
            
            print(f"✅ {len(data)} produits valides pour '{keyword}'")
            return data

    except Exception as e:
        print(f"⚠️ Erreur lors du scraping de {keyword}: {e}")
        return []

# -------------------------------
# 🔹 Exécution principale
# -------------------------------
if __name__ == "__main__":
    final_results = []
    
    # Liste des mots-clés à chercher
    search_terms = ["samsung", "iphone"]
    
    for term in search_terms:
        results = scrape_electroplanet(term)
        final_results.extend(results)
        time.sleep(2) # Pause de sécurité

    # --- OPTIONNEL : Trier par prix croissant ---
    final_results = sorted(final_results, key=lambda x: x['price'])

    print(f"\n📊 TOTAL FINAL : {len(final_results)} produits enregistrés.")

    # Sauvegarde finale dans le fichier JSON
    with open("electroplanet_products.json", "w", encoding="utf-8") as f:
        json.dump(final_results, f, ensure_ascii=False, indent=4)
        
    print("✅ Fichier 'electroplanet_products.json' mis à jour avec succès.")