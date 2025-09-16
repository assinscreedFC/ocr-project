# ocr_engine.py
import os
import base64
import json
from pathlib import Path
from turtle import st

from mistralai import Mistral
from dotenv import load_dotenv

# 🔹 Charger la clé API
load_dotenv(dotenv_path="./env")

# Puis récupérer la clé soit dans env, soit dans secrets
api_key = (
    os.getenv("MISTRAL_API_KEY")
    or st.secrets.get("MISTRAL_API_KEY")
)
if not api_key:
    raise ValueError("❌ MISTRAL_API_KEY introuvable")
client = Mistral(api_key=api_key)

# 🔹 Fonction pour encoder un fichier en base64
def encode_file_to_base64(file_path: str) -> str:
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# 🔹 Fonction pour déterminer le MIME type
def get_mime_type(file_path: str) -> str:
    ext = file_path.lower().split(".")[-1]
    if ext == "pdf":
        return "application/pdf"
    elif ext in ["png", "jpg", "jpeg"]:
        return f"image/{ext if ext != 'jpg' else 'jpeg'}"
    else:
        raise ValueError(f"Format non supporté : {ext}")

# 🔹 Fonction principale OCR
def run_ocr(file_path: str, output_folder: str = "./data/samples") -> str:
    mime_type = get_mime_type(file_path)
    file_base64 = encode_file_to_base64(file_path)

    # 🔹 Appel OCR Mistral
    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={"type": "document_url", "document_url": f"data:{mime_type};base64,{file_base64}"},
        include_image_base64=True
    )

    # 🔹 Convertir en dictionnaire
    ocr_dict = ocr_response.model_dump()

    # 🔹 Enrichir le JSON pour indexation/recherche
    pages = ocr_dict.get("pages", [])
    full_text = " ".join([page.get("markdown", "") for page in pages])
    ocr_dict["full_text"] = full_text
    ocr_dict["file_name"] = Path(file_path).name
    ocr_dict["num_pages"] = len(pages)
    ocr_dict["document_type"] = "facture"  # tu peux rendre dynamique si besoin

    # 🔹 Sauvegarder
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    output_path = Path(output_folder) / f"{Path(file_path).stem}_ocr_result.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(ocr_dict, f, ensure_ascii=False, indent=4)

    print(f"✅ OCR terminé et JSON enrichi sauvegardé dans : {output_path}")

    # 🔹 Afficher le texte extrait
    for i, page in enumerate(pages, 1):
        print(f"\n=== Page {i} ===")
        print(page.get("text", "Aucun texte détecté"))

    return str(output_path)


# 🔹 Exemple d'utilisation
if __name__ == "__main__":
    local_file_path = "./data/samples/facture1.pdf"  # ou image
    run_ocr(local_file_path)
