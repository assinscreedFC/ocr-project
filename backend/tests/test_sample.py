import os
import base64
import json
from mistralai import Mistral
from dotenv import load_dotenv

# 🔹 Charger la clé API depuis .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../env"))
api_key = os.environ.get("MISTRAL_API_KEY")
if not api_key:
    raise ValueError("❌ MISTRAL_API_KEY introuvable")

client = Mistral(api_key=api_key)

# 🔹 Chemin local du fichier (PDF ou image)
local_file_path = "./data/samples/facture1.pdf"  # ou .png/.jpg

# 🔹 Encoder le fichier en base64
def encode_file_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

file_base64 = encode_file_to_base64(local_file_path)

# 🔹 Déterminer le type MIME
if local_file_path.lower().endswith(".pdf"):
    mime_type = "application/pdf"
else:
    mime_type = "image/png"  # ou "image/jpeg" selon le format

# 🔹 Appel OCR Mistral
ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "document_url",
        "document_url": f"data:{mime_type};base64,{file_base64}"
    },
    include_image_base64=True
)

# 🔹 Convertir la réponse en dict JSON
ocr_dict = ocr_response.model_dump()

# 🔹 Sauvegarder le résultat
output_path = "./data/samples/facture1_ocr_result.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(ocr_dict, f, ensure_ascii=False, indent=4)

print(f"✅ OCR terminé et sauvegardé dans : {output_path}")

# 🔹 Afficher le texte extrait
for i, page in enumerate(ocr_dict.get("pages", []), 1):
    print(f"\n=== Page {i} ===")
    print(page.get("text", "Aucun texte détecté"))
