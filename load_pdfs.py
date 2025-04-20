from serpapi import GoogleSearch
import os
import requests



def download_patent(keyword) : 
  params = {
    "engine": "google_patents",
    "q": keyword,
    "api_key": "YOUR_API_HERE",
    "country" : "US",
    "num": 10
    ## specify latest patents !!
  }

  search = GoogleSearch(params)
  results = search.get_dict()
  print(results)
  organic_results = results["organic_results"]

  pdf_links = list()

  for dict in organic_results : 
      try : 
        print(dict['pdf'])
        pdf_links.append(dict['pdf'])
      except :
        print('not found')

  for i in range(len(pdf_links)) : 
    response = requests.get(pdf_links[i])
    if response.status_code == 200:
        with open(f"downloaded_{i}.pdf", "wb") as file:
            file.write(response.content)
        print("Download complete!")
        return True
    else:
        print("Failed to download PDF:", response.status_code)
        return False
 
