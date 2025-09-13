from fastapi import FastAPI 
# workflow.py
import os
from pathlib import Path
from services.ocr_engine import run_ocr
from services.exporter import structure_ocr

def process_file(file_path: str, output_folder: str = "./data/samples"):
    """
    Processus complet :
    1️⃣ OCR du fichier (PDF ou image)
    2️⃣ Extraction du JSON OCR
    3️⃣ Structuration via LLM
    """
    print(f"\n🔹 Traitement du fichier : {file_path}")

    # 1️⃣ OCR
    ocr_json_path = run_ocr(file_path, output_folder=output_folder)

    # 2️⃣ Structuration LLM
    structured_json_path, structured_json = structure_ocr(ocr_json_path, output_folder=output_folder)

    print(f"✅ Workflow terminé pour : {file_path}")
    return ocr_json_path, structured_json_path, structured_json

def process_folder(folder_path: str, output_folder: str = "./data/samples"):
    """
    Traite tous les fichiers PDF et images d'un dossier
    """
    folder = Path(folder_path)
    for file in folder.iterdir():
        if file.suffix.lower() in [".pdf", ".png", ".jpg", ".jpeg"]:
            process_file(str(file), output_folder=output_folder)

if __name__ == "__main__":
    # 🔹 Exemple : traiter un seul fichier
    single_file = "./data/samples/facture1.pdf"
    process_file(single_file)

    # 🔹 Exemple : traiter un dossier entier
    # folder_path = "./data/samples/"
    # process_folder(folder_path)
