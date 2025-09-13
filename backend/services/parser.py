import os
import json
from pathlib import Path

# 🔹 Dossiers où sont stockés les fichiers OCR et structured
OCR_FOLDER = "./data/samples"
STRUCTURED_FOLDER = "./data/samples"

# 🔹 Fichier index final
INDEX_FILE = "./data/index.json"

index_data = []

# 🔹 Parcourir tous les fichiers OCR
for ocr_file in Path(OCR_FOLDER).glob("*_ocr_result.json"):
    # Nom du fichier (sans extension)
    stem = ocr_file.stem.replace("_ocr_result", "")

    # Correspondant structured file
    structured_file = Path(STRUCTURED_FOLDER) / f"{stem}_structured.json"

    # Charger OCR JSON
    with open(ocr_file, "r", encoding="utf-8") as f:
        ocr_json = json.load(f)

    # Charger structured JSON si présent
    if structured_file.exists():
        with open(structured_file, "r", encoding="utf-8") as f:
            structured_json = json.load(f)
    else:
        structured_json = None

    # Construire l'entrée index
    entry = {
        "file_name": ocr_json.get("file_name", f"{stem}.pdf"),
        "document_type": ocr_json.get("document_type", "unknown"),
        "full_text": ocr_json.get("full_text", ""),
        "structured_json": structured_json,
        "path_ocr": str(ocr_file),
        "path_structured": str(structured_file) if structured_file.exists() else None
    }

    index_data.append(entry)

# 🔹 Sauvegarder l'index complet
Path(INDEX_FILE).parent.mkdir(parents=True, exist_ok=True)
with open(INDEX_FILE, "w", encoding="utf-8") as f:
    json.dump(index_data, f, ensure_ascii=False, indent=4)

print(f"✅ Index généré avec {len(index_data)} documents dans : {INDEX_FILE}")
