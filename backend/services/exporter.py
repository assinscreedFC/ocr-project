# llm_structuration.py
import os
import json
import re
from mistralai import Mistral
from dotenv import load_dotenv

# 🔹 Charger la clé API
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../env"))
api_key = os.environ.get("MISTRAL_API_KEY")
if not api_key:
    raise ValueError("❌ MISTRAL_API_KEY introuvable")
client = Mistral(api_key=api_key)
model = "mistral-large-latest"

# 🔹 Fonction pour extraire un JSON du texte
def extract_json(text: str) -> str | None:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else None

# 🔹 Fonction principale pour structurer le JSON OCR
def structure_ocr(ocr_json_path: str, output_folder: str = "./data/samples") -> tuple[str, dict]:
    with open(ocr_json_path, "r", encoding="utf-8") as f:
        ocr_data = json.load(f)

    markdown = ocr_data.get("pages", [{}])[0].get("markdown", "")

    prompt = f"""
Voici le texte OCR d'une facture au format Markdown.
Analyse-le et retourne un JSON strictement valide avec les champs :
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
- Pas de ```json ou ``` ni de commentaires.
- Si un champ est manquant, mets null ou [].

Texte OCR :
{markdown}
"""

    response = client.chat.complete(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

    structured_text = response.choices[0].message.content
    json_candidate = extract_json(structured_text)

    try:
        structured_json = json.loads(json_candidate or structured_text)
    except json.JSONDecodeError:
        print("⚠️ Réponse non valide JSON, sauvegarde brute...")
        structured_json = {"raw_output": structured_text}

    import pathlib
    pathlib.Path(output_folder).mkdir(parents=True, exist_ok=True)
    output_path = Path(output_folder) / f"{Path(ocr_json_path).stem}_structured.json"
    with open(output_path, "w", encoding="utf-8") as out_file:
        json.dump(structured_json, out_file, ensure_ascii=False, indent=4)

    print(f"✅ JSON structuré sauvegardé dans : {output_path}")
    return str(output_path), structured_json
