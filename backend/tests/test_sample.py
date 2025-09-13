import os
import json
from mistralai import Mistral
from dotenv import load_dotenv

# 🔹 Charger la clé API depuis le fichier .env
# Assure-toi que ton fichier env est à la racine du projet
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../env"))

api_key = os.environ.get("MISTRAL_API_KEY")
if not api_key:
    raise ValueError("⚠️ La variable d'environnement MISTRAL_API_KEY n'est pas définie !")

client = Mistral(api_key=api_key)

# 🔹 URL publique de ton PDF via ngrok
pdf_url = "https://b2dc716cbb28.ngrok-free.app/facture1.pdf"

# 🔹 Appeler Mistral OCR
ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "document_url",
        "document_url": pdf_url
    },
    include_image_base64=True
)

# 🔹 Convertir l'objet OCRResponse en dictionnaire JSON serializable
ocr_dict = ocr_response.dict()

# 🔹 Sauvegarder le résultat dans un fichier JSON
output_json_path = "./data/samples/facture1_ocr_result.json"
with open(output_json_path, "w", encoding="utf-8") as out_file:
    json.dump(ocr_dict, out_file, ensure_ascii=False, indent=4)

print(f"OCR terminé ! Résultat sauvegardé dans : {output_json_path}")

# 🔹 Afficher le texte extrait page par page
if "pages" in ocr_dict:
    for i, page in enumerate(ocr_dict["pages"], 1):
        print(f"\n=== Page {i} ===")
        print(page.get("text", "Aucun texte détecté"))
