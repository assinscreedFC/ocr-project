import json

# 🔹 Charger l'index
with open("data/index.json", "r", encoding="utf-8") as f:
    index = json.load(f)

def search_index(index, query):
    """
    Recherche tous les documents contenant tous les mots du query dans le full_text.
    """
    results = []
    keywords = query.lower().split()  # séparer la requête en mots

    for doc in index:
        text = doc.get("full_text", "").lower()
        if all(k in text for k in keywords):
            results.append(doc)

    return results

print("🔹 Bienvenue dans le moteur de recherche des documents !")
print("Tapez vos mots-clés séparés par des espaces (ou 'exit' pour quitter)")

while True:
    query = input("\nVotre recherche : ").strip()
    if query.lower() == "exit":
        break
    if not query:
        print("❌ Veuillez saisir au moins un mot-clé.")
        continue

    matches = search_index(index, query)
    if not matches:
        print("⚠️ Aucun document trouvé.")
    else:
        print(f"✅ {len(matches)} document(s) trouvé(s) :")
        for m in matches:
            total = m.get("structured_json", {}).get("total", "N/A")
            print(f"- {m['file_name']} | Type: {m.get('document_type')} | Total: {total}")
