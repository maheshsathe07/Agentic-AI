from mem0 import Memory
from dotenv import load_dotenv
import os
from openai import OpenAI
import json

load_dotenv()

client = OpenAI()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
config = {
    "version":"v1.1",
    "embedder": {
        "provider":"openai",
        "config":{
            "api_key":OPENAI_API_KEY,
            "model":"text-embedding-3-small"
        }
    },
    "llm":{
        "provider":"openai",
        "config":{
            "api_key":OPENAI_API_KEY,
            "model":"gpt-5-nano"
        }
    },
    "vector_store":{
        "provider":"qdrant",
        "config":{
            "host":"localhost",
            "port":6333
        }
    }
}

mem_client = Memory.from_config(config)

while True:
    user_query = input("> ")

    # creating memory layer:
    # need to retrieve from memory to gain the previous history
    search_memory = mem_client.search(query=user_query, user_id="Mahesh") 

    memories = [
        f"ID: {mem.get('id')}\nMemory: {mem.get('memory')}"
        for mem in search_memory.get('results')
    ]

    print("Found memories: ", memories)
    SYSTEM_PROMPT = f"""
        Here is the context about the user:
        {json.dumps(memories)}
    """

    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {"role":"system", "content": SYSTEM_PROMPT},
            {"role":"user", "content":user_query}
        ]
    )

    ai_response = response.choices[0].message.content

    print("BOT: ", ai_response)

    mem_client.add(
        user_id="Mahesh", # unique per user
        messages=[
            {"role":"user", "content":user_query},
            {"role":"assistant", "content": ai_response}
        ]
    )

    print("Memory has been saved!!")