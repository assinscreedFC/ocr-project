# app.py (version corrigée pour persistance structuration & DataFrame)
import streamlit as st
import json
import base64
import pandas as pd
from pathlib import Path
from backend.services.ocr_engine import run_ocr
from backend.services.exporter import structure_ocr
import hashlib

st.set_page_config(page_title="OCR & Structuration", layout="wide")
st.title("📄 Traitement intelligent de documents")

# Paths
DATA_DIR = Path("data")
UPLOAD_DIR = DATA_DIR / "uploads"
SAMPLES_DIR = DATA_DIR / "samples"
INDEX_FILE = DATA_DIR / "index.json"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)

# ----------------------
# Helpers (inchangés)
# ----------------------
def load_index():
    if INDEX_FILE.exists():
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_index(index_data):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=4)

def add_or_update_index_entry(entry):
    index = load_index()
    # Remove existing entry with same file_name to avoid duplicates
    index = [e for e in index if e.get("file_name") != entry.get("file_name")]
    index.append(entry)
    save_index(index)

def embed_pdf(path: Path, height=600):
    if not path.exists():
        return None
    data = path.read_bytes()
    b64 = base64.b64encode(data).decode("utf-8")
    src = f"data:application/pdf;base64,{b64}"
    html = f'<iframe src="{src}" width="100%" height="{height}"></iframe>'
    return html

def make_safe_key(*parts):
    raw = "|".join(map(str, parts))
    return hashlib.sha1(raw.encode()).hexdigest()[:16]

def structured_to_dataframe(structured):
    if not isinstance(structured, dict):
        return None
    if structured.get("items") and isinstance(structured.get("items"), list):
        try:
            df_items = pd.json_normalize(structured["items"])
            return df_items
        except Exception:
            pass
    rows = []
    for k, v in structured.items():
        if isinstance(v, (dict, list)):
            val = json.dumps(v, ensure_ascii=False)
        else:
            val = v
        rows.append({"field": k, "value": val})
    return pd.DataFrame(rows)

# ----------------------
# Initialise session_state keys si absents
# ----------------------
if "last_structured_path" not in st.session_state:
    st.session_state["last_structured_path"] = None
if "last_structured" not in st.session_state:
    st.session_state["last_structured"] = None
if "last_ocr_path" not in st.session_state:
    st.session_state["last_ocr_path"] = None
if "last_uploaded_file" not in st.session_state:
    st.session_state["last_uploaded_file"] = None

# Button to clear last result
st.sidebar.markdown("### Actions")
if st.sidebar.button("🔄 Réinitialiser dernier résultat"):
    st.session_state["last_structured_path"] = None
    st.session_state["last_structured"] = None
    st.session_state["last_ocr_path"] = None
    st.session_state["last_uploaded_file"] = None
    st.success("Dernier résultat réinitialisé.")

# ----------------------
# Upload + OCR + Structuration
# ----------------------
uploaded_file = st.file_uploader("Dépose un PDF ou une image", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    # Save uploaded file
    temp_path = UPLOAD_DIR / uploaded_file.name
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.read())
    st.success(f"✅ Fichier enregistré : {temp_path}")

    # store uploaded filename in session_state
    st.session_state["last_uploaded_file"] = str(temp_path)

    # OCR
    with st.spinner("🔍 Exécution de l'OCR..."):
        ocr_json_path = run_ocr(str(temp_path))
    st.success("✅ OCR terminé")
    st.session_state["last_ocr_path"] = str(ocr_json_path)

    # Load OCR JSON and display full_text
    with open(ocr_json_path, "r", encoding="utf-8") as f:
        ocr_data = json.load(f)

    full_text = (ocr_data.get("full_text") or "").strip()
    st.subheader("📝 Texte OCR")
    if full_text:
        st.text_area("Texte extrait (full_text)", full_text, height=300)
    else:
        st.warning("⚠️ Aucun texte détecté (OCR vide ou erreur)")

    # Structuration
    if st.button("Structurer le document (LLM)"):
        with st.spinner("🤖 Structuration via LLM..."):
            # appel existant (peut lever erreurs, garde tel quel)
            structured_json_path, structured_json = structure_ocr(ocr_json_path)

        # persist into session_state so it survives reruns
        st.session_state["last_structured_path"] = str(structured_json_path)
        st.session_state["last_structured"] = structured_json

        st.success(f"✅ JSON structuré sauvegardé : {structured_json_path}")

        # Add to index.json (include path to original uploaded file for download/view)
        entry = {
            "file_name": Path(temp_path).name,
            "stem": Path(temp_path).stem,
            "path_file": str(temp_path),
            "path_ocr": str(ocr_json_path),
            "path_structured": str(structured_json_path),
            "full_text": full_text,
            "structured_json": structured_json,
            "num_pages": ocr_data.get("num_pages", ocr_data.get("usage_info", {}).get("pages_processed", 1)),
            "document_type": ocr_data.get("document_type", "unknown")
        }
        add_or_update_index_entry(entry)
        st.success("Index mis à jour.")

