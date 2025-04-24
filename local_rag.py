from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
import json


with open("redesign_content.json", "r", encoding="utf-8") as f:
    data = json.load(f)


documents = []
for item in data:
    documents.append({
        "page_content": item["content"],
        "metadata": {"source": item["url"]}
    })


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
texts = text_splitter.split_documents(documents)


embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_db = Chroma.from_documents(
    documents=texts,
    embedding=embeddings,
    persist_directory="./chroma_db"
)
vector_db.persist()