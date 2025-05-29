from langchain_community.embeddings import HuggingFaceEmbeddings

'''def get_embedding_function():
    # Define the model name from Hugging Face Model Hub
    model_name = "AI-Growth-Lab/PatentSBERTa"

    # Define model arguments (e.g., to use GPU or CPU)
    model_kwargs = {'device': 'cpu'}  # Or 'cuda' if you have a GPU
                                     # e.g., model_kwargs = {'device': 'cuda:0'}

    encode_kwargs = {'normalize_embeddings': True}

    # Initialize HuggingFaceEmbeddings
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
        # cache_folder='/path/to/your/cache_folder' # Optional: to control download location
    )
    return embeddings'''

def get_embedding_function():
    model_name = "BAAI/bge-m3"
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': True}

    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    return embeddings