# ----------------------
# Display last structuring result stored in session_state (persists across reruns)
# ----------------------
if st.session_state.get("last_structured"):
    st.markdown("---")
    st.subheader("Résultat de la dernière structuration")

    structured_data = st.session_state["last_structured"]
    structured_path = st.session_state["last_structured_path"]

    # View selection persists via key
    view_format = st.radio(
        "Afficher le résultat comme",
        options=["JSON", "DataFrame"],
        index=0,
        key="last_view_choice"
    )

    if view_format == "JSON":
        st.subheader("📊 Résultat structuré (JSON)")
        st.json(structured_data)
    else:
        st.subheader("📑 Résultat structuré (DataFrame view)")
        # Try to convert to DataFrame and catch exceptions
        try:
            df_view = structured_to_dataframe(structured_data)
            if df_view is None or df_view.empty:
                st.info("Aucune vue tabulaire disponible pour cette structuration. Affichage JSON ci-dessous.")
                st.json(structured_data)
            else:
                st.dataframe(df_view, use_container_width=True)
        except Exception as e:
            st.error(f"Erreur lors de la conversion en DataFrame : {e}")
            st.json(structured_data)

    # Download structured JSON (unique key)
    dl_key = make_safe_key("dl_last_struct", structured_path or "none")
    st.download_button(
        label="⬇️ Télécharger le JSON structuré",
        data=json.dumps(structured_data, ensure_ascii=False, indent=4),
        file_name=Path(structured_path).name if structured_path else "structured.json",
        mime="application/json",
        key=f"dl_last_{dl_key}"
    )

# ----------------------
# Index & Recherche (table + selection)
# ----------------------
st.markdown("---")
st.subheader("🔎 Recherche globale et navigation")

index_data = load_index()
st.write(f"Documents indexés : **{len(index_data)}**")

# Search input
search_query = st.text_input("Recherche (mots séparés par espaces)")

# Optional filters
types = sorted({d.get("document_type", "unknown") for d in index_data})
selected_type = st.selectbox("Filtrer par type de document", ["Tous"] + types)

# Perform search
def matches_query(doc, keywords):
    text = (doc.get("full_text") or "").lower()
    return all(k in text for k in keywords)

results = index_data
if search_query:
    keywords = [w.strip().lower() for w in search_query.split() if w.strip()]
    results = [d for d in results if matches_query(d, keywords)]
if selected_type and selected_type != "Tous":
    results = [d for d in results if d.get("document_type") == selected_type]

# Show results as DataFrame for selection
if results:
    rows = []
    for d in results:
        total = d.get("structured_json", {}).get("total", None)
        rows.append({
            "file_name": d.get("file_name"),
            "document_type": d.get("document_type"),
            "total": total,
            "path_file": d.get("path_file"),
            "path_structured": d.get("path_structured")
        })
    df_results = pd.DataFrame(rows)
    st.dataframe(df_results, use_container_width=True)

    choices = [f"{r['file_name']} — {r['document_type']} — total:{r['total']}" for r in rows]
    selected = st.selectbox("Sélectionner un document pour afficher / télécharger", [""] + choices)
    if selected:
        idx = choices.index(selected)
        doc = results[idx]

        st.markdown("### Détails du document")
        st.write(f"**{doc.get('file_name')}** — Type: {doc.get('document_type')} — Pages: {doc.get('num_pages')}")

        snippet = (doc.get("full_text") or "")[:1000].replace("\n", " ")
        st.write("> " + snippet + ("..." if len(snippet) > 1000 else ""))

        # Show structured JSON / DataFrame
        st.subheader("Contenu structuré")
        structured = doc.get("structured_json")
        if structured:
            view_choice = st.radio("Afficher comme", ["JSON", "DataFrame"], key=f"view_{make_safe_key(doc.get('file_name'))}")
            if view_choice == "JSON":
                st.json(structured)
            else:
                try:
                    df_view = structured_to_dataframe(structured)
                    if df_view is not None and not df_view.empty:
                        st.dataframe(df_view, use_container_width=True)
                    else:
                        st.write("Aucune vue tabulaire disponible, affichage JSON :")
                        st.json(structured)
                except Exception as e:
                    st.error(f"Erreur conversion DataFrame: {e}")
                    st.json(structured)

            dl_key = make_safe_key("dl_struct", doc.get("file_name"))
            st.download_button(
                label="⬇️ Télécharger JSON structuré",
                data=json.dumps(structured, ensure_ascii=False, indent=4),
                file_name=Path(doc.get("path_structured") or doc.get("file_name")).name,
                mime="application/json",
                key=f"dl_struct_{dl_key}"
            )
        else:
            st.info("Aucun JSON structuré pour ce document.")

        # Show & download original file
        pf = doc.get("path_file")
        if pf and Path(pf).exists():
            if pf.lower().endswith(".pdf"):
                html = embed_pdf(Path(pf), height=700)
                if html:
                    st.components.v1.html(html, height=700, scrolling=True)
            with open(pf, "rb") as bf:
                pdf_bytes = bf.read()
                dl_pdf_key = make_safe_key("dl_pdf", doc.get("file_name"))
                st.download_button(
                    label="⬇️ Télécharger le fichier original (PDF/IMG)",
                    data=pdf_bytes,
                    file_name=Path(pf).name,
                    mime="application/pdf" if pf.lower().endswith(".pdf") else "application/octet-stream",
                    key=f"dl_pdf_{dl_pdf_key}"
                )
        else:
            st.warning("Fichier original absent.")
else:
    st.info("Aucun document ne correspond à la requête actuellement.")

# Footer
st.sidebar.markdown("## Info")
st.sidebar.write(f"Index entries: {len(index_data)}")
