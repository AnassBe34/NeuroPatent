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


CHROMA_PATH = "./patents_app"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""



def query_rag():
    # Prepare the DB.
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    print("CHATBOT: Hi! how can I help you ?")
    # Search the DB.
    query_text = input('HUMAN: ')
    #results = db.similarity_search_with_score(query_text, k=2)
    #context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    #prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    #prompt = prompt_template.format(context=context_text, question=query_text)
    #print(prompt)
    prompt = f'USER : {query_text}'
    model = Ollama(model="mistral")
    response_text = model.invoke(prompt)
    #sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"CHATBOT: {response_text}" #\nSources: {sources}"
    print(formatted_response)




store = {}  ## example : {'id151' : 'chatobject'} can be used to store multiple sessions 

def get_by_session_id(session_id):
        if session_id not in store :
            store[session_id] = InMemoryChatMessageHistory()
        return store[session_id]  

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def get_question(input_dict):
        return input_dict["question"]

def deserve_retrieve(question) :
     pass 
    
def chat_with_history() :
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    retriever = db.as_retriever(k = 2)

    system_template = """
    You are a patent analyzer assistant. Answer engineering questions briefly using:
    - The provided context (most important)
    - Conversation history (secondary)
    - Your knowledge (if no context exists)
    - NB !!! Do not use the context until a relevant question is asked
    
    Context: {context}
    """

    human_template = "{question}"
    prompt_template = ChatPromptTemplate.from_messages(
    [
         MessagesPlaceholder(variable_name = 'history'),
        ("system", system_template),
        ("human", human_template),
    ]
    )
    model = Ollama(model="mistral")
    chain  = (
        {
            "context": RunnablePassthrough() | get_question | retriever | format_docs,  # Need to format retrieved documents
            "question": lambda x: x["question"],
            "history": lambda x: x["history"],  # Need to pass through history
        }
        | prompt_template
        | model
        | StrOutputParser()
    )


     ## example : {'id151' : 'chatobject'}
     
    chat_with_history = RunnableWithMessageHistory(
         chain,
         get_by_session_id,
         input_messages_key="question",
         history_messages_key="history"
     )
    
    chain_without_rag = prompt_template | model
    chat_without_rag = RunnableWithMessageHistory(  ## adjust it and remove context from system message
         chain,
         get_by_session_id,
         input_messages_key="question",
         history_messages_key="history"
     )
    
    while True : 
        user_question = input('Human : ')
        result = chat_with_history.invoke(
                {"question": user_question},
        config = {"configurable" : {"session_id" : "boo"}})
        print(f"Chatbot : {result}")


if __name__ == "__main__":
    chat_with_history()