## NeuroPatent

NeuroPatent is a Python-based retrieval‑augmented generation (RAG) prototype built to index PDF patents, create embeddings, store them in a local Chroma DB, and provide a simple web UI to query the indexed patent documents.

This repository contains scripts to clean PDFs, extract embeddings, initialize a local vector database, load PDFs into the DB, and run a lightweight web application to interact with the system.

### Key features
- Search for relevant patents to the user problem
- Parse and clean PDF files
- Generate embeddings for document chunks
- Store embeddings and metadata in a local Chroma DB (`chroma_db/`)
- Simple web UI for chat-style querying and keyword search

## Repository structure

- `app.py` — main Flask app to run the UI and handle queries
- `load_pdfs.py` — script to download a relevant patent to the user problem and load them into the DB
- `initialize_db.py` — create/initialize the Chroma DB and required tables
- `embedding_function.py` — code that wraps the embedding model/function used to create vectors
- `clean_pdf.py` — utilities to clean or preprocess PDF text prior to embedding
- `read_from_db.py` — utilities to query the Chroma DB and retrieve documents
- `rag.py` — RAG orchestration utilities (retrieval + generation agents logic)
- `requirements.txt` — Python dependencies for the project
- `chroma_db/` — local Chroma DB files (SQLite + stored vector data)
- `patents_dataset/` — folder where raw PDF patent files are stored (not included in repo)
- `templates/` and `static/` — web UI templates and assets (CSS, images)


## Quickstart (Windows PowerShell)

Prerequisites:
- Python 3.10+ (or your project's tested Python version)
- Git (optional)

1) Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```
3) Get your SerpAPI API (free) and place it in the load_pdfs.py file

4) Run the web app

Start the application :

```powershell
python app.py
```

## Usage
- Use the web UI in `templates/` for chat-style queries and keyword search.
- For programmatic access, use `read_from_db.py` functions to retrieve similar document chunks and `rag.py` to generate answers.

## Development notes
- The embedding implementation is in `embedding_function.py` — swap the model here if needed (if you want to use a specific embedding function).
- The project currently uses a local Chroma-based store under `chroma_db/` — treat this folder as the persistent vector store.
- If you want to replace the vector DB or use a hosted service (Pinecone, Weaviate, etc.), update the DB wrapper utilities in `initialize_db.py` / `read_from_db.py` accordingly.

## Contact / Author
- Repository: `NeuroPatent` by Anass Benamara and Mohamed Tribak.
- For questions, open an issue or contact : anassbenamara8@gmail.com
---
