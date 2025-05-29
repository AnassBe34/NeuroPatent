from sqlalchemy import create_engine, text
import json
import markdown
import os

def load_sessions(engine) :
    with engine.connect() as con :
        result = con.execute(text("SELECT DISTINCT session_id FROM message_store "))
        result_all = result.all()
        sessions = []
        for row in result_all :
            sessions.append(dict(row._mapping))
        list_session = []
        for session in sessions : 
            list_session.append(session['session_id'])
        return list_session
    
def load_conversation(engine, session_id) : 
    with engine.connect() as con :
        result = con.execute(text("SELECT message FROM message_store WHERE session_id = :session_id"), {"session_id": session_id})
        result_all = result.all()
        conv = []
        for row in result_all :
            conv.append(dict(row._mapping))
        messages = []
        for message in conv : 
            messages.append(markdown.markdown(json.loads(message['message'])['data']['content'] ) )
        messages = list(zip(messages[::2], messages[1::2]))
        #print(messages)
        
        return messages
    

def save_ai_message(msg, engine):
    new_value = {
        "type": "ai",
        "data": {
            "content": msg,
            "additional_kwargs": {},
            "response_metadata": {},
            "type": "ai",
            "name": None,
            "id": None,
            "example": False,
            "tool_calls": [],
            "invalid_tool_calls": [],
            "usage_metadata": None
        }
    }
    
    # Convert the dictionary to a JSON string
    json_value = json.dumps(new_value)
    
    with engine.connect() as con:
        result = con.execute(
            text("UPDATE message_store SET message = :new_value WHERE id = (SELECT MAX(id) FROM message_store);"), 
            {"new_value": json_value}
        )
        con.commit()  # Don't forget to commit your changes


def get_patent_id(keyword) : 
    pdf_files = []
    directory_path = 'patents_dataset'
    # Check if the directory exists
    if not os.path.exists(directory_path):
        print(f"Directory '{directory_path}' does not exist.")
        return pdf_files
    
    # Get all files in the directory
    for file in os.listdir(directory_path):
        if keyword in file : 
            id = file.split('_')[0]
            return "Patent No.:" +  id
    return "I'm your friend NeuroPatent, feel inspired ?"


## this function will get you all the patents i have
def get_all_patents_id() : 
    pdf_ids = []
    directory_path = 'patents_dataset'
    
    # Get all files in the directory
    for file in os.listdir(directory_path):
        id = file.split('_')[0]
        pdf_ids.append(id)
    return pdf_ids


def delete_session_from_db(session_id, engine) :
    with engine.connect() as con:
        result = con.execute(
                text("DELETE FROM message_store WHERE session_id = :session_id"), 
                {"session_id": session_id}
            )
        con.commit()






'''
def add_keyword_dataset(keyword, engine) :
    new_msg = {
        "type": "ai",
        "data": {
            "content": None,
            "additional_kwargs": {},
            "response_metadata": {},
            "type": "ai",
            "name": None,
            "id": None,
            "example": False,
            "tool_calls": [],
            "invalid_tool_calls": [],
            "usage_metadata": None
        }
    }
    json_value = json.dumps(new_msg)

    with engine.connect() as con:
        sql_statement = text("INSERT INTO message_store (session_id, message) VALUES (:keyword, :new_msg)")

        con.execute(
            sql_statement,
            {"keyword" : keyword, "new_msg" : json_value}
        )

        con.execute(
            sql_statement,
            {"keyword" : keyword, "new_msg" : json_value}
        )

        con.commit()

'''