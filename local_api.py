import json
import requests
from bs4 import BeautifulSoup
from unstructured.partition.html import partition_html
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_community.llms import GPT4All
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

import os

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Carregar embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Configurar Chroma
vector_db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

# Configurar modelo local
model_path = "/home/alessandro/Documentos/BotRe/models/mistral-7b-instruct.Q4_K_M.gguf"

llm = GPT4All(model=model_path, verbose=True)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vector_db.as_retriever()
)

class Query(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(query: Query):
    response = qa_chain.run(query.question)
    return {"answer": response}

# Função de raspagem
def scrape_redesign():
    base_url = "https://redesignconsultoria.com.br"
    pages = ["", "/solucoes", "/quem-somos", "/contato"]
    
    all_content = []
    
    for page in pages:
        url = base_url + page
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Erro ao acessar {url}: {response.status_code}")
            continue
        
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

# Salvando dados raspados
data = scrape_redesign()
with open("redesign_content.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False)
