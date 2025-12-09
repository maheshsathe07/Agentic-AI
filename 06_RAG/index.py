from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()   

pdf_path = Path(__file__).parent / "nodejs.pdf"

# load this file in python program => use pypdfloader
loader = PyPDFLoader(file_path=pdf_path)
docs = loader.load() # docs contains every single page as a document

#split docs into smaller chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)

chunks = text_splitter.split_documents(documents=docs)

# Vector Embeddings for these chunks
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

# store embeddings to vector database
vector_store = QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embeddings,
    url="http://localhost:6333", # http://localhost:6333/dashboard can check indexing related info
    collection_name="learning_rag"
)

print("indexing completed")