from langchain_ollama import OllamaEmbeddings

def get_embedding_function():

    ## SEARCH FOR BETTER EMBEDDINGS MODELS, THIS ONE IS BAD
    ## EMBEDDING MODELS AFFECTS RAG RESULTS
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    return embeddings