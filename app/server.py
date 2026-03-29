from flask import Flask, jsonify
import json
import os

app = Flask(__name__)

# chemin absolu
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_PATH = os.path.join(BASE_DIR, "data", "processed", "cleaned.json")

@app.route("/")
def home():
    return "API Price Intelligence 🚀"

@app.route("/products")
def products():
    with open(FILE_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)

@app.route("/compare")
def compare():
    with open(FILE_PATH, encoding="utf-8") as f:
        data = json.load(f)

    jumia = [p for p in data if p["platform"] == "jumia"]
    electro = [p for p in data if p["platform"] == "electroplanet"]

    return jsonify({
        "jumia_count": len(jumia),
        "electroplanet_count": len(electro)
    })

# 🔥 BONUS : meilleur prix
@app.route("/best-price")
def best_price():
    with open(FILE_PATH, encoding="utf-8") as f:
        data = json.load(f)

    best = {}

    for p in data:
        key = p["model"]
        if key not in best or p["price"] < best[key]["price"]:
            best[key] = p

    return jsonify(list(best.values()))

if __name__ == "__main__":
    app.run(debug=True)