from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from openai import OpenAI

load_dotenv()

openai_client = OpenAI()

# need embeddings to query vector database => needs user_query to covert in vector embedding
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

vector_db = QdrantVectorStore.from_existing_collection(
    embedding=embeddings,
    url="http://localhost:6333",
    collection_name="learning_rag"
)
# take user query
user_query = input("Ask something: ")

# returns relevant chunks from the vector database
search_results = vector_db.similarity_search(user_query)

context = "\n\n\n".join([f"Page Content: {result.page_content}\nPage Number: {result.metadata['page_label']}\nFile Location: {result.metadata['source']}" for result in search_results])

SYSTEM_PROPMT = f"""
   You are a helpful AI assistant who answers user query based on the available context
   retrieved from a PDF file along with page_contents and page number.

   You should only answer the user based on the following context and navigate the user 
   to open the right page number to know more.

   Context: {context}
"""

response = openai_client.chat.completions.create(
    model="gpt-5-nano",
    messages=[
        {"role": "system", "content": SYSTEM_PROPMT},
        {"role": "user", "content": user_query}
    ]
)

print(f"BOT: {response.choices[0].message.content}")