# 📄 OCR & Smart Document Structuring

<div align="center">
  <p><strong>Automated invoice processing and data extraction with Mistral LLM</strong></p>

  [![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.109%2B-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
  [![Mistral](https://img.shields.io/badge/AI-Mistral-purple?style=for-the-badge&logo=openai)](https://mistral.ai/)

  ![Status](https://img.shields.io/badge/Status-Active-success?style=flat-square)
  ![Version](https://img.shields.io/badge/Version-1.0.0-blue?style=flat-square)
</div>

## 📋 Overview

**OCR Project** is a powerful Python application designed to digitize and structure complex documents (PDFs, images) automatically. By combining robust OCR (Optical Character Recognition) with the **Mistral Large Language Model**, it transforms unstructured invoices and contracts into clean, validated JSON data.

- 🔍 **Smart OCR**: Automatically detects file types (PDF/Image) and extracts text.
- 🧠 **AI Structuring**: Uses Mistral LLM to parse raw text into strict JSON formats.
- 🚀 **High Performance**: Asynchronous processing pipeline via FastAPI.
- 📂 **Batch Processing**: Capable of handling single files or entire folders.
- 📊 **Search Engine**: (Prototype) Full-text search and filtering by document metadata.

## ✨ Features

### Core Features
- **Auto-Detection**: Seamlessly handles PDF, JPG, PNG, and JPEG formats.
- **Base64 Processing**: Local file processing without fastidious URL hosting.
- **Data Validation**: Ensures output JSON handles null values and empty lists gracefully.
- **Page-by-Page Analysis**: Detailed breakdown of text extraction per page.

### Advanced Capabilities
- **LLM Integration**: Leverages Mistral to "understand" document context (Dates, Amounts, Vendors).
- **Markdown Export**: Converts raw OCR output into readable Markdown before structuring.
- **Search prototype**: Indexing system to query documents by content, date, or amount.

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+**
- **Mistral API Key** (or local LLM setup)

### Installation

1. **Clone the project**
   ```bash
   git clone https://github.com/assinscreedFC/ocr-project.git
   cd ocr-project
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration**
   Ensure your environment variables (API keys) are set up for the OCR and Mistral services.

## 📖 Usage

### Start the Pipeline
You can process files directly using the main script:
```bash
python backend/app.py
```

### Key Functions
- `process_file(path)`: Runs OCR -> Structuring -> JSON Export for a single file.
- `process_folder(path)`: Batch processes an entire directory of documents.

## 📁 Project Structure

```
ocr-project/
├── backend/             # Core application logic
│   ├── app.py           # Main entry point / Workflow orchestrator
│   └── services/        # Business logic modules
│       ├── ocr_engine.py    # OCR extraction logic
│       ├── exporter.py      # JSON/Markdown export handling
│       ├── parser.py        # Text parsing utilities
│       └── preprocessing.py # Image/PDF preparation
│
├── data/                # Data storage (Input/Output)
│   └── samples/         # Sample invoices and results
│
├── frontend/            # (In Development) Web Interface
│   └── requirements.txt
│
└── requirements.txt     # Project dependencies
```

## 🛠 Tech Stack

- **Language**: Python 3.10+
- **API Framework**: FastAPI
- **AI/LLM**: Mistral (via API)
- **Data**: JSON, Markdown

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to submit a Pull Request.

## 📝 License

Copyright © 2024. All rights reserved.
Internal usage only.

---
<div align="center">
  <p>Built with ❤️ for automation</p>
</div>
