from serpapi import GoogleSearch
import os
import requests
import fitz
from langchain_community.llms.ollama import Ollama
from langchain.prompts import PromptTemplate


model = Ollama(model="llama3.1:8b")

def question_to_keywords(question) :
    """Extrait 3 mots-clés techniques depuis une question"""
    prompt = f"""
    Design 3 technical keywords from the question below to perform a well patent research.
    Return only and directly the keywords separated by commas, no line return, without any sentences or explanations.

    Question: {question}

    Keywords:
    """.strip()

    formatted_prompt = prompt.format(question = question)
    raw_response = model.invoke(formatted_prompt)
    return raw_response

# print(question_to_keywords(question ='What are the innovations in solar panel efficiency for residential use?'))

def download_patent(keyword) : 
  params = {
    "engine": "google_patents",
    "q": keyword,
    "api_key": "YOUR SERPAPI API HERE",
    "country" : "US",
    "num": 10,
    ## specify latest patents !!
    "after": "publication:20100101"
  }

  search = GoogleSearch(params)
  results = search.get_dict()
  print(results)
  organic_results = results["organic_results"]

  pdf_links = list()
  patent_ids = list()

  for dict in organic_results : 
      try : 
        print(dict['pdf'])
        patent_ids.append(dict["publication_number"])
        pdf_links.append(dict['pdf'])
      except :
        print('not found')

  for i in range(len(pdf_links)) : 
    response = requests.get(pdf_links[i])
    pdf_path = f"patents_dataset\{patent_ids[i]}_{keyword}.pdf"
    if response.status_code == 200:
        with open(pdf_path, "wb") as file:
            file.write(response.content)
        print("Download complete!")
        split_columns(pdf_path)
        return patent_ids[i]
    else:
        print("Failed to download PDF:", response.status_code)
        return None
 
def split_columns(pdf_path):
    """
    Divise chaque page d'un PDF à deux colonnes en deux pages.
    """
    doc = fitz.open(pdf_path)
    new_doc = fitz.open()

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        rect = page.rect

        left_col = fitz.Rect(rect.x0, rect.y0, rect.width / 2, rect.y1)
        right_col = fitz.Rect(rect.width / 2, rect.y0, rect.x1, rect.y1)

        for col_rect in [left_col, right_col]:
            new_page = new_doc.new_page(width=col_rect.width, height=col_rect.height)
            new_page.show_pdf_page(new_page.rect, doc, page_num, clip=col_rect)
    doc.close()
    new_doc.save(f'clean_patent.pdf')
    #print(f"📄 PDF divisé sauvegardé sous : {output_path}")


#download_patent("vibration")
