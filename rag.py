from load_pdfs import download_patent
from initialize_db import load_documents, split_documents, add_to_chroma, name_collection
from embedding_function import get_embedding_function
import argparse
from read_from_db import save_ai_message

from sqlalchemy import create_engine

from langchain_community.vectorstores import Chroma
from langchain_community.llms.ollama import Ollama
from langchain_community.chat_message_histories import SQLChatMessageHistory


from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
import markdown
import re

model = Ollama(model="llama3.1:8b")

def get_chatbot_response(user_input, session_id) :
     combined_prompt = """
            Conversation History:
                {history}

            You are a patent analyzer assistant. Answer the user-question using:
            - The provided context
            - The previous conversation

            Context:
            {context}

            User Question:
            {question}
            """


     prompt_template = PromptTemplate.from_template(combined_prompt)
     embedding_function = get_embedding_function()
     collection_name = name_collection(session_id)
     db = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function, collection_name=collection_name)
     retriever = db.as_retriever(search_type="mmr",
                                search_kwargs={'k': 4, 'fetch_k': 20, 'lambda_mult': 0.5})
     chain = (
        {
             ## the invoke creates a dict with question key
             ## the runnablewithmessagehistory adds the history to this dict
             ## then RunnablePassthrough() just forwards the full input dictionary and then it adds the context ket to out dict 
            "context": RunnablePassthrough() | get_question | retriever | format_docs,
            ## those ones takes our input dict, extracts the question and the history and pass them to the prompt_template...
            "question": lambda x: x["question"],
            "history": lambda x: format_last_n_turns(x["history"]),
        }
        #| RunnableLambda(debug_input)
        | prompt_template
        | model
        | StrOutputParser()
    )
     engine = create_engine("sqlite:///chat_history.db")
     chain_with_history = RunnableWithMessageHistory(
        chain,
        lambda session_id: SQLChatMessageHistory(session_id=session_id, connection=engine),
        input_messages_key="question",
        history_messages_key="history",
    )
     result = chain_with_history.invoke(
            {"question": user_input},
            config={"configurable": {"session_id": session_id}},
        )
     #result = markdown.markdown(result)

     
     context = contexts[-1]
     
     critic_result = critic_agent(user_input,context, result)
     final_response = refiner_agent(user_input,result,critic_result, context)
     

     print("##################### FIRST AGENT RESPONSE ########################")
     print(result)
     print("##################### CRITICS RESPONSE ########################")
     print(critic_result)
     print("##################### REFINER RESPONSE ########################")
     print(final_response)

     save_ai_message(msg = final_response, engine=engine)

     return final_response


def critic_agent(user_input,context,result) : 
    critic_template = """
        You are a critical reasoning agent. Your task is to critique the response of a question-answering agent only based on the user's question and the provided context.

        NOTES:
        - If the context doesn't relate to the question at all: ONLY WRITE THIS SINGLE POINT → "- The context doesn't relate to the question!"
        - Otherwise, list specific critique points starting with a dash (-), focusing on: factual errors, unsupported claims, irrelevant information, or missing insights.
        - The first agent has the history of the conversation of the user, so he might have some informations from there, so don't worry if he brings some informations that are not in the context, like the name of the user for example

        ### USER QUESTION:
        {user_question}

        ### RETRIEVED CONTEXT:
        {context}

        ### AGENT RESPONSE:
        {agent_answer}

        ### CRITIQUE POINTS:
""".strip()
    
    formatted_prompt = critic_template.format(
    user_question=user_input,
    context=context,
    agent_answer=result
)
    critic_result = model.invoke(formatted_prompt)
    return critic_result
    
def refiner_agent(user_input,result,critic_result,context) :
    refiner_template = """
        You are a Refiner Agent. Your role is to improve an existing answer by analyzing:
        - The original user question
        - The initial answer provided by another agent
        - Critical feedback about that answer
        - Additional contextual information

        Your goal is to refine the answer by:
        - Correcting any inaccuracies or gaps pointed out in the critiques
        - Aligning the response better with the user’s intent
        - Ensuring it is concise, coherent, and context-aware

        ### User Question :
        {question}

        ### Initial Answer:
        {initial_response}

        ### Critical Feedback:
        {critics}

        ### Additional Context:
        {context}

        Note: Your answer is given directly to the user so please address directly a refined version of the answer for the user in Markdown Format without any prefixes like bot: or Refined Answer : :
""".strip()
    
    formatted__refiner_prompt = refiner_template.format(
    question=user_input,
    initial_response = result,
    critics = critic_result,
    context=context,
)
    final_response = model.invoke(formatted__refiner_prompt)
    final_response = markdown.markdown(final_response)
    return final_response


def format_last_n_turns(history, n_turns=5):
    # Get last 2 * n_turns messages (Human + AI per turn)
    recent_history = history[-2 * n_turns:]
    formatted = ""
    for msg in recent_history:
        role = "User" if msg.type == "human" else "AI"
        formatted += f"{role}: {msg.content.strip()}\n"
    return formatted.strip()


contexts = list()
def format_docs(docs):
    print("🧠 Context returned by retriever:")
    for i, doc in enumerate(docs):
        print(f"[{i+1}] {doc.page_content}\n")
    contexts.append("\n\n".join(doc.page_content for doc in docs))
    return contexts[-1]

def get_question(input_dict):
    return input_dict["question"]