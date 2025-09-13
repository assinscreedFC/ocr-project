# ocr_engine.py
import os
import base64
import json
from pathlib import Path
from mistralai import Mistral
from dotenv import load_dotenv

# 🔹 Charger la clé API
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../env"))
api_key = os.environ.get("MISTRAL_API_KEY")
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

    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={"type": "document_url", "document_url": f"data:{mime_type};base64,{file_base64}"},
        include_image_base64=True
    )

    ocr_dict = ocr_response.model_dump()
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    output_path = Path(output_folder) / f"{Path(file_path).stem}_ocr_result.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(ocr_dict, f, ensure_ascii=False, indent=4)

    print(f"✅ OCR terminé et sauvegardé dans : {output_path}")
    return str(output_path)
