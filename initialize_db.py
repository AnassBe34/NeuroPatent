import argparse
import os
import shutil
from langchain.document_loaders.pdf import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain.vectorstores.chroma import Chroma
from embedding_function import get_embedding_function
from langchain.document_loaders import PyPDFLoader
from langchain_community.document_loaders import UnstructuredPDFLoader
import chromadb

import re



CHROMA_PATH = "./chroma_db"

'''def load_documents():
    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, "clean_patent.pdf")
    document_loader = PyPDFLoader(file_path)
    return document_loader.load()'''

def load_documents() -> list[Document]: # Added type hint for clarity
    """
    Loads documents from a PDF file using UnstructuredPDFLoader.
    Assumes "clean_patent.pdf" is in the current working directory.
    """
    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, "clean_patent.pdf")

    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return [] # Return an empty list if the file doesn't exist

    print(f"Loading document from: {file_path} using UnstructuredPDFLoader")

    loader = UnstructuredPDFLoader(
        file_path=file_path,
        mode="single",      # Tries to combine pages into a single logical document content
        strategy="hi_res"    # Let unstructured pick, or try "fast" or "hi_res"
                           # For patents with columns, "hi_res" might be better if "auto" doesn't work well.
    )

    try:
        documents = loader.load() # This returns list[Document]
        print(f"Successfully loaded {len(documents)} document(s) with UnstructuredPDFLoader.")
        return documents
    except Exception as e:
        print(f"Error loading document with UnstructuredPDFLoader: {e}")
        return []


def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)


def add_to_chroma(chunks: list[Document], keyword ):
    ## Load the existing database.
    collection_name = name_collection(keyword)
    db = Chroma(
        persist_directory=CHROMA_PATH, embedding_function=get_embedding_function(), collection_name= collection_name
    )

    ## Calculate Page IDs.
    chunks_with_ids = calculate_chunk_ids(chunks)

    ## Add or Update the documents.
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    ## Only add documents that don't exist in the DB.
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
        db.persist()
    else:
        print("✅ No new documents to add")

def name_collection(session_id):
    session_id = session_id.strip().replace(" ", "_")
    session_id = re.sub(r'[^a-zA-Z0-9_-]', '', session_id)
    if len(session_id) < 3:
        name += "_default"
    return session_id[:63]


def calculate_chunk_ids(chunks):

    ## This will create IDs like "data/monopoly.pdf:6:2"
    ## Page Source : Page Number : Chunk Index

    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        ## If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        ## Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        ## Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id

    return chunks


def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)



def main():

    # Check if the database should be cleared (using the --clear flag).
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()
    if args.reset:
        print("✨ Clearing Database")
        clear_database()
        return 0

    # Create (or update) the data store.
    documents = load_documents()
    chunks = split_documents(documents)
    add_to_chroma(chunks)
    print("DOCUMENTS ADDED SUCCESSFULLY")





client = chromadb.PersistentClient(path=CHROMA_PATH)
collections = client.list_collections()
collection_names = client.list_collections()
for name in collection_names:
    collection_obj = client.get_collection(name=name)
    print(f"- Collection Name: {name}")
    print(f"  ID: {collection_obj.id}")
    print(f"  Metadata: {collection_obj.metadata}")
    # You can also get the count
    print(f"  Item Count: {collection_obj.count()}")
'''
if __name__ == "__main__":
    main()

'''
'''documents = load_documents()
chunks = split_documents(documents)
print(chunks[0].metadata)
'''