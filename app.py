from flask import (
    Flask, render_template, redirect, request, url_for,
    session, flash, jsonify
)
from load_pdfs import download_patent, question_to_keywords
from initialize_db import load_documents, split_documents, add_to_chroma, name_collection
from read_from_db import load_sessions, load_conversation,get_patent_id, delete_session_from_db
from rag import get_chatbot_response
from langchain_community.document_loaders import UnstructuredPDFLoader

import tempfile
from sqlalchemy import create_engine




import markdown
import chromadb
import re




app = Flask(__name__)

app.secret_key = "Hii"

keywords = []
engine = create_engine("sqlite:///chat_history.db")
@app.route("/")
def login_page():
    sessions = load_sessions(engine)
    sessions.reverse()
    return render_template("keyword.html", sessions = sessions)

@app.route("/search", methods = ["GET", "POST"])
def search():
    user_pdf = request.files.get('user_pdf')
    if user_pdf :
        keyword = user_pdf.filename
        temp_pdf_path = None
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", mode='wb') as tmp_file:
                user_pdf.save(tmp_file) # Save content to the temp file
                temp_pdf_path = tmp_file.name
        #loader = PyPDFLoader(file_path=temp_pdf_path)
        loader = UnstructuredPDFLoader(
        file_path=temp_pdf_path,
        mode="single",      # Tries to combine pages into a single logical document content
        strategy="hi_res"    # Let unstructured pick, or try "fast" or "hi_res"
                           # For patents with columns, "hi_res" might be better if "auto" doesn't work well.
    )
        langchain_documents = loader.load() 
        if not langchain_documents:
            result_message = "Could not extract any content from the PDF."
            print(result_message)
            return redirect(url_for("login_page"))
        else :
            chunks = split_documents(langchain_documents)
            add_to_chroma(chunks, keyword)
            print("DOCUMENTS ADDED SUCCESSFULLY")
            return redirect(url_for("go_session", session_id = keyword))
        
    question = request.form["keyword"]  # we need to check its validity
    keyword = question_to_keywords(question)
    keyword =keyword.split(',')[0]
    keywords.append(keyword)
    patent_id = download_patent(keyword)
    if patent_id :
        documents = load_documents()
        chunks = split_documents(documents)
        add_to_chroma(chunks, keyword)
        print("DOCUMENTS ADDED SUCCESSFULLY")
        return redirect(url_for("go_session", session_id = keyword))
    else :
        flash("No Patent found with the corresponding keywords, try again !")
        return render_template("keyword.html")


@app.route("/session/<session_id>")
def go_session(session_id) :
    patent_id = get_patent_id(session_id)
    messages = load_conversation(engine, session_id)
    sessions = load_sessions(engine)
    sessions.reverse()
    return render_template("chatbot.html", sessions = sessions, messages = messages, session_id = session_id, patent_id= patent_id)



@app.route("/chatbot")
def chatbot() :
    sessions = load_sessions(engine)
    sessions.reverse()
    return render_template("chatbot.html", sessions = sessions, messages = None)

# Initialize components once (outside routes)
'''embedding_function = get_embedding_function()  # Make sure this is defined
db = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)
model = Ollama(model="llama3.1:8b")
'''
@app.route("/get_response", methods=["POST"])
def get_response():
    ## check if the user sneaks the route
    user_input = request.form["user_input"]
    session_id = request.form.get("session_idd")
    print("##############################################")
    print(session_id)
    print("##############################################")

    '''if keywords : 
        session_id = keywords[-1]
    else : 
        engine = create_engine("sqlite:///chat_history.db")
        sessions = load_sessions(engine)
        session_id = sessions[-1]
'''
    if not session_id :
        session_id = keywords[-1]
    bot_response = get_chatbot_response(user_input, session_id)
    return jsonify({"response": bot_response})




@app.route("/delete_session", methods=["POST"])
def delete_session() : 
    session_id = request.form["session_id_delete"]
    delete_session_from_db(session_id, engine)
    try : 
        db_path = "./chroma_db"
        client = chromadb.PersistentClient(path=db_path)
        collection_name = name_collection(session_id)
        client.delete_collection(name=collection_name)
    except : 
        print("This collection doesnt exist")
    return redirect(url_for("login_page") )



'''
debugging the parameters injected to the prompt
def debug_input(x):
    print("\n########################DEBUG: Prompt Input##########################")
    print(">>> HISTORY:\n", x["history"])
    print(">>> CONTEXT:\n", x["context"])
    print(">>> QUESTION:\n", x["question"])
    print("=================================\n")
    return x  # must return the unchanged input
'''
if __name__ == "__main__" :
    app.run(debug=True)
