import json
import re
import os

# ---------------------------------------------------------
# 🔹 CONFIGURATION
# ---------------------------------------------------------
INPUT_FILE = "all_products.json"
OUTPUT_FILE = "cleaned_products.json"

# ---------------------------------------------------------
# 🔹 LOGIQUE D'EXTRACTION (REGEX)
# ---------------------------------------------------------
def parse_product_name(name):
    name_lower = name.lower()
    
    # 1. Extraction de la Marque (Brand)
    brands = ["samsung", "iphone", "apple", "xiaomi", "redmi", "oppo", "huawei", "google", "pixel", "oneplus", "infinix"]
    brand = "Autre"
    for b in brands:
        if b in name_lower:
            brand = b.capitalize()
            break
    if brand == "Apple": brand = "Iphone" # Standardisation

    # 2. Extraction du Stockage (Storage)
    # Cherche des patterns comme 128gb, 256 gb, 1to, 512 go
    storage_pattern = r'(\d+\s?(?:gb|go|to|tb))'
    storage_match = re.search(storage_pattern, name_lower)
    storage = storage_match.group(1).upper().replace(" ", "") if storage_match else "N/A"
    # Standardisation GO -> GB
    storage = storage.replace("GO", "GB").replace("TO", "1TB")

    # 3. Extraction du Modèle (Model)
    # On essaie de nettoyer le nom pour ne garder que le modèle
    # On retire la marque et le stockage du nom d'origine
    model = name
    # Retire la marque
    model = re.sub(brand, '', model, flags=re.IGNORECASE)
    # Retire le stockage
    model = re.sub(storage_pattern, '', model, flags=re.IGNORECASE)
    # Retire les mots inutiles et symboles
    model = re.sub(r'(\d+ ram|dual sim|noir|black|white|silver|gold|bleu|blue|4g|5g|verre trempé|coque)', '', model, flags=re.IGNORECASE)
    model = re.sub(r'[^\w\s\+]', '', model) # Retire la ponctuation
    model = model.strip()

    return brand, model, storage

# ---------------------------------------------------------
# 🔹 PIPELINE DE NETTOYAGE
# ---------------------------------------------------------
def clean_data():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Erreur : Le fichier {INPUT_FILE} est introuvable.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    cleaned_data = []
    print(f"🧹 Nettoyage de {len(raw_data)} produits...")

    for item in raw_data:
        brand, model, storage = parse_product_name(item["name"])
        
        # On reconstruit l'objet selon ton objectif
        clean_item = {
            "brand": brand,
            "model": model,
            "storage": storage,
            "price": item["price"],
            "platform": item["platform"],
            "original_name": item["name"], # On garde l'original au cas où
            "timestamp": item.get("timestamp")
        }
        cleaned_data.append(clean_item)

    # Sauvegarde du résultat
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=4)

    print(f"✅ Nettoyage terminé ! {len(cleaned_data)} produits sauvegardés dans {OUTPUT_FILE}")

# ---------------------------------------------------------
# 🔹 EXECUTION
# ---------------------------------------------------------
if __name__ == "__main__":
    clean_data()