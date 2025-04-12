from flask import Flask, render_template, redirect, request, url_for, session, flash, send_file, jsonify, session
from load_pdfs import download_patent
from initialize_db import load_documents, split_documents, add_to_chroma
from embedding_function import get_embedding_function
import argparse
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
from langchain_core.messages import AIMessage, HumanMessage
from embedding_function import get_embedding_function
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser




app = Flask(__name__)

app.secret_key = "Hii"

@app.route("/")
def login_page(): 
    return render_template("keyword.html")


@app.route("/search", methods = ["GET", "POST"])
def search():
    keyword = request.form["keyword"]  # we need to check its validity
    if download_patent(keyword) :
        documents = load_documents()
        chunks = split_documents(documents)
        add_to_chroma(chunks)
        print("DOCUMENTS ADDED SUCCESSFULLY")
        return redirect(url_for("chatbot"))
    else :
        flash("No Patent found with the corresponding keywords, try again !")
        return render_template("keyword.html")


@app.route("/chatbot")
def chatbot() :
    return render_template("chatbot.html")


# Global store for conversation history (simple in-memory)
store = {}

# Initialize components once (outside routes)
embedding_function = get_embedding_function()  # Make sure this is defined
db = Chroma(persist_directory="./patents_app", embedding_function=embedding_function)
model = Ollama(model="mistral")

@app.route("/get_response", methods=["POST"])
def get_response():
    user_input = request.form["user_input"]
    
    # Hardcoded session ID for simplicity (all users share same history)
    session_id = "default_session"  
    
    # Get bot response
    bot_response = get_chatbot_response(user_input, session_id)
    return jsonify({"response": bot_response})

def get_chatbot_response(input, session_id):
    retriever = db.as_retriever(k=2)
    
    system_template = """
    You are a patent analyzer assistant. Answer engineering questions briefly using:
    - The provided context (most important)
    - Conversation history (secondary)
    - Your knowledge (if no context exists)
    - NB !!! Do not use the context until a relevant question is asked
    
    Context: {context}
    """
    
    prompt_template = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name='history'),
        ("system", system_template),
        ("human", "{question}"),
    ])
    
    chain = (
        {
            "context": RunnablePassthrough() | get_question | retriever | format_docs,
            "question": lambda x: x["question"],
            "history": lambda x: x["history"],
        }
        | prompt_template
        | model
        | StrOutputParser()
    )
    
    chat_with_history = RunnableWithMessageHistory(
        chain,
        get_by_session_id,
        input_messages_key="question",
        history_messages_key="history"
    )
    
    result = chat_with_history.invoke(
        {"question": input},
        config={"configurable": {"session_id": session_id}}
    )
    return result

def get_by_session_id(session_id):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def get_question(input_dict):
    return input_dict["question"]


if __name__ == "__main__" :
    app.run(debug=True)
