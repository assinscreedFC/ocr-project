import os
import json
import re
from mistralai import Mistral
from dotenv import load_dotenv

# Charger la clé API depuis le fichier .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../env"))
api_key = os.environ.get("MISTRAL_API_KEY")
if not api_key:
    raise ValueError("❌ MISTRAL_API_KEY introuvable dans les variables d'environnement")

client = Mistral(api_key=api_key)
model = "mistral-large-latest"

# 1. Charger le résultat OCR
input_json_path = "data/samples/facture1_ocr_result.json"
with open(input_json_path, "r", encoding="utf-8") as f:
    ocr_data = json.load(f)

# 2. Extraire le markdown
markdown = ocr_data["pages"][0]["markdown"]

# 3. Prompt renforcé pour forcer un JSON brut
prompt = f"""
Voici le texte OCR d'une facture au format Markdown.
Analyse-le et retourne un **JSON strictement valide** avec les champs suivants :
- invoice_number
- date
- due_date
- seller (nom)
- buyer (nom, adresse)
- items (liste avec description, quantité, prix_unitaire, montant)
- subtotal
- tax
- total
- amount_paid
- terms

⚠️ Règles :
- Réponds UNIQUEMENT par un JSON brut, sans aucun texte avant ou après.
- Ne mets pas de ```json ou ``` dans la réponse.
- Pas de commentaires ni d'explications.
- Si un champ est manquant, mets null ou [].

Texte OCR :
{markdown}
"""

print("🔄 Envoi du markdown à Mistral pour structuration...")

response = client.chat.complete(
    model=model,
    messages=[{"role": "user", "content": prompt}]
)

structured_text = response.choices[0].message.content

# 4. Extraction automatique du JSON si jamais du texte pollue la réponse
def extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else None

json_candidate = extract_json(structured_text)

try:
    structured_json = json.loads(json_candidate or structured_text)
except json.JSONDecodeError:
    print("⚠️ Réponse non valide JSON, sauvegarde brute...")
    structured_json = {"raw_output": structured_text}

# 5. Sauvegarder le résultat
output_json_path = "data/samples/facture1_structured.json"
with open(output_json_path, "w", encoding="utf-8") as out_file:
    json.dump(structured_json, out_file, ensure_ascii=False, indent=4)

print(f"✅ JSON structuré sauvegardé dans : {output_json_path}")
