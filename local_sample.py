import requests
from bs4 import BeautifulSoup
from unstructured.partition.html import partition_html

def scrape_redesign():
    base_url = "https://redesignconsultoria.com.br"
    pages = ["", "/solucoes", "/quem-somos", "/contato"]
    
    all_content = []
    
    for page in pages:
        url = base_url + page
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        

        for element in soup(["script", "style", "nav", "footer"]):
            element.decompose()
        
        elements = partition_html(str(soup))
        page_text = "\n".join([str(el) for el in elements])
        all_content.append({
            "url": url,
            "content": page_text
        })
    
    return all_content

import json
data = scrape_redesign()
with open("redesign_content.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False)