# RAG => 
1. indexing phase => providing the data
2. Retrieval phase => chatting with data


1. Indexing: 

data(a lot) => chunking (spliting data into chunks(smaller pieces)) => embeding model (every chunk is getting passed to embedding model) => vector embeddings (embedding model converts chunks into vectors) => vector db (storing vector embeddings+ into vector dbs) (storing like chunk 1 + vector embeddings + metadata, similarly for all the chunks)
metadata like {page_num, doc} 

means all we have done is to divide whole data into smaller vectors and stored them in a vector db, this all is done in a indexing phase.


2. Retrieval:

User query => converting user query into vector embeddings using embedding model => then searching this vector in vector db which is known as vector similarity search => will get only relevant chunks after vector similarity search => will use chat model and provide this relevant data to chat model in SYSTEM_PROMPT => 